# wikiget - CLI tool for downloading files from Wikimedia sites
# Copyright (C) 2018-2023 Cody Logan and contributors
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
from concurrent.futures import ThreadPoolExecutor

from mwclient import APIError, InvalidResponse, LoginError, Site
from requests import ConnectionError, HTTPError
from tqdm import tqdm

import wikiget
from wikiget.exceptions import ParseError
from wikiget.file import File
from wikiget.logging import FileLogAdapter
from wikiget.parse import get_dest
from wikiget.validations import verify_hash


def query_api(filename, site_name, args):
    # connect to site and identify ourselves
    logging.info(f"Connecting to {site_name}")
    try:
        site = Site(site_name, path=args.path, clients_useragent=wikiget.USER_AGENT)
        if args.username and args.password:
            site.login(args.username, args.password)
    except ConnectionError as e:
        # usually this means there is no such site, or there's no network connection,
        # though it could be a certificate problem
        logging.error("Could not connect to specified site")
        logging.debug(e)
        raise
    except HTTPError as e:
        # most likely a 403 forbidden or 404 not found error for api.php
        logging.error(
            "Could not find the specified wiki's api.php. Check the value of --path."
        )
        logging.debug(e)
        raise
    except (InvalidResponse, LoginError) as e:
        # InvalidResponse: site exists, but we couldn't communicate with the API
        # endpoint for some reason other than an HTTP error.
        # LoginError: missing or invalid credentials
        logging.error(e)
        raise

    # get info about the target file
    try:
        image = site.images[filename]
    except APIError as e:
        # an API error at this point likely means access is denied, which could happen
        # with a private wiki
        logging.error(
            "Access denied. Try providing credentials with --username and --password."
        )
        for i in e.args:
            logging.debug(i)
        raise

    return image


def prep_download(dl, args):
    file = get_dest(dl, args)
    file.image = query_api(file.name, file.site, args)
    return file


def batch_download(args):
    input_file = args.FILE
    dl_list = {}
    errors = 0

    logging.info(f"Using batch file '{input_file}'.")

    try:
        fd = open(input_file)
    except OSError as e:
        logging.error("File could not be read. The following error was encountered:")
        logging.error(e)
        sys.exit(1)
    else:
        with fd:
            # read the file into memory and process each line as we go
            for line_num, line in enumerate(fd, start=1):
                line_s = line.strip()
                # ignore blank lines and lines starting with "#" (for comments)
                if line_s and not line_s.startswith("#"):
                    dl_list[line_num] = line_s

    # TODO: validate file contents before download process starts
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = []
        for line_num, line in dl_list.items():
            # keep track of batch file line numbers for debugging/logging purposes
            logging.info(f"Processing '{line}' at line {line_num}")
            try:
                file = prep_download(line, args)
            except ParseError as e:
                logging.warning(f"{e} (line {line_num})")
                errors += 1
                continue
            except (ConnectionError, HTTPError, InvalidResponse, LoginError, APIError):
                logging.warning(
                    f"Unable to download '{line}' (line {line_num}) due to an error"
                )
                errors += 1
                continue
            future = executor.submit(download, file, args)
            futures.append(future)
        # wait for downloads to finish
        for future in futures:
            errors += future.result()
    return errors


def download(f, args):
    file = f.image
    filename = f.name
    dest = f.dest
    site = file.site

    errors = 0

    logger = logging.getLogger("")
    adapter = FileLogAdapter(logger, {"filename": filename})

    if file.exists:
        # file exists either locally or at a common repository, like Wikimedia Commons
        file_url = file.imageinfo["url"]
        file_size = file.imageinfo["size"]
        file_sha1 = file.imageinfo["sha1"]

        filename_log = f"Downloading '{filename}' ({file_size} bytes) from {site.host}"
        if args.output:
            filename_log += f" to '{dest}'"
        adapter.info(filename_log)
        adapter.info(f"{file_url}")

        if os.path.isfile(dest) and not args.force:
            adapter.warning("File already exists, skipping download (use -f to force)")
            errors += 1
        else:
            try:
                fd = open(dest, "wb")
            except OSError as e:
                adapter.error(f"File could not be written. {e}")
                errors += 1
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

            # verify file integrity and log details
            dl_sha1 = verify_hash(dest)

            adapter.info(f"Remote file SHA1 is {file_sha1}")
            adapter.info(f"Local file SHA1 is {dl_sha1}")
            if dl_sha1 == file_sha1:
                adapter.info("Hashes match!")
                # at this point, we've successfully downloaded the file
                success_log = f"'{filename}' downloaded"
                if args.output:
                    success_log += f" to '{dest}'"
                adapter.info(success_log)
            else:
                adapter.error("Hash mismatch! Downloaded file may be corrupt.")
                errors += 1

    else:
        # no file information returned
        adapter.warning("Target does not appear to be a valid file")
        errors += 1

    return errors
