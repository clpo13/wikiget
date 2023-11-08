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

from typing import TYPE_CHECKING

import pytest

from wikiget.validations import valid_file, valid_site, verify_hash

if TYPE_CHECKING:
    from pathlib import Path
    from re import Match


class TestSiteInput:
    @pytest.fixture(
        params=[
            "example.com",
            "vim.wikia.com",
            "en.wikipedia.com",
            "en.wikimpedia.org",
        ],
    )
    def invalid_input(self, request: pytest.FixtureRequest) -> Match | None:
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
        return valid_site(request.param)

    def test_invalid_site_input(self, invalid_input: None) -> None:
        """Invalid site strings should not return regex match objects."""
        assert invalid_input is None

    def test_valid_site_input(self, valid_input: Match) -> None:
        """Valid site strings should return regex match objects."""
        assert valid_input is not None


class TestFileRegex:
    @pytest.fixture()
    def file_match(self) -> Match | None:
        """
        File regex should return a match object with match groups corresponding
        to the file prefix and name.
        """
        return valid_file("File:Example.jpg")

    def test_file_match_exists(self, file_match: Match) -> None:
        assert file_match is not None

    def test_file_match_entire_match(self, file_match: Match) -> None:
        assert file_match.group(0) == "File:Example.jpg"

    def test_file_match_first_group(self, file_match: Match) -> None:
        assert file_match.group(1) == "File:"

    def test_file_match_second_group(self, file_match: Match) -> None:
        assert file_match.group(2) == "Example.jpg"


class TestFileInput:
    @pytest.fixture(
        params=[
            "file:example",
            "example.jpg",
            "Foo Bar.gif",
            "Fil:Example.jpg",
        ],
    )
    def invalid_input(self, request: pytest.FixtureRequest) -> Match | None:
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
        return valid_file(request.param)

    def test_invalid_file_input(self, invalid_input: None) -> None:
        """Invalid file strings should not return regex match objects."""
        assert invalid_input is None

    def test_valid_file_input(self, valid_input: Match) -> None:
        """Valid file strings should return regex match objects."""
        assert valid_input is not None


class TestVerifyHash:
    def test_verify_hash(self, tmp_path: Path) -> None:
        """Confirm that verify_hash returns the proper SHA1 hash."""
        file_name = "testfile"
        file_contents = "foobar"
        file_sha1 = "8843d7f92416211de9ebb963ff4ce28125932878"

        tmp_file = tmp_path / file_name
        tmp_file.write_text(file_contents)

        assert verify_hash(str(tmp_file)) == file_sha1
