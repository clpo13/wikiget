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

# 2x2 JPEG
TEST_FILE_BYTES = (
    b"\xff\xd8\xff\xdb\x00C\x00\x03\x02\x02\x02\x02\x02\x03\x02\x02\x02\x03\x03\x03\x03"
    b"\x04\x06\x04\x04\x04\x04\x04\x08\x06\x06\x05\x06\t\x08\n\n\t\x08\t\t\n\x0c\x0f"
    b"\x0c\n\x0b\x0e\x0b\t\t\r\x11\r\x0e\x0f\x10\x10\x11\x10\n\x0c\x12\x13\x12\x10\x13"
    b"\x0f\x10\x10\x10\xff\xc0\x00\x0b\x08\x00\x02\x00\x02\x01\x01\x11\x00\xff\xc4\x00"
    b"\x14\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\t\xff"
    b"\xc4\x00\x14\x10\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00"
    b"\x00\xff\xda\x00\x08\x01\x01\x00\x00?\x00T\xdf\xff\xd9"
)


@pytest.fixture(autouse=True, scope="session")
def _chdir_to_tmp_dir(tmp_path_factory: pytest.TempPathFactory) -> None:
    """Change to the base temporary directory before running tests.

    :param tmp_path_factory: temporary path generator
    :type tmp_path_factory: pytest.TempPathFactory
    """
    chdir(tmp_path_factory.getbasetemp())


@pytest.fixture(scope="session")
def batch_file(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Create a temporary batch file for testing.

    :param tmp_path_factory: temporary path generator
    :type tmp_path_factory: pytest.TempPathFactory
    :return: test batch file
    :rtype: pathlib.Path
    """
    tmp_file = tmp_path_factory.getbasetemp() / "batch.txt"
    tmp_file.write_text("File:Foo.jpg\nFile:Bar.jpg\nFile:Baz.jpg\n")
    return tmp_file


@pytest.fixture(scope="session")
def batch_file_with_comment(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Create a temporary batch file with comments for testing.

    :param tmp_path_factory: temporary path generator
    :type tmp_path_factory: pytest.TempPathFactory
    :return: test batch file
    :rtype: pathlib.Path
    """
    tmp_file = tmp_path_factory.getbasetemp() / "batch_with_comment.txt"
    tmp_file.write_text("File:Foo.jpg\n\n#File:Bar.jpg\nFile:Baz.jpg\n")
    return tmp_file


@pytest.fixture(scope="session")
def test_file(tmp_path_factory: pytest.TempPathFactory) -> Path:
    """Create a fake downloaded file with known contents.

    :param tmp_path_factory: temporary path generator
    :type tmp_path_factory: pytest.TempPathFactory
    :return: test file
    :rtype: pathlib.Path
    """
    tmp_file = tmp_path_factory.getbasetemp() / "Testfile.jpg"
    tmp_file.write_bytes(TEST_FILE_BYTES)
    return tmp_file


@pytest.fixture()
def file_with_name() -> File:
    """Create a test File with only a filename.

    A File object created with only a name should set its destination property to
    the same value and its site property to the program's default site.

    :return: File object created using a filename
    :rtype: wikiget.file.File
    """
    return File("foobar.jpg")


@pytest.fixture()
def file_with_name_and_dest() -> File:
    """Create a test File with a name and destination.

    :return: File object created with name and dest
    :rtype: wikiget.file.File
    """
    return File(name="foobar.jpg", dest="bazqux.jpg")


@pytest.fixture()
def _mock_get(requests_mock: rm.Mocker) -> None:
    """Fake the download request for the true URL of File:Example.jpg.

    :param requests_mock: a requests_mock Mocker object
    :type requests_mock: requests_mock.Mocker
    """
    requests_mock.get(
        "https://upload.wikimedia.org/wikipedia/commons/a/a9/Example.jpg",
        content=TEST_FILE_BYTES,
    )
