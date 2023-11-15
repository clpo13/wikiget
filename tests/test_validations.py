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

"""Define tests related to the wikiget.validations module."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from wikiget.validations import valid_file, valid_site, verify_hash

if TYPE_CHECKING:
    from pathlib import Path
    from re import Match


class TestSiteInput:
    """Define tests related to wikiget.validations.valid_site."""

    @pytest.fixture(
        params=[
            "example.com",
            "vim.wikia.com",
            "en.wikipedia.com",
            "en.wikimpedia.org",
        ],
    )
    def invalid_input(self, request: pytest.FixtureRequest) -> Match | None:
        """Return the results of checking various invalid site names.

        :param request: Pytest request object containing parameter values
        :type request: pytest.FixtureRequest
        :return: a Match object for the site or None if there was no match
        :rtype: Match | None
        """
        return valid_site(request.param)

    @pytest.fixture(
        params=[
            "en.wikipedia.org",
            "commons.wikimedia.org",
            "de.wikipedia.org",
            "meta.wikimedia.org",
        ],
    )
    def valid_input(self, request: pytest.FixtureRequest) -> Match | None:
        """Return the results of checking various valid site names.

        :param request: Pytest request object containing parameter values
        :type request: pytest.FixtureRequest
        :return: a Match object for the site or None if there was no match
        :rtype: Match | None
        """
        return valid_site(request.param)

    def test_invalid_site_input(self, invalid_input: None) -> None:
        """Invalid site strings should not return regex match objects."""
        assert invalid_input is None

    def test_valid_site_input(self, valid_input: Match) -> None:
        """Valid site strings should return regex match objects."""
        assert valid_input is not None


class TestFileRegex:
    """Define tests related to the regex matching in wikiget.validations.valid_file."""

    @pytest.fixture()
    def file_match(self) -> Match | None:
        """Return the results of processing a filename.

        The match object returned will have match groups corresponding to the file
        prefix and name.

        :return: a Match object for the filename or None if there was no match
        :rtype: Match | None
        """
        return valid_file("File:Example.jpg")

    def test_file_match_exists(self, file_match: Match) -> None:
        """Test that a Match object was returned."""
        assert file_match is not None

    def test_file_match_entire_match(self, file_match: Match) -> None:
        """Test that the the first match group equals the expected value."""
        assert file_match.group(0) == "File:Example.jpg"

    def test_file_match_first_group(self, file_match: Match) -> None:
        """Test that the second match group equals the expected value."""
        assert file_match.group(1) == "File:"

    def test_file_match_second_group(self, file_match: Match) -> None:
        """Test that the third match group equals the expected value."""
        assert file_match.group(2) == "Example.jpg"


class TestFileInput:
    """Tests related to wikiget.validations.valid_site."""

    @pytest.fixture(
        params=[
            "file:example",
            "example.jpg",
            "Foo Bar.gif",
            "Fil:Example.jpg",
        ],
    )
    def invalid_input(self, request: pytest.FixtureRequest) -> Match | None:
        """Return the results of checking various invalid filenames.

        :param request: Pytest request object containing parameter values
        :type request: pytest.FixtureRequest
        :return: a Match object for the filename or None if there was no match
        :rtype: Match | None
        """
        return valid_file(request.param)

    @pytest.fixture(
        params=[
            "Image:example.jpg",
            "file:example.jpg",
            "File:example.file-01.jpg",
            "FILE:FOO.BMP",
            "File:ß handwritten sample.gif",
            "File:A (1).jpeg",
        ],
    )
    def valid_input(self, request: pytest.FixtureRequest) -> Match | None:
        """Return the results of checking various valid filenames.

        :param request: Pytest request object containing parameter values
        :type request: pytest.FixtureRequest
        :return: a Match object for the filename or None if there was no match
        :rtype: Match | None
        """
        return valid_file(request.param)

    def test_invalid_file_input(self, invalid_input: None) -> None:
        """Invalid file strings should not return regex match objects."""
        assert invalid_input is None

    def test_valid_file_input(self, valid_input: Match) -> None:
        """Valid file strings should return regex match objects."""
        assert valid_input is not None


class TestVerifyHash:
    """Define tests related to wikiget.validations.verify_hash."""

    def test_verify_hash(self, test_file: Path) -> None:
        """Confirm that verify_hash returns the proper SHA1 hash.

        The test file used here is generated by a fixture in conftest.py.
        """
        expected_sha1 = "cd19c009a30ca9b68045415a3a0838e64f3c2443"

        assert verify_hash(str(test_file)) == expected_sha1
