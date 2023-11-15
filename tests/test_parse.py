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

"""Define tests related to the wikiget.parse module."""

from __future__ import annotations

import io
import logging
from typing import TYPE_CHECKING

import pytest

from wikiget.exceptions import ParseError
from wikiget.parse import get_dest, read_batch_file
from wikiget.wikiget import parse_args

if TYPE_CHECKING:
    from pathlib import Path

    from wikiget.file import File


class TestGetDest:
    """Define tests related to wikiget.parse.get_dest."""

    @pytest.fixture()
    def file_with_filename(self) -> File:
        """Create a File object with a given filename.

        When only the filename is given as an argument, the dest attribute will be set
        to the same value as the filename and the default site will be used.

        :return: a File object created using a filename
        :rtype: File
        """
        args = parse_args(["File:Example.jpg"])
        return get_dest(args.FILE, args)

    def test_get_dest_name_with_filename(self, file_with_filename: File) -> None:
        """Test that the file's name attribute is set correctly."""
        assert file_with_filename.name == "Example.jpg"

    def test_get_dest_with_filename(self, file_with_filename: File) -> None:
        """Test that the file's dest attribute is set correctly.

        Unless otherwise specified, it should match the filename.
        """
        assert file_with_filename.dest == "Example.jpg"

    def test_get_dest_site_with_filename(self, file_with_filename: File) -> None:
        """Test that the file's site attribute is set correctly.

        Unless otherwise specified, it should be the default site.
        """
        assert file_with_filename.site == "commons.wikimedia.org"

    @pytest.fixture()
    def file_with_url(self) -> File:
        """Create a File object with a given URL.

        When a URL is passed to get_dest, it will create a File object with the
        filename and site parsed from the URL.

        :return: a File object created using a URL
        :rtype: File
        """
        args = parse_args(["https://en.wikipedia.org/wiki/File:Example.jpg"])
        return get_dest(args.FILE, args)

    def test_get_dest_name_with_url(self, file_with_url: File) -> None:
        """Test that the file's name attribute is set correctly."""
        assert file_with_url.name == "Example.jpg"

    def test_get_dest_with_url(self, file_with_url: File) -> None:
        """Test that the file's dest attribute is set correctly."""
        assert file_with_url.dest == "Example.jpg"

    def test_get_dest_site_with_url(self, file_with_url: File) -> None:
        """Test that the file's site attribute is set correctly.

        The site should be what was parsed from the URL, not the default site.
        """
        assert file_with_url.site == "en.wikipedia.org"

    def test_get_dest_with_bad_filename(self) -> None:
        """Test that a ParseError exception is raised if the filename is invalid."""
        args = parse_args(["Example.jpg"])
        with pytest.raises(ParseError):
            _ = get_dest(args.FILE, args)

    def test_get_dest_with_different_site(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that a warning log message is created.

        If a URL is passed to get_dest and a site is also given on the command line,
        the site in the URL should be used and a warning log message created.
        """
        args = parse_args(
            [
                "https://commons.wikimedia.org/wiki/File:Example.jpg",
                "--site",
                "commons.wikimedia.org",
            ]
        )
        _ = get_dest(args.FILE, args)
        assert "Target is a URL; ignoring site specified with --site" in caplog.text


class TestReadBatchFile:
    """Define tests related to wikiget.parse.read_batch_file."""

    @pytest.fixture()
    def dl_dict(self, batch_file: Path) -> dict[int, str]:
        """Create and process a test batch file with three lines.

        :param batch_file: test batch file
        :type batch_file: Path
        :return: dictionary representation of the input file
        :rtype: dict[int, str]
        """
        return read_batch_file(str(batch_file))

    def test_batch_file_log(
        self, caplog: pytest.LogCaptureFixture, batch_file: Path
    ) -> None:
        """Test that reading a batch file creates an info log message.

        Reading in a batch file should create an info log message containing the name
        of the batch file.
        """
        caplog.set_level(logging.INFO)
        _ = read_batch_file(str(batch_file))
        assert f"Using file '{batch_file}' for batch download" in caplog.text

    def test_batch_file_length(self, dl_dict: dict[int, str]) -> None:
        """Test that the batch dict has the same number of lines as the batch file."""
        assert len(dl_dict) == 3

    def test_batch_file_contents(self, dl_dict: dict[int, str]) -> None:
        """Test that the batch dict has the correct line numbers and filenames.

        The processed batch dict should have the batch file's line numbers and filenames
        as keys and values, respectively.
        """
        expected_dict = {1: "File:Foo.jpg", 2: "File:Bar.jpg", 3: "File:Baz.jpg"}
        assert dl_dict == expected_dict

    @pytest.fixture()
    def dl_dict_stdin(self, monkeypatch: pytest.MonkeyPatch) -> dict[int, str]:
        """Pass three lines of filenames from stdin to read_batch_file to create a dict.

        :param monkeypatch: Pytest monkeypatch helper
        :type monkeypatch: pytest.MonkeyPatch
        :return: dictionary representation of the input
        :rtype: dict[int, str]
        """
        monkeypatch.setattr(
            "sys.stdin", io.StringIO("File:Foo.jpg\nFile:Bar.jpg\nFile:Baz.jpg\n")
        )
        return read_batch_file("-")

    def test_batch_stdin_log(
        self, caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """Test that using stdin for batch processing creates an info log message."""
        caplog.set_level(logging.INFO)
        monkeypatch.setattr("sys.stdin", io.StringIO("File:Foo.jpg\n"))
        _ = read_batch_file("-")
        assert "Using stdin for batch download" in caplog.text

    def test_batch_stdin_length(self, dl_dict_stdin: dict[int, str]) -> None:
        """Test that the batch dict has the correct number of items.

        The dict should contain the same number of items as lines in the input.
        """
        assert len(dl_dict_stdin) == 3

    def test_batch_stdin_contents(self, dl_dict_stdin: dict[int, str]) -> None:
        """Test that the batch dict has the correct keys and values.

        The line numbers and filenames from the input should be the keys and values,
        respectively.
        """
        expected_list = {1: "File:Foo.jpg", 2: "File:Bar.jpg", 3: "File:Baz.jpg"}
        assert dl_dict_stdin == expected_list

    @pytest.fixture()
    def dl_dict_with_comment(self, batch_file_with_comment: Path) -> dict[int, str]:
        """Create and process a test batch file with four lines.

        In addition to filenames, one line is commented out and another line is blank.

        :param batch_file_with_comment: test batch file
        :type batch_file_with_comment: Path
        :return: dictionary representation of the input file
        :rtype: dict[int, str]
        """
        return read_batch_file(str(batch_file_with_comment))

    def test_batch_file_with_comment_length(
        self, dl_dict_with_comment: dict[int, str]
    ) -> None:
        """Test the length of the dict created from a file with comments.

        The processed batch dict should contain the same number of items as uncommented
        and non-blank lines in the input.
        """
        assert len(dl_dict_with_comment) == 2

    def test_batch_file_with_comment_contents(
        self, dl_dict_with_comment: dict[int, str]
    ) -> None:
        """Test that the batch dict has the correct keys and values.

        The processed batch dict should have the correct line numbers and filenames as
        keys and values, respectively, skipping any commented or blank lines.
        """
        expected_list = {1: "File:Foo.jpg", 4: "File:Baz.jpg"}
        assert dl_dict_with_comment == expected_list
