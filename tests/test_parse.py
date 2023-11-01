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

import io
import logging
from pathlib import Path
from typing import Dict

import pytest

from wikiget.exceptions import ParseError
from wikiget.file import File
from wikiget.parse import get_dest, read_batch_file
from wikiget.wikiget import construct_parser


class TestGetDest:
    @pytest.fixture(scope="class")
    def file_with_filename(self) -> File:
        """
        When a filename is passed to get_dest, it should create a File object with the
        correct name and dest and the default site.
        """
        args = construct_parser().parse_args(["File:Example.jpg"])
        return get_dest(args.FILE, args)

    def test_get_dest_name_with_filename(self, file_with_filename: File) -> None:
        assert file_with_filename.name == "Example.jpg"

    def test_get_dest_with_filename(self, file_with_filename: File) -> None:
        assert file_with_filename.dest == "Example.jpg"

    def test_get_dest_site_with_filename(self, file_with_filename: File) -> None:
        assert file_with_filename.site == "commons.wikimedia.org"

    @pytest.fixture(scope="class")
    def file_with_url(self) -> File:
        """
        When a URL is passed to get_dest, it should create a File object with the
        correct name and dest and the site from the URL.
        """
        args = construct_parser().parse_args(
            ["https://en.wikipedia.org/wiki/File:Example.jpg"]
        )
        return get_dest(args.FILE, args)

    def test_get_dest_name_with_url(self, file_with_url: File) -> None:
        assert file_with_url.name == "Example.jpg"

    def test_get_dest_with_url(self, file_with_url: File) -> None:
        assert file_with_url.dest == "Example.jpg"

    def test_get_dest_site_with_url(self, file_with_url: File) -> None:
        assert file_with_url.site == "en.wikipedia.org"

    def test_get_dest_with_bad_filename(self) -> None:
        """
        The get_dest function should raise a ParseError if the filename is invalid.
        """
        args = construct_parser().parse_args(["Example.jpg"])
        with pytest.raises(ParseError):
            _ = get_dest(args.FILE, args)

    def test_get_dest_with_different_site(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        If a URL is passed to get_dest and a site is also given on the command line,
        the site in the URL should be used and a warning log message created.
        """
        args = construct_parser().parse_args(
            [
                "https://commons.wikimedia.org/wiki/File:Example.jpg",
                "--site",
                "commons.wikimedia.org",
            ]
        )
        _ = get_dest(args.FILE, args)
        assert "Target is a URL; ignoring site specified with --site" in caplog.text


class TestReadBatchFile:
    @pytest.fixture()
    def dl_list(self, tmp_path: Path) -> Dict[int, str]:
        """
        Create and process a test batch file with three lines, returning a dictionary.
        """
        tmp_file = tmp_path / "batch.txt"
        tmp_file.write_text("File:Foo.jpg\nFile:Bar.jpg\nFile:Baz.jpg\n")
        return read_batch_file(str(tmp_file))

    def test_batch_file_log(
        self, caplog: pytest.LogCaptureFixture, tmp_path: Path
    ) -> None:
        """
        Reading in a batch file should create an info log message containing the name
        of the batch file.
        """
        caplog.set_level(logging.INFO)
        tmp_file = tmp_path / "batch.txt"
        tmp_file.write_text("File:Foo.jpg\n")
        _ = read_batch_file(str(tmp_file))
        assert f"Using file '{tmp_file}' for batch download" in caplog.text

    def test_batch_file_length(self, dl_list: Dict[int, str]) -> None:
        """
        The processed batch dict should have the same number of items as lines in the
        batch file.
        """
        assert len(dl_list) == 3

    def test_batch_file_contents(self, dl_list: Dict[int, str]) -> None:
        """
        The processed batch dict should have the correct line numbers and filenames as
        keys and values, respectively.
        """
        expected_list = {1: "File:Foo.jpg", 2: "File:Bar.jpg", 3: "File:Baz.jpg"}
        assert dl_list == expected_list

    @pytest.fixture()
    def dl_list_stdin(self, monkeypatch: pytest.MonkeyPatch) -> Dict[int, str]:
        """
        Pass three lines of filenames from stdin to read_batch_file and return a dict.
        """
        monkeypatch.setattr(
            "sys.stdin", io.StringIO("File:Foo.jpg\nFile:Bar.jpg\nFile:Baz.jpg\n")
        )
        return read_batch_file("-")

    def test_batch_stdin_log(
        self, caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        Using stdin for batch processing should create an info log message saying so.
        """
        caplog.set_level(logging.INFO)
        monkeypatch.setattr("sys.stdin", io.StringIO("File:Foo.jpg\n"))
        _ = read_batch_file("-")
        assert "Using stdin for batch download" in caplog.text

    def test_batch_stdin_length(self, dl_list_stdin: Dict[int, str]) -> None:
        """
        The processed batch dict should have the same number of items as lines in the
        input.
        """
        assert len(dl_list_stdin) == 3

    def test_batch_stdin_contents(self, dl_list_stdin: Dict[int, str]) -> None:
        """
        The processed batch dict should have the correct line numbers and filenames as
        keys and values, respectively.
        """
        expected_list = {1: "File:Foo.jpg", 2: "File:Bar.jpg", 3: "File:Baz.jpg"}
        assert dl_list_stdin == expected_list

    @pytest.fixture()
    def dl_list_with_comment(self, tmp_path: Path) -> Dict[int, str]:
        """
        Create and process a test batch file with four lines, one of which is
        commented out and another of which is blank, and return a dictionary.
        """
        tmp_file = tmp_path / "batch.txt"
        tmp_file.write_text("File:Foo.jpg\n\n#File:Bar.jpg\nFile:Baz.jpg\n")
        return read_batch_file(str(tmp_file))

    def test_batch_file_with_comment_length(
        self, dl_list_with_comment: Dict[int, str]
    ) -> None:
        """
        The processed batch dict should contain the same number of items as uncommented
        and non-blank lines in the input.
        """
        assert len(dl_list_with_comment) == 2

    def test_batch_file_with_comment_contents(
        self, dl_list_with_comment: Dict[int, str]
    ) -> None:
        """
        The processed batch dict should have the correct line numbers and filenames as
        keys and values, respectively, skipping any commented or blank lines.
        """
        expected_list = {1: "File:Foo.jpg", 4: "File:Baz.jpg"}
        assert dl_list_with_comment == expected_list
