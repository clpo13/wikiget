# wikiget - CLI tool for downloading files from Wikimedia sites
# Copyright (C) 2018, 2019, 2020 Cody Logan and contributors
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

from . import DEFAULT_SITE, DEFAULT_PATH, __version__
from .dl import download


def main():
    """
    Main entry point for console script. Automatically compiled by setuptools
    when installed with `pip install` or `python setup.py install`.
    """

    parser = argparse.ArgumentParser(description="""
                                     A tool for downloading files from
                                     MediaWiki sites using the file name or
                                     description page URL
                                     """,
                                     epilog="""
                                     Copyright (C) 2018, 2019, 2020 Cody Logan
                                     and contributors.
                                     License GPLv3+: GNU GPL version 3 or later
                                     <http://www.gnu.org/licenses/gpl.html>.
                                     This is free software; you are free to
                                     change and redistribute it under certain
                                     conditions. There is NO WARRANTY, to the
                                     extent permitted by law.
                                     """)
    parser.add_argument('FILE', help="""
                        name of the file to download with the File: or Image:
                        prefix, or the URL of its file description page
                        """)
    parser.add_argument('-V', '--version', action='version',
                        version='%(prog)s {}'.format(__version__))
    message_options = parser.add_mutually_exclusive_group()
    message_options.add_argument('-q', '--quiet',
                                 help='suppress warning messages',
                                 action='store_true')
    message_options.add_argument('-v', '--verbose',
                                 help='print detailed information; '
                                 'use -vv for even more detail',
                                 action='count', default=0)
    parser.add_argument('-f', '--force',
                        help='force overwriting existing files',
                        action='store_true')
    parser.add_argument('-s', '--site', default=DEFAULT_SITE,
                        help='MediaWiki site to download from '
                        '(default: %(default)s)')
    parser.add_argument('-p', '--path', default=DEFAULT_PATH,
                        help='MediaWiki site path to download from '
                        '(default: %(default)s)')
    parser.add_argument('--username', default="",
                        help='MediaWiki site username '
                        '(default: %(default)s)')
    parser.add_argument('--password', default="",
                        help='MediaWiki site password '
                        '(default: %(default)s)')
    output_options = parser.add_mutually_exclusive_group()
    output_options.add_argument('-o', '--output',
                                help='write download to OUTPUT')
    output_options.add_argument('-a', '--batch',
                                help='treat FILE as a textfile containing '
                                'multiple files to download, one URL or '
                                'filename per line', action='store_true')

    args = parser.parse_args()

    # print API and debug messages in verbose mode
    if args.verbose >= 2:
        logging.basicConfig(level=logging.DEBUG)
    elif args.verbose >= 1:
        logging.basicConfig(level=logging.WARNING)

    if args.batch:
        # batch download mode
        input_file = args.FILE
        if args.verbose >= 1:
            print("Info: using batch file '{}'".format(input_file))
        try:
            fd = open(input_file, 'r')
        except IOError as e:
            print('File could not be read. '
                  'The following error was encountered:')
            print(e)
            sys.exit(1)
        else:
            with fd:
                for _, line in enumerate(fd):
                    line = line.strip()
                    download(line, args)
    else:
        # single download mode
        dl = args.FILE
        download(dl, args)
