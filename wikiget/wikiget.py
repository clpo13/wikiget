"""wikiget2
Simple wget clone for downloading files from Wikimedia sites.
Copyright (C) 2018 Cody Logan; licensed GPLv3+
SPDX-License-Identifier: GPL-3.0-or-later
"""

from __future__ import absolute_import, division, print_function, unicode_literals

from builtins import open

from future import standard_library

standard_library.install_aliases()

import argparse
import logging
import os
import re
import sys
from urllib.parse import urlparse

from mwclient import InvalidResponse, Site, __ver__ as mwclient_version
from requests import ConnectionError
from tqdm import tqdm

from wikiget.version import __version__


def main():
    """
    Main entry point for console script. Automatically compiled by setuptools.
    """
    default_site = "en.wikipedia.org"
    site_regex = re.compile(r"wiki[mp]edia\.org$", re.I)
    file_regex = re.compile(r"([Ff]ile:|[Ii]mage:)([^/\s]+\.\w+)$")
    user_agent = "wikiget/{} (https://github.com/clpo13/wikiget) " \
                 "mwclient/{}".format(__version__, mwclient_version)

    parser = argparse.ArgumentParser(description="""
                                     A tool for downloading files from MediaWiki sites
                                     using the file name or description page URL
                                     """,
                                     epilog="""
                                     Copyright (C) 2018 Cody Logan. License GPLv3+: GNU GPL version 3
                                     or later <http://www.gnu.org/licenses/gpl.html>.
                                     This is free software; you are free to change and redistribute it.
                                     There is NO WARRANTY, to the extent permitted by law.
                                     """)
    parser.add_argument("FILE", help="""
                        name of the file to download with the File: or Image: prefix,
                        or the URL of its file description page
                        """)
    parser.add_argument("-V", "--version", action="version",
                        version="%(prog)s {}".format(__version__))
    output_options = parser.add_mutually_exclusive_group()
    output_options.add_argument("-q", "--quiet", help="suppress warning messages",
                                action="store_true")
    output_options.add_argument("-v", "--verbose",
                                help="print detailed information, use -vv for even more detail",
                                action="count", default=0)
    parser.add_argument("-f", "--force", help="force overwriting existing files",
                        action="store_true")
    parser.add_argument("-s", "--site", default=default_site,
                        help="MediaWiki site to download from (default: %(default)s)")
    parser.add_argument("-o", "--output", help="write download to OUTPUT")
    args = parser.parse_args()

    # print API and debug messages in verbose mode
    if args.verbose >= 2:
        logging.basicConfig(level=logging.DEBUG)
    elif args.verbose >= 1:
        logging.basicConfig(level=logging.WARNING)

    url = urlparse(args.FILE)

    if url.netloc:
        filename = url.path
        site_name = url.netloc
        if args.site is not default_site and not args.quiet:
            print("Warning: target is a URL, ignoring site specified with --site")
    else:
        filename = args.FILE
        site_name = args.site

    file_match = file_regex.search(filename)
    site_match = site_regex.search(site_name)

    # check for valid site parameter
    if not site_match:
        print("Only Wikimedia sites (wikipedia.org and wikimedia.org) are currently supported.")
        sys.exit(1)

    # check if this is a valid file
    if file_match:
        # get file name without File:/Image: prefix (second match group)
        filename = file_match.group(2)
    else:
        # no file extension or prefix, probably an article
        print("Downloading Wikipedia articles is not currently supported. "
              "If this is a file, please add the 'File:' prefix.")
        sys.exit(1)

    dest = args.output or filename

    if args.verbose >= 2:
        print("User agent: {}".format(user_agent))

    # connect to site and identify ourselves
    try:
        site = Site(site_name, clients_useragent=user_agent)
    except ConnectionError:
        # usually this means there is no such site, or there's no network connection
        print("Error: couldn't connect to specified site.")
        sys.exit(1)
    except InvalidResponse as e:
        # site exists, but we couldn't communicate with the API endpoint
        print(e)
        sys.exit(1)

    # get info about the target file
    file = site.images[filename]

    if file.imageinfo != {}:
        # file exists either locally or at Wikimedia Commons
        file_url = file.imageinfo["url"]
        file_size = file.imageinfo["size"]

        if args.verbose >= 1:
            print("Info: downloading '{}' "
                  "({} bytes) from {}".format(filename, file_size, site.host), end="")
            if args.output:
                print(" to '{}'".format(dest))
            else:
                print("\n", end="")
            print("Info: {}".format(file_url))

        if os.path.isfile(dest) and not args.force:
            print("File '{}' already exists, skipping download (use -f to ignore)".format(dest))
        else:
            try:
                # download the file
                with tqdm(total=file_size, unit="B",
                          unit_scale=True, unit_divisor=1024) as progress_bar:
                    with open(dest, "wb") as fd:
                        res = site.connection.get(file_url, stream=True)
                        progress_bar.set_postfix(file=dest, refresh=False)
                        for chunk in res.iter_content(1024):
                            fd.write(chunk)
                            progress_bar.update(len(chunk))
            except IOError as e:
                print("File could not be written. The following error was encountered:")
                print(e)
                sys.exit(1)
    else:
        # no file information returned
        print("Target does not appear to be a valid file.")
        sys.exit(1)
