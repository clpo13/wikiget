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

import fileinput
import logging
from argparse import Namespace
from typing import Dict
from urllib.parse import unquote, urlparse

import wikiget
from wikiget.exceptions import ParseError
from wikiget.file import File
from wikiget.validations import valid_file

logger = logging.getLogger(__name__)


def get_dest(dl: str, args: Namespace) -> File:
    url = urlparse(dl)

    if url.netloc:
        filename = url.path
        site_name = url.netloc
        if args.site is not wikiget.DEFAULT_SITE:
            # this will work even if the user specifies 'commons.wikimedia.org' since
            # we're comparing objects instead of values ('is not' vs. '!=')
            logger.warning("Target is a URL; ignoring site specified with --site")
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
        msg = f"Could not parse input '{dl}' as a file"
        raise ParseError(msg)

    filename = unquote(filename)  # remove URL encoding for special characters
    dest = args.output or filename
    return File(filename, dest, site_name)


def read_batch_file(batch_file: str) -> Dict[int, str]:
    dl_list = {}

    if batch_file == "-":
        logger.info("Using stdin for batch download")
    else:
        logger.info(f"Using file '{batch_file}' for batch download")

    with fileinput.input(batch_file) as fd:
        # read the file into memory and process each line as we go
        for line_num, line in enumerate(fd, start=1):
            line_s = line.strip()
            # ignore blank lines and lines starting with "#" (for comments)
            if line_s and not line_s.startswith("#"):
                dl_list[line_num] = line_s

    return dl_list
