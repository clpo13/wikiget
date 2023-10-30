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
        args = construct_parser().parse_args(["Example.jpg"])
        with pytest.raises(ParseError):
            _ = get_dest(args.FILE, args)

    def test_get_dest_with_different_site(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
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
        tmp_file = tmp_path / "batch.txt"
        tmp_file.write_text("File:Foo.jpg\nFile:Bar.jpg\nFile:Baz.jpg\n")
        return read_batch_file(str(tmp_file))

    def test_batch_file_log(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.INFO)
        _ = read_batch_file("batch.txt")
        assert "Using file 'batch.txt' for batch download" in caplog.text

    def test_batch_file_length(self, dl_list: Dict[int, str]) -> None:
        assert len(dl_list) == 3

    def test_batch_file_contents(self, dl_list: Dict[int, str]) -> None:
        expected_list = {1: "File:Foo.jpg", 2: "File:Bar.jpg", 3: "File:Baz.jpg"}
        assert dl_list == expected_list

    @pytest.fixture()
    def dl_list_stdin(self, monkeypatch: pytest.MonkeyPatch) -> Dict[int, str]:
        monkeypatch.setattr(
            "sys.stdin", io.StringIO("File:Foo.jpg\nFile:Bar.jpg\nFile:Baz.jpg\n")
        )
        return read_batch_file("-")

    def test_batch_stdin_log(
        self, caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        caplog.set_level(logging.INFO)
        monkeypatch.setattr("sys.stdin", io.StringIO("File:Foo.jpg\n"))
        _ = read_batch_file("-")
        assert "Using stdin for batch download" in caplog.text

    def test_batch_stdin_length(self, dl_list_stdin: Dict[int, str]) -> None:
        assert len(dl_list_stdin) == 3

    def test_batch_stdin_contents(self, dl_list_stdin: Dict[int, str]) -> None:
        expected_list = {1: "File:Foo.jpg", 2: "File:Bar.jpg", 3: "File:Baz.jpg"}
        assert dl_list_stdin == expected_list

    @pytest.fixture()
    def dl_list_with_comment(self, tmp_path: Path) -> Dict[int, str]:
        tmp_file = tmp_path / "batch.txt"
        tmp_file.write_text("File:Foo.jpg\n\n#File:Bar.jpg\nFile:Baz.jpg\n")
        return read_batch_file(str(tmp_file))

    def test_batch_file_with_comment_length(
        self, dl_list_with_comment: Dict[int, str]
    ) -> None:
        assert len(dl_list_with_comment) == 2

    def test_batch_file_with_comment_contents(
        self, dl_list_with_comment: Dict[int, str]
    ) -> None:
        expected_list = {1: "File:Foo.jpg", 4: "File:Baz.jpg"}
        assert dl_list_with_comment == expected_list
