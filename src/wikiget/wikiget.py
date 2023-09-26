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

import argparse
import logging
import sys

import wikiget
from wikiget.dl import download


def main():
    """
    Main entry point for console script. Automatically compiled by setuptools
    when installed with `pip install` or `python setup.py install`.
    """

    parser = argparse.ArgumentParser(
        description="""
        A tool for downloading files from
        MediaWiki sites using the file name or
        description page URL
        """,
        epilog="""
        Copyright (C) 2018-2023 Cody Logan
        and contributors.
        License GPLv3+: GNU GPL version 3 or later
        <http://www.gnu.org/licenses/gpl.html>.
        This is free software; you are free to
        change and redistribute it under certain
        conditions. There is NO WARRANTY, to the
        extent permitted by law.
        """,
    )
    parser.add_argument(
        "FILE",
        help="""
        name of the file to download with the File:
        prefix, or the URL of its file description page
        """,
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {wikiget.wikiget_version}",
    )
    message_options = parser.add_mutually_exclusive_group()
    message_options.add_argument(
        "-q", "--quiet", help="suppress warning messages", action="store_true"
    )
    message_options.add_argument(
        "-v",
        "--verbose",
        help="print detailed information; use -vv for even more detail",
        action="count",
        default=0,
    )
    parser.add_argument(
        "-f", "--force", help="force overwriting existing files", action="store_true"
    )
    parser.add_argument(
        "-s",
        "--site",
        default=wikiget.DEFAULT_SITE,
        help="MediaWiki site to download from (default: %(default)s)",
    )
    parser.add_argument(
        "-p",
        "--path",
        default=wikiget.DEFAULT_PATH,
        help="MediaWiki site path, where api.php is located (default: %(default)s)",
    )
    parser.add_argument(
        "--username", default="", help="MediaWiki site username, for private wikis"
    )
    parser.add_argument(
        "--password", default="", help="MediaWiki site password, for private wikis"
    )
    output_options = parser.add_mutually_exclusive_group()
    output_options.add_argument("-o", "--output", help="write download to OUTPUT")
    output_options.add_argument(
        "-a",
        "--batch",
        help="treat FILE as a textfile containing "
        "multiple files to download, one URL or "
        "filename per line",
        action="store_true",
    )
    parser.add_argument(
        "-l", "--logfile", default="", help="save log output to LOGFILE"
    )

    args = parser.parse_args()

    loglevel = logging.WARNING
    if args.verbose >= wikiget.VERY_VERBOSE:
        # this includes API and library messages
        loglevel = logging.DEBUG
    elif args.verbose >= wikiget.STD_VERBOSE:
        loglevel = logging.INFO
    elif args.quiet:
        loglevel = logging.ERROR

    # configure logging:
    # console log level is set via -v, -vv, and -q options
    # file log level is always info (TODO: add debug option)
    if args.logfile:
        # log to console and file
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s [%(levelname)-7s] %(message)s",
            filename=args.logfile,
        )

        console = logging.StreamHandler()
        # TODO: even when loglevel is set to logging.DEBUG,
        # debug messages aren't printing to console
        console.setLevel(loglevel)
        console.setFormatter(logging.Formatter("[%(levelname)s] %(message)s"))
        logging.getLogger("").addHandler(console)
    else:
        # log only to console
        logging.basicConfig(level=loglevel, format="[%(levelname)s] %(message)s")

    # log events are appended to the file if it already exists,
    # so note the start of a new download session
    logging.info(f"Starting download session using wikiget {wikiget.wikiget_version}")
    # logging.info(f"Log level is set to {loglevel}")

    if args.batch:
        # batch download mode
        input_file = args.FILE
        dl_list = []

        logging.info(f"Using batch file '{input_file}'.")

        try:
            fd = open(input_file)
        except OSError as e:
            logging.error(
                "File could not be read. The following error was encountered:"
            )
            logging.error(e)
            sys.exit(1)
        else:
            with fd:
                # store file contents in memory in case something
                # happens to the file while we're downloading
                for _, line in enumerate(fd):
                    dl_list.append(line)

        # TODO: validate file contents before download process starts
        for line_num, url in enumerate(dl_list, start=1):
            s_url = url.strip()
            # keep track of batch file line numbers for
            # debugging/logging purposes
            logging.info(f"Downloading '{s_url}' at line {line_num}:")
            download(s_url, args)
    else:
        # single download mode
        dl = args.FILE
        download(dl, args)
