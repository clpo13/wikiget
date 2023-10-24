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

import wikiget


class FileLogAdapter(logging.LoggerAdapter):
    def process(self, msg, kwargs):
        return f"[{self.extra['filename']}] {msg}", kwargs


def configure_logging(verbosity: int, logfile: str, *, quiet: bool) -> None:
    loglevel = logging.WARNING
    if verbosity >= wikiget.VERY_VERBOSE:
        # this includes API and library messages
        loglevel = logging.DEBUG
    elif verbosity >= wikiget.STD_VERBOSE:
        loglevel = logging.INFO
    elif quiet:
        loglevel = logging.ERROR

    # configure logging:
    # console log level is set via -v, -vv, and -q options;
    # file log level is always debug (TODO: make this user configurable)
    console_log_format = "[%(levelname)s] %(message)s"
    file_log_format = "%(asctime)s [%(levelname)-7s] %(message)s"

    logger = logging.getLogger("")  # root logger

    # set up console logging
    ch = logging.StreamHandler()
    ch.setLevel(loglevel)
    ch.setFormatter(logging.Formatter(console_log_format))
    logger.addHandler(ch)

    if logfile:
        # also log to file
        fh = logging.FileHandler(logfile)
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(file_log_format))
        logger.addHandler(fh)
