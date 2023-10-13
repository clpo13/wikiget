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
from urllib.parse import unquote, urlparse

import wikiget
from wikiget.exceptions import ParseError
from wikiget.validations import valid_file


def get_dest(dl, args):
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
        msg = f"Could not parse input '{filename}' as a file"
        raise ParseError(msg)

    filename = unquote(filename)  # remove URL encoding for special characters

    dest = args.output or filename

    return filename, dest, site_name
