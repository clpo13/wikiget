# wikiget - CLI tool for downloading files from Wikimedia sites
# Copyright (C) 2023 Cody Logan
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
from argparse import Namespace

import wikiget


class FileLogAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return f"[{self.extra['filename']}] {msg}", kwargs


def configure_logging(args: Namespace) -> None:
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
    base_format = "%(message)s"
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
