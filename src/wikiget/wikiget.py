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
from typing import List

import wikiget
from wikiget.dl import process_download
from wikiget.logging import configure_logging

logger = logging.getLogger(__name__)


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="""
        A tool for downloading files from MediaWiki sites using the file name or
        description page URL.
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
        name of the file to download, with the File: prefix, or the URL of its file
        description page
        """,
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {wikiget.__version__}",
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
    parser.add_argument(
        "-n",
        "--dry-run",
        help="check the download or batch file without actually downloading anything",
        action="store_true",
    )

    return parser.parse_args(argv)


def cli() -> None:
    # setup our environment
    args = parse_args(sys.argv[1:])
    configure_logging(verbosity=args.verbose, logfile=args.logfile, quiet=args.quiet)

    # log events are appended to the file if it already exists, so note the start of a
    # new download session
    logger.info(f"Starting download session using wikiget {wikiget.__version__}")
    logger.debug(f"User agent: {wikiget.USER_AGENT}")

    exit_code = process_download(args)
    sys.exit(exit_code)
