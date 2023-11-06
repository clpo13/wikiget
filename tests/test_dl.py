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

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from wikiget.dl import prep_download, process_download
from wikiget.file import File
from wikiget.wikiget import parse_args


class TestPrepDownload:
    @patch("wikiget.dl.query_api")
    @patch("wikiget.dl.connect_to_site")
    def test_prep_download(
        self, mock_connect_to_site: MagicMock, mock_query_api: MagicMock
    ) -> None:
        """The prep_download function should create the expected file object."""
        mock_site = Mock()
        mock_image = Mock()

        mock_connect_to_site.return_value = mock_site
        mock_query_api.return_value = mock_image

        expected_file = File(name="Example.jpg")
        expected_file.image = mock_image

        args = parse_args(["File:Example.jpg"])
        file = prep_download(args.FILE, args)
        assert file == expected_file

    def test_prep_download_with_existing_file(self, tmp_path: Path) -> None:
        """
        Attempting to download a file with the same destination name as an existing file
        should raise a FileExistsError.
        """
        tmp_file = tmp_path / "File:Example.jpg"
        tmp_file.write_text("nothing")
        args = parse_args(["File:Example.jpg", "-o", str(tmp_file)])
        with pytest.raises(FileExistsError):
            _ = prep_download(args.FILE, args)


class TestProcessDownload:
    @patch("wikiget.dl.batch_download")
    def test_batch_download(self, mock_batch_download: MagicMock) -> None:
        """A successful batch download should not return any errors."""
        mock_batch_download.return_value = 0

        args = parse_args(["-a", "batch.txt"])
        exit_code = process_download(args)
        assert exit_code == 0

    @patch("wikiget.dl.batch_download")
    def test_batch_download_with_errors(
        self, mock_batch_download: MagicMock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        Any errors during batch download should create a log message containing the
        number of errors and result in a non-zero exit code.
        """
        mock_batch_download.return_value = 4

        args = parse_args(["-a", "batch.txt"])
        exit_code = process_download(args)
        assert exit_code == 1
        assert "4 problems encountered during batch processing" in caplog.text

    @patch("wikiget.dl.prep_download")
    @patch("wikiget.dl.download")
    def test_single_download(
        self, mock_download: MagicMock, mock_prep_download: MagicMock
    ) -> None:
        """A successful download should not return any errors."""
        mock_download.return_value = 0
        mock_prep_download.return_value = File("Example.jpg")

        args = parse_args(["File:Example.jpg"])
        exit_code = process_download(args)
        assert exit_code == 0

    @patch("wikiget.dl.prep_download")
    @patch("wikiget.dl.download")
    def test_single_download_with_errors(
        self, mock_download: MagicMock, mock_prep_download: MagicMock
    ) -> None:
        """Any errors during download should result in a non-zero exit code."""
        mock_download.return_value = 1
        mock_prep_download.return_value = File("Example.jpg")

        args = parse_args(["File:Example.jpg"])
        exit_code = process_download(args)
        assert exit_code == 1
