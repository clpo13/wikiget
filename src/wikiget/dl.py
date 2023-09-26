# wikiget - CLI tool for downloading files from Wikimedia sites
# Copyright (C) 2018-2021 Cody Logan and contributors
# SPDX-License-Identifier: GPL-3.0-or-later
#
# Wikiget is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Wikiget is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Wikiget. If not, see <https://www.gnu.org/licenses/>.

import logging
import os
import sys
from urllib.parse import unquote, urlparse

from mwclient import APIError, InvalidResponse, LoginError, Site
from requests import ConnectionError, HTTPError
from tqdm import tqdm

import wikiget
from wikiget.validations import valid_file, verify_hash


def download(dl, args):
    url = urlparse(dl)

    if url.netloc:
        filename = url.path
        site_name = url.netloc
        if args.site is not wikiget.DEFAULT_SITE:
            # this will work even if the user specifies 'commons.wikimedia.org'
            logging.warning("target is a URL, ignoring site specified with --site")
    else:
        filename = dl
        site_name = args.site

    file_match = valid_file(filename)

    # check if this is a valid file
    if file_match and file_match.group(1):
        # has File:/Image: prefix and extension
        filename = file_match.group(2)
    else:
        # no file extension and/or prefix, probably an article
        logging.error(f"Could not parse input '{filename}' as a file.")
        sys.exit(1)

    filename = unquote(filename)  # remove URL encoding for special characters

    dest = args.output or filename

    logging.debug(f"User agent: {wikiget.USER_AGENT}")

    # connect to site and identify ourselves
    logging.info(f"Site name: {site_name}")
    try:
        site = Site(site_name, path=args.path, clients_useragent=wikiget.USER_AGENT)
        if args.username and args.password:
            site.login(args.username, args.password)
    except ConnectionError as e:
        # usually this means there is no such site, or there's no network
        # connection, though it could be a certificate problem
        logging.error("Couldn't connect to specified site.")
        logging.debug("Full error message:")
        logging.debug(e)
        sys.exit(1)
    except HTTPError as e:
        # most likely a 403 forbidden or 404 not found error for api.php
        logging.error(
            "Couldn't find the specified wiki's api.php. Check the value of --path."
        )
        logging.debug("Full error message:")
        logging.debug(e)
        sys.exit(1)
    except (InvalidResponse, LoginError) as e:
        # InvalidResponse: site exists, but we couldn't communicate with the
        # API endpoint for some reason other than an HTTP error.
        # LoginError: missing or invalid credentials
        logging.error(e)
        sys.exit(1)

    # get info about the target file
    try:
        file = site.images[filename]
    except APIError as e:
        # an API error at this point likely means access is denied,
        # which could happen with a private wiki
        logging.error(
            "Access denied. Try providing credentials with "
            "--username and --password."
        )
        logging.debug("Full error message:")
        for i in e.args:
            logging.debug(i)
        sys.exit(1)

    if file.imageinfo != {}:
        # file exists either locally or at a common repository,
        # like Wikimedia Commons
        file_url = file.imageinfo["url"]
        file_size = file.imageinfo["size"]
        file_sha1 = file.imageinfo["sha1"]

        filename_log = f"Downloading '{filename}' ({file_size} bytes) from {site.host}"
        if args.output:
            filename_log += f" to '{dest}'"
        logging.info(filename_log)
        logging.info(f"{file_url}")

        if os.path.isfile(dest) and not args.force:
            logging.warning(
                f"File '{dest}' already exists, skipping download (use -f to ignore)"
            )
        else:
            try:
                fd = open(dest, "wb")
            except OSError as e:
                logging.error(
                    "File could not be written. The following error was encountered:"
                )
                logging.error(e)
                sys.exit(1)
            else:
                # download the file(s)
                if args.verbose >= wikiget.STD_VERBOSE:
                    leave_bars = True
                else:
                    leave_bars = False
                with tqdm(
                    leave=leave_bars,
                    total=file_size,
                    unit="B",
                    unit_scale=True,
                    unit_divisor=wikiget.CHUNKSIZE,
                ) as progress_bar:
                    with fd:
                        res = site.connection.get(file_url, stream=True)
                        progress_bar.set_postfix(file=dest, refresh=False)
                        for chunk in res.iter_content(wikiget.CHUNKSIZE):
                            fd.write(chunk)
                            progress_bar.update(len(chunk))

            # verify file integrity and optionally print details
            dl_sha1 = verify_hash(dest)

            logging.info(f"Downloaded file SHA1 is {dl_sha1}")
            logging.info(f"Server file SHA1 is {file_sha1}")
            if dl_sha1 == file_sha1:
                logging.info("Hashes match!")
                # at this point, we've successfully downloaded the file
            else:
                logging.error("Hash mismatch! Downloaded file may be corrupt.")
                sys.exit(1)

    else:
        # no file information returned
        logging.error(f"Target '{filename}' does not appear to be a valid file.")
        sys.exit(1)