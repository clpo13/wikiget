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

import argparse
import logging
import sys
from concurrent.futures import ThreadPoolExecutor

import wikiget
from wikiget.dl import download, prep_download
from wikiget.exceptions import ParseError


def construct_parser():
    parser = argparse.ArgumentParser(
        description="""
        A tool for downloading files from MediaWiki sites using the file name or
        description page URL
        """,
        epilog="""
        Copyright (C) 2018-2023 Cody Logan and contributors. License GPLv3+: GNU GPL
        version 3 or later <http://www.gnu.org/licenses/gpl.html>. This is free
        software; you are free to change and redistribute it under certain conditions.
        There is NO WARRANTY, to the extent permitted by law.
        """,
    )
    parser.add_argument(
        "FILE",
        help="""
        name of the file to download with the File: prefix, or the URL of its file
        description page
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
        "-P",
        "--path",
        default=wikiget.DEFAULT_PATH,
        help="MediaWiki site path, where api.php is located (default: %(default)s)",
    )
    parser.add_argument(
        "-u",
        "--username",
        default="",
        help="MediaWiki site username, for private wikis",
    )
    parser.add_argument(
        "-p",
        "--password",
        default="",
        help="MediaWiki site password, for private wikis",
    )
    output_options = parser.add_mutually_exclusive_group()
    output_options.add_argument("-o", "--output", help="write download to OUTPUT")
    output_options.add_argument(
        "-a",
        "--batch",
        help="treat FILE as a textfile containing multiple files to download, one URL "
        "or filename per line",
        action="store_true",
    )
    parser.add_argument(
        "-l", "--logfile", default="", help="save log output to LOGFILE"
    )
    parser.add_argument(
        "-j",
        "--threads",
        default=1,
        help="number of parallel downloads to attempt in batch mode",
        type=int,
    )

    return parser


def configure_logging(args):
    loglevel = logging.WARNING
    if args.verbose >= wikiget.VERY_VERBOSE:
        # this includes API and library messages
        loglevel = logging.DEBUG
    elif args.verbose >= wikiget.STD_VERBOSE:
        loglevel = logging.INFO
    elif args.quiet:
        loglevel = logging.ERROR

    # configure logging:
    # console log level is set via -v, -vv, and -q options;
    # file log level is always debug (TODO: make this user configurable)
    base_format = "%(threadName)s - %(message)s"
    log_format = "[%(levelname)s] " + base_format
    if args.logfile:
        # log to console and file
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s [%(levelname)-7s] " + base_format,
            filename=args.logfile,
        )

        console = logging.StreamHandler()
        console.setLevel(loglevel)
        console.setFormatter(logging.Formatter(log_format))
        logging.getLogger("").addHandler(console)
    else:
        # log only to console
        logging.basicConfig(level=loglevel, format=log_format)


def batch_download(args):
    input_file = args.FILE
    dl_list = {}

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
    with ThreadPoolExecutor(
        max_workers=args.threads,
        thread_name_prefix="download",
    ) as executor:
        futures = []
        for line_num, line in dl_list.items():
            # keep track of batch file line numbers for debugging/logging purposes
            logging.info(f"Downloading '{line}' at line {line_num}")
            try:
                file = prep_download(line, args)
            except ParseError as e:
                logging.warning(f"{e} (line {line_num})")
            future = executor.submit(download, file, args)
            futures.append(future)
        # wait for downloads to finish
        for future in futures:
            future.result()


def main():
    # setup
    parser = construct_parser()
    args = parser.parse_args()

    configure_logging(args)

    # log events are appended to the file if it already exists, so note the start of a
    # new download session
    logging.info(f"Starting download session using wikiget {wikiget.wikiget_version}")

    if args.batch:
        # batch download mode
        batch_download(args)
    else:
        # single download mode
        try:
            file = prep_download(args.FILE, args)
        except ParseError as e:
            logging.error(e)
            sys.exit(1)
        download(file, args)
