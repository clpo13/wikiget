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

from wikiget.file import File


def test_file_with_name_only():
    file = File("foobar.jpg")
    assert file.name == "foobar.jpg"
    assert file.dest == file.name


def test_file_with_name_and_dest():
    file = File("foobar.jpg", "bazqux.jpg")
    assert file.name == "foobar.jpg"
    assert file.dest == "bazqux.jpg"
    assert file.dest != file.name
