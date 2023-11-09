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

"""Define fixtures used across all tests in this folder."""

from os import chdir
from pathlib import Path

import pytest
import requests_mock as rm

from wikiget.file import File


@pytest.fixture(autouse=True)
def _chdir_to_tmp_dir(tmp_path: Path) -> None:
    """Change to a temporary directory before running tests.

    :param tmp_path: temporary path object
    :type tmp_path: Path
    """
    chdir(tmp_path)


@pytest.fixture()
def file_with_name() -> File:
    """Create a test File with only a filename.

    A File object created with only a name should set its destination property to
    the same value and its site property to the program's default site.

    :return: File object created using a filename
    :rtype: File
    """
    return File("foobar.jpg")


@pytest.fixture()
def file_with_name_and_dest() -> File:
    """Create a test File with a name and destination.

    :return: File object created with name and dest
    :rtype: File
    """
    return File(name="foobar.jpg", dest="bazqux.jpg")


@pytest.fixture()
def _mock_get(requests_mock: rm.Mocker) -> None:
    """Fake the download request for the true URL of File:Example.jpg.

    :param requests_mock: a requests_mock Mocker object
    :type requests_mock: rm.Mocker
    """
    requests_mock.get(
        "https://upload.wikimedia.org/wikipedia/commons/a/a9/Example.jpg",
        text="data",
    )
