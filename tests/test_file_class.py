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

"""Define tests related to the wikiget.file module."""

from wikiget import DEFAULT_SITE
from wikiget.file import File


class TestFileClass:
    """Define tests related to wikiget.file.File creation."""

    def test_file_with_name(self, file_with_name: File) -> None:
        """The file name attribute should equal what was passed in."""
        assert file_with_name.name == "foobar.jpg"

    def test_file_with_name_dest(self, file_with_name: File) -> None:
        """The file dest attribute should be the same as the name."""
        assert file_with_name.dest == file_with_name.name

    def test_file_with_name_site(self, file_with_name: File) -> None:
        """The file site attribute should equal the default site."""
        assert file_with_name.site == DEFAULT_SITE

    def test_file_with_name_and_dest(self, file_with_name_and_dest: File) -> None:
        """The file dest attribute should equal what was passed in."""
        assert file_with_name_and_dest.dest == "bazqux.jpg"

    def test_name_and_dest_are_different(self, file_with_name_and_dest: File) -> None:
        """The file name and dest attributes should not be the same."""
        assert file_with_name_and_dest.dest != file_with_name_and_dest.name

    def test_file_with_name_and_site(self) -> None:
        """Test the attributes of a File created with a name and site.

        A File object created with a name and site should set those properties
        accordingly and not use the program's default site.
        """
        file = File("foobar.jpg", site="en.wikipedia.org")
        assert file.site == "en.wikipedia.org"


class TestFileComparison:
    """Define tests related to wikiget.file.File comparisons."""

    def test_file_equality(self, file_with_name: File) -> None:
        """Test that two similar Files equal each other."""
        assert File(name="foobar.jpg") == file_with_name

    def test_file_inequality(self, file_with_name: File) -> None:
        """Test that two dissimilar Files do not equal each other."""
        assert File(name="foobaz.jpg", dest="output.jpg") != file_with_name

    def test_file_comparison_with_non_file(self, file_with_name: File) -> None:
        """Test what happens when a File is compared with a different object.

        The equality comparison should return NotImplemented when comparing non-Files
        with Files.
        """
        not_a_file = {"name": "foobar.jpg", "dest": "foobar.jpg"}
        assert file_with_name.__eq__(not_a_file) == NotImplemented
