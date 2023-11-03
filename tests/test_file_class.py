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

import pytest

from wikiget import DEFAULT_SITE
from wikiget.file import File


class TestFileClass:
    @pytest.fixture
    def file_with_name(self) -> File:
        """
        A File object created with only a name should set its destination property to
        the same value and its site property to the program's default site.
        """
        return File("foobar.jpg")

    def test_file_with_name(self, file_with_name: File) -> None:
        assert file_with_name.name == "foobar.jpg"

    def test_file_with_name_dest(self, file_with_name: File) -> None:
        assert file_with_name.dest == file_with_name.name

    def test_file_with_name_site(self, file_with_name: File) -> None:
        assert file_with_name.site == DEFAULT_SITE

    @pytest.fixture
    def file_with_name_and_dest(self) -> File:
        """
        A File object created with a name and destination should set those properties
        accordingly; they should not be the same value.
        """
        return File("foobar.jpg", dest="bazqux.jpg")

    def test_file_with_name_and_dest(self, file_with_name_and_dest: File) -> None:
        assert file_with_name_and_dest.dest == "bazqux.jpg"

    def test_name_and_dest_are_different(self, file_with_name_and_dest: File) -> None:
        assert file_with_name_and_dest.dest != file_with_name_and_dest.name

    def test_file_with_name_and_site(self) -> None:
        """
        A File object created with a name and site should set those properties
        accordingly and not use the program's default site.
        """
        file = File("foobar.jpg", site="en.wikipedia.org")
        assert file.site == "en.wikipedia.org"
