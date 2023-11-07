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

import logging
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests
from mwclient import Site

from wikiget.dl import batch_download, download, prep_download, process_download
from wikiget.exceptions import ParseError
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
    def test_process_batch_download(self, mock_batch_download: MagicMock) -> None:
        """A successful batch download should not return any errors."""
        mock_batch_download.return_value = 0

        args = parse_args(["-a", "batch.txt"])
        exit_code = process_download(args)

        assert exit_code == 0

    @patch("wikiget.dl.batch_download")
    def test_process_batch_download_with_errors(
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
    def test_process_single_download(
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
    def test_process_single_download_with_errors(
        self, mock_download: MagicMock, mock_prep_download: MagicMock
    ) -> None:
        """Any errors during download should result in a non-zero exit code."""
        mock_download.return_value = 1
        mock_prep_download.return_value = File("Example.jpg")

        args = parse_args(["File:Example.jpg"])
        exit_code = process_download(args)

        assert exit_code == 1

    @patch("wikiget.dl.prep_download")
    def test_process_single_download_parse_error(
        self, mock_prep_download: MagicMock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        If process_download catches a ParseError, it should create an error log message.
        """
        mock_prep_download.side_effect = ParseError("error message")

        args = parse_args(["File:Example.jpg"])
        _ = process_download(args)

        assert mock_prep_download.called
        assert caplog.record_tuples == [("wikiget.dl", logging.ERROR, "error message")]

    @patch("wikiget.dl.prep_download")
    def test_process_single_download_file_exists_error(
        self, mock_prep_download: MagicMock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        If process_download catches a FileExistsError, it should create a warning log
        message.
        """
        mock_prep_download.side_effect = FileExistsError("warning message")

        args = parse_args(["File:Example.jpg"])
        _ = process_download(args)

        assert mock_prep_download.called
        assert caplog.record_tuples == [
            ("wikiget.dl", logging.WARNING, "warning message"),
        ]

    @patch("wikiget.dl.prep_download")
    def test_process_single_download_other_error(
        self, mock_prep_download: MagicMock
    ) -> None:
        """
        If process_download catches any other errors, it should return 1.
        """
        mock_prep_download.side_effect = requests.ConnectionError

        args = parse_args(["File:Example.jpg"])
        exit_code = process_download(args)

        assert mock_prep_download.called
        assert exit_code == 1


class TestBatchDownload:
    @patch("wikiget.dl.download")
    @patch("wikiget.dl.prep_download")
    @patch("wikiget.dl.read_batch_file")
    def test_batch_download(
        self,
        mock_read_batch_file: MagicMock,
        mock_prep_download: MagicMock,
        mock_download: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        caplog.set_level(logging.INFO)

        # set dummy return values for read_batch_file() and download()
        mock_read_batch_file.return_value = {1: "File:Example.jpg"}
        mock_download.return_value = 0

        args = parse_args(["-a", "batch.txt"])
        errors = batch_download(args)

        assert mock_read_batch_file.called
        assert mock_prep_download.called
        assert mock_download.called
        assert caplog.record_tuples == [
            ("wikiget.dl", logging.INFO, "Processing 'File:Example.jpg' at line 1")
        ]
        assert errors == 0

    @patch("wikiget.dl.read_batch_file")
    def test_batch_download_os_error(
        self, mock_read_batch_file: MagicMock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        If batch_download catches an OSError, it should print an error log message
        and exit the program.
        """
        mock_read_batch_file.side_effect = OSError("error message")

        args = parse_args(["-a", "batch.txt"])
        with pytest.raises(SystemExit):
            _ = batch_download(args)

        assert mock_read_batch_file.called
        assert caplog.record_tuples == [
            ("wikiget.dl", logging.ERROR, "File could not be read: error message"),
        ]

    @patch("wikiget.dl.prep_download")
    @patch("wikiget.dl.read_batch_file")
    def test_batch_download_parse_error(
        self,
        mock_read_batch_file: MagicMock,
        mock_prep_download: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        mock_read_batch_file.return_value = {1: "File:Example.jpg"}
        mock_prep_download.side_effect = ParseError("warning message")

        args = parse_args(["-a", "batch.txt"])
        errors = batch_download(args)

        assert mock_read_batch_file.called
        assert mock_prep_download.called
        assert caplog.record_tuples == [
            ("wikiget.dl", logging.WARNING, "warning message (line 1)"),
        ]
        assert errors == 1

    @patch("wikiget.dl.prep_download")
    @patch("wikiget.dl.read_batch_file")
    def test_batch_download_file_exists_error(
        self,
        mock_read_batch_file: MagicMock,
        mock_prep_download: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        mock_read_batch_file.return_value = {1: "File:Example.jpg"}
        mock_prep_download.side_effect = FileExistsError("warning message")

        args = parse_args(["-a", "batch.txt"])
        errors = batch_download(args)

        assert mock_read_batch_file.called
        assert mock_prep_download.called
        assert caplog.record_tuples == [
            ("wikiget.dl", logging.WARNING, "warning message"),
        ]
        assert errors == 1

    @patch("wikiget.dl.prep_download")
    @patch("wikiget.dl.read_batch_file")
    def test_batch_download_other_error(
        self,
        mock_read_batch_file: MagicMock,
        mock_prep_download: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        mock_read_batch_file.return_value = {1: "File:Example.jpg"}
        mock_prep_download.side_effect = requests.ConnectionError

        args = parse_args(["-a", "batch.txt"])
        errors = batch_download(args)

        assert mock_read_batch_file.called
        assert mock_prep_download.called
        assert caplog.record_tuples == [
            (
                "wikiget.dl",
                logging.WARNING,
                "Unable to download 'File:Example.jpg' (line 1) due to an error",
            ),
        ]
        assert errors == 1


@pytest.mark.usefixtures("mock_get")
class TestDownload:
    @pytest.fixture
    def mock_file(self, tmp_path: Path) -> File:
        file = File(name="Example.jpg", dest=str(tmp_path / "Example.jpg"))
        file.image = Mock()
        file.image.exists = True
        file.image.imageinfo = {
            "url": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Example.jpg",
            "size": 9022,
            "sha1": "d01b79a6781c72ac9bfff93e5e2cfbeef4efc840",
        }
        file.image.site = MagicMock(Site)
        file.image.site.host = "commons.wikimedia.org"
        file.image.site.connection = requests.Session()
        return file

    def test_download(self, mock_file: File, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.INFO)

        with patch("wikiget.dl.verify_hash") as mock_verify_hash:
            mock_verify_hash.return_value = "d01b79a6781c72ac9bfff93e5e2cfbeef4efc840"
            args = parse_args(["File:Example.jpg"])
            errors = download(mock_file, args)

        assert caplog.record_tuples == [
            (
                "wikiget.dl",
                logging.INFO,
                "[Example.jpg] Downloading 'Example.jpg' (9022 bytes) from "
                "commons.wikimedia.org",
            ),
            (
                "wikiget.dl",
                logging.INFO,
                "[Example.jpg] "
                "https://upload.wikimedia.org/wikipedia/commons/a/a9/Example.jpg",
            ),
            (
                "wikiget.dl",
                logging.INFO,
                "[Example.jpg] Remote file SHA1 is "
                "d01b79a6781c72ac9bfff93e5e2cfbeef4efc840",
            ),
            (
                "wikiget.dl",
                logging.INFO,
                "[Example.jpg] Local file SHA1 is "
                "d01b79a6781c72ac9bfff93e5e2cfbeef4efc840",
            ),
            ("wikiget.dl", logging.INFO, "[Example.jpg] Hashes match!"),
            ("wikiget.dl", logging.INFO, "[Example.jpg] 'Example.jpg' downloaded"),
        ]
        assert errors == 0

    def test_download_with_output(
        self, mock_file: File, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.INFO)

        tmp_file = mock_file.dest

        with patch("wikiget.dl.verify_hash") as mock_verify_hash:
            mock_verify_hash.return_value = "d01b79a6781c72ac9bfff93e5e2cfbeef4efc840"
            args = parse_args(["-o", tmp_file, "File:Example.jpg"])
            errors = download(mock_file, args)

        assert caplog.record_tuples[0] == (
            "wikiget.dl",
            logging.INFO,
            "[Example.jpg] Downloading 'Example.jpg' (9022 bytes) from "
            f"commons.wikimedia.org to '{tmp_file}'",
        )
        assert caplog.record_tuples[5] == (
            "wikiget.dl",
            logging.INFO,
            f"[Example.jpg] 'Example.jpg' downloaded to '{tmp_file}'",
        )
        assert errors == 0

    def test_download_dry_run(
        self, mock_file: File, caplog: pytest.LogCaptureFixture
    ) -> None:
        caplog.set_level(logging.INFO)

        args = parse_args(["-n", "File:Example.jpg"])
        errors = download(mock_file, args)

        # ignore first two log records since we tested for those earlier
        assert caplog.record_tuples[2:] == [
            ("wikiget.dl", logging.WARNING, "[Example.jpg] Dry run; download skipped"),
        ]
        assert errors == 0

    def test_download_os_error(
        self, mock_file: File, caplog: pytest.LogCaptureFixture
    ) -> None:
        with patch("wikiget.dl.open") as mock_open:
            mock_open.side_effect = OSError("write error")
            args = parse_args(["File:Example.jpg"])
            errors = download(mock_file, args)

        assert caplog.record_tuples == [
            (
                "wikiget.dl",
                logging.ERROR,
                "[Example.jpg] File could not be written: write error",
            ),
        ]
        assert errors == 1

    def test_download_verify_os_error(
        self, mock_file: File, caplog: pytest.LogCaptureFixture
    ) -> None:
        with patch("wikiget.dl.verify_hash") as mock_verify_hash:
            mock_verify_hash.side_effect = OSError("read error")
            args = parse_args(["File:Example.jpg"])
            errors = download(mock_file, args)

        assert caplog.record_tuples == [
            (
                "wikiget.dl",
                logging.ERROR,
                "[Example.jpg] File downloaded but could not be verified: read error",
            )
        ]
        assert errors == 1

    def test_download_verify_hash_mismatch(
        self, mock_file: File, caplog: pytest.LogCaptureFixture
    ) -> None:
        with patch("wikiget.dl.verify_hash") as mock_verify_hash:
            mock_verify_hash.return_value = "mismatch"
            args = parse_args(["File:Example.jpg"])
            errors = download(mock_file, args)

        assert caplog.record_tuples == [
            (
                "wikiget.dl",
                logging.ERROR,
                "[Example.jpg] Hash mismatch! Downloaded file may be corrupt.",
            )
        ]
        assert errors == 1

    def test_download_nonexistent_file(
        self, mock_file: File, caplog: pytest.LogCaptureFixture
    ) -> None:
        mock_file.image.exists = False

        args = parse_args(["File:Example.jpg"])
        errors = download(mock_file, args)

        assert caplog.record_tuples == [
            (
                "wikiget.dl",
                logging.WARNING,
                "[Example.jpg] Target does not appear to be a valid file",
            ),
        ]
        assert errors == 1
