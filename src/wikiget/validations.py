# wikiget - CLI tool for downloading files from Wikimedia sites
# Copyright (C) 2018-2023 Cody Logan
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

from __future__ import annotations

import hashlib
import re
from typing import TYPE_CHECKING

from wikiget import BLOCKSIZE

if TYPE_CHECKING:
    from pathlib import Path


def valid_file(search_string: str) -> re.Match | None:
    """Determine if the given string contains a valid file name.

    A valid file name is a string that begins with 'File:' or 'Image:' (the standard
    file prefixes in MediaWiki), includes a period, and has at least one character
    following the period, like 'File:Example.jpg' or 'Image:Example.svg'.

    :param search_string: string to validate
    :type search_string: str
    :returns: a regex Match object if there's a match or None otherwise
    :rtype: re.Match
    """
    # second group could also restrict to file extensions with three or more
    # letters with ([^/\r\n\t\f\v]+\.\w{3,})
    file_regex = re.compile(r"(File:|Image:)([^/\r\n\t\f\v]+\.\w+)$", re.I)
    return file_regex.search(search_string)


def valid_site(search_string: str) -> re.Match | None:
    """Determine if the given string contains a valid site name.

    A valid site name is a string ending with 'wikipedia.org' or 'wikimedia.org'. This
    covers all subdomains of those domains.

    Currently unused since any site is accepted as input, and we rely on the user to
    ensure the site has a compatible API.

    :param search_string: string to validate
    :type search_string: str
    :returns: a regex Match object if there's a match or None otherwise
    :rtype: re.Match
    """
    site_regex = re.compile(r"wiki[mp]edia\.org$", re.I)
    return site_regex.search(search_string)


def verify_hash(file: Path) -> str:
    """Calculate the SHA1 hash of the given file for comparison with a known value.

    Despite being insecure, SHA1 is used since that's what the MediaWiki API returns for
    the file hash.

    :param filename: name of the file to calculate a hash for
    :type filename: str
    :return: hash digest
    :rtype: str
    """
    hasher = hashlib.sha1()  # noqa: S324
    with file.open("rb") as dl:
        buf = dl.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = dl.read(BLOCKSIZE)
    return hasher.hexdigest()
