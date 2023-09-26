# -*- coding: utf-8 -*-
# wikiget - CLI tool for downloading files from Wikimedia sites
# Copyright (C) 2018-2021 Cody Logan
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

from wikiget.validations import valid_file, valid_site, verify_hash


def test_invalid_site_input():
    """
    Invalid site strings should not return regex match objects.
    """
    invalid_input = ["example.com", "vim.wikia.com",
                     "en.wikipedia.com", "en.wikimpedia.org"]
    for i in invalid_input:
        site_match = valid_site(i)
        assert site_match is None


def test_valid_site_input():
    """
    Valid site strings should return regex match objects.
    """
    valid_input = ["en.wikipedia.org", "commons.wikimedia.org",
                   "de.wikipedia.org", "meta.wikimedia.org"]
    for i in valid_input:
        site_match = valid_site(i)
        assert site_match is not None


def test_file_regex():
    """
    File regex should return a match object with match groups corresponding
    to the file prefix and name.
    """
    i = "File:Example.jpg"
    file_match = valid_file(i)
    assert file_match is not None
    assert file_match.group(0) == "File:Example.jpg"  # entire match
    assert file_match.group(1) == "File:"             # first group
    assert file_match.group(2) == "Example.jpg"       # second group


def test_invalid_file_input():
    """
    Invalid file strings should not return regex match objects.
    """
    invalid_input = ["file:example", "example.jpg", "Foo Bar.gif",
                     "Fil:Example.jpg"]
    for i in invalid_input:
        file_match = valid_file(i)
        assert file_match is None


def test_valid_file_input():
    """
    Valid file strings should return regex match objects.
    """
    valid_input = ["Image:example.jpg", "file:example.jpg",
                   "File:example.file-01.jpg", "FILE:FOO.BMP",
                   "File:ß handwritten sample.gif", "File:A (1).jpeg"]
    for i in valid_input:
        file_match = valid_file(i)
        assert file_match is not None


def test_verify_hash(tmp_path):
    """
    Confirm that verify_hash returns the proper SHA1 hash.
    """
    file_name = "testfile"
    file_contents = "foobar"
    file_sha1 = "8843d7f92416211de9ebb963ff4ce28125932878"

    tmp_file = tmp_path / file_name
    tmp_file.write_text(file_contents)

    assert verify_hash(tmp_file) == file_sha1
