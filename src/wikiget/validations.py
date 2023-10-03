# wikiget - CLI tool for downloading files from Wikimedia sites
# Copyright (C) 2018-2020 Cody Logan
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

import hashlib
import re

from wikiget import BLOCKSIZE


def valid_file(search_string):
    """
    Determines if the given string contains a valid file name, defined as a
    string ending with a '.' and at least one character, beginning with 'File:'
    or 'Image:', the standard file prefixes in MediaWiki.
    :param search_string: string to validate
    :returns: a regex Match object if there's a match or None otherwise
    """
    # second group could also restrict to file extensions with three or more
    # letters with ([^/\r\n\t\f\v]+\.\w{3,})
    file_regex = re.compile(r"(File:|Image:)([^/\r\n\t\f\v]+\.\w+)$", re.I)
    return file_regex.search(search_string)


def valid_site(search_string):
    """
    Determines if the given string contains a valid site name, defined as a
    string ending with 'wikipedia.org' or 'wikimedia.org'. This covers all
    subdomains of those domains. Eventually, it should be possible to support
    any MediaWiki site, regardless of domain name.
    :param search_string: string to validate
    :returns: a regex Match object if there's a match or None otherwise
    """
    site_regex = re.compile(r"wiki[mp]edia\.org$", re.I)
    return site_regex.search(search_string)


def verify_hash(filename):
    """
    Calculates the SHA1 hash of the given file for comparison with a known
    value.
    :param filename: name of the file to calculate a hash for
    :return: hash digest
    """
    hasher = hashlib.sha1()  # noqa: S324
    with open(filename, "rb") as dl:
        buf = dl.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = dl.read(BLOCKSIZE)
    return hasher.hexdigest()
