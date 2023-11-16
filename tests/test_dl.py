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

"""Define tests related to the wikiget.dl module."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests
from mwclient import Site

from wikiget.dl import batch_download, download, prep_download, process_download
from wikiget.exceptions import ParseError
from wikiget.file import File
from wikiget.wikiget import parse_args

if TYPE_CHECKING:
    from pathlib import Path


class TestPrepDownload:
    """Define tests related to wikiget.dl.prep_download."""

    def test_prep_download(self) -> None:
        """The prep_download function should create the expected file object."""
        expected_file = File(name="Example.jpg")

        args = parse_args(["File:Example.jpg"])
        file = prep_download(args.FILE, args)

        assert file == expected_file

    def test_prep_download_with_existing_file(self, test_file: Path) -> None:
        """Test that an exception is raised when the download file already exists.

        Attempting to download a file with the same destination name as an existing file
        should raise a FileExistsError.
        """
        args = parse_args(["File:Example.jpg", "-o", str(test_file)])
        with pytest.raises(FileExistsError):
            _ = prep_download(args.FILE, args)


class TestProcessDownload:
    """Define tests related to wikiget.dl.process_download."""

    @patch("wikiget.dl.batch_download")
    def test_process_batch_download(self, mock_batch_download: MagicMock) -> None:
        """A successful batch download should have an exit code of zero (no errors)."""
        mock_batch_download.return_value = 0

        args = parse_args(["-a", "batch.txt"])
        exit_code = process_download(args)

        assert exit_code == 0

    @patch("wikiget.dl.batch_download")
    def test_process_batch_download_with_errors(
        self, mock_batch_download: MagicMock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """A batch download with errors should have a non-zero exit code.

        Additionally, it should create a log message containing the number of errors.
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
        """A successful download should have an exit code of zero (no errors)."""
        mock_download.return_value = 0
        mock_prep_download.return_value = File("Example.jpg")

        args = parse_args(["File:Example.jpg"])
        with patch("wikiget.dl.connect_to_site"), patch("wikiget.dl.query_api"):
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
        with patch("wikiget.dl.connect_to_site"), patch("wikiget.dl.query_api"):
            exit_code = process_download(args)

        assert exit_code == 1

    @patch("wikiget.dl.prep_download")
    def test_process_single_download_parse_error(
        self, mock_prep_download: MagicMock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """If ParseError is raised, it should create an error log message."""
        mock_prep_download.side_effect = ParseError("error message")

        args = parse_args(["File:Example.jpg"])
        _ = process_download(args)

        assert mock_prep_download.called
        assert caplog.record_tuples == [("wikiget.dl", logging.ERROR, "error message")]

    @patch("wikiget.dl.prep_download")
    def test_process_single_download_file_exists_error(
        self, mock_prep_download: MagicMock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """If FileExistsError is raised, it should create a warning log message."""
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
        """If any other errors occur, an exit code of 1 should be returned."""
        mock_prep_download.side_effect = requests.ConnectionError

        args = parse_args(["File:Example.jpg"])
        exit_code = process_download(args)

        assert mock_prep_download.called
        assert exit_code == 1


class TestBatchDownload:
    """Define tests related to wikiget.dl.batch_download."""

    @patch("wikiget.dl.download")
    @patch("wikiget.dl.read_batch_file")
    def test_batch_download(
        self,
        mock_read_batch_file: MagicMock,
        mock_download: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that no errors are returned for a successful batch download.

        Additionally, a log message should be created for each line in the batch file
        and should contain the line number and contents.
        """
        caplog.set_level(logging.INFO)

        # set dummy return values for read_batch_file() and download()
        mock_read_batch_file.return_value = {1: "File:Example.jpg"}
        mock_download.return_value = 0

        args = parse_args(["-a", "batch.txt"])
        with patch("wikiget.dl.query_api"), patch("wikiget.dl.connect_to_site"), patch(
            "wikiget.dl.prep_download"
        ):
            errors = batch_download(args)

        assert mock_read_batch_file.called
        assert mock_download.called
        assert caplog.record_tuples == [
            ("wikiget.dl", logging.INFO, "Processing 'File:Example.jpg' at line 1")
        ]
        assert errors == 0

    @patch("wikiget.dl.connect_to_site")
    @patch("wikiget.dl.prep_download")
    @patch("wikiget.dl.read_batch_file")
    def test_batch_download_reuse_site(
        self,
        mock_read_batch_file: MagicMock,
        mock_prep_download: MagicMock,
        mock_connect_to_site: MagicMock,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that an existing site object is reused."""
        caplog.set_level(logging.DEBUG)

        mock_site = MagicMock()
        mock_site.host = "commons.wikimedia.org"
        mock_read_batch_file.return_value = {
            1: "File:Example.jpg",
            2: "File:Foobar.jpg",
        }
        mock_prep_download.return_value = File("Example.jpg")
        mock_connect_to_site.return_value = mock_site

        args = parse_args(["-a", "batch.txt"])
        with patch("wikiget.dl.download"), patch("wikiget.dl.query_api"):
            _ = batch_download(args)

        assert mock_read_batch_file.called
        assert mock_prep_download.called
        assert mock_connect_to_site.called
        assert caplog.record_tuples[1] == (
            "wikiget.dl",
            logging.DEBUG,
            "Made a new site connection",
        )
        assert caplog.record_tuples[3] == (
            "wikiget.dl",
            logging.DEBUG,
            "Reused an existing site connection",
        )

    @patch("wikiget.dl.read_batch_file")
    def test_batch_download_os_error(
        self, mock_read_batch_file: MagicMock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that an OSError results in an error log message and program exit."""
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
        """Test that a warning log message is created if ParseError is raised.

        The resulting log message should contain the relevant line where the problem
        ocurred.
        """
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
        """Test that a warning log message is created if the download file exists."""
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
        """Test that a warning log message is created if there are problems downloading.

        The log message should also contain the line number and contents of the line
        that caused the error.
        """
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


@pytest.mark.usefixtures("_mock_get")
class TestDownload:
    """Define tests related to wikiget.dl.download."""

    @pytest.fixture()
    def mock_file(self) -> File:
        """Create a mock File object to test against.

        :return: mock File object
        :rtype: File
        """
        file = File(name="Example.jpg")
        file.image = Mock()
        file.image.imageinfo = {
            "url": "https://upload.wikimedia.org/wikipedia/commons/a/a9/Example.jpg",
            "size": 9022,
            "sha1": "d01b79a6781c72ac9bfff93e5e2cfbeef4efc840",
        }
        file.image.site = MagicMock(Site)
        file.image.site.host = "commons.wikimedia.org"
        file.image.site.connection = requests.Session()
        return file

    @patch("wikiget.dl.verify_hash")
    def test_download(
        self,
        mock_verify_hash: MagicMock,
        mock_file: File,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that the correct log messages are created when downloading a file.

        There should be a series of info-level messages containing the filename, size,
        site name, actual URL, and SHA1 hash, along with a message noting the successful
        download.
        """
        caplog.set_level(logging.INFO)

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

    @patch("wikiget.dl.verify_hash")
    def test_download_with_output(
        self,
        mock_verify_hash: MagicMock,
        mock_file: File,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test that the correct log messages are created when downloading a file.

        When an output name is specified, the log messages should reflect that.
        """
        caplog.set_level(logging.INFO)

        tmp_file = mock_file.dest
        mock_verify_hash.return_value = "d01b79a6781c72ac9bfff93e5e2cfbeef4efc840"

        args = parse_args(["-o", str(tmp_file), "File:Example.jpg"])
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
        """Test that a dry run creates a log message saying so."""
        caplog.set_level(logging.INFO)

        args = parse_args(["-n", "File:Example.jpg"])
        errors = download(mock_file, args)

        # ignore first two log records since we tested for those earlier
        assert caplog.record_tuples[2:] == [
            ("wikiget.dl", logging.WARNING, "[Example.jpg] Dry run; download skipped"),
        ]
        assert errors == 0

    @patch("pathlib.Path.open")
    def test_download_os_error(
        self, mock_open: MagicMock, mock_file: File, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test what happens when an OSError is raised during download.

        If the downloaded file cannot be created, an error log message should be created
        with details on the exception.
        """
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

    @patch("wikiget.dl.verify_hash")
    def test_download_verify_os_error(
        self,
        mock_verify_hash: MagicMock,
        mock_file: File,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test what happens when an OSError is raised during verification.

        If the downloaded file cannot be read in order to calculate its hash, an error
        log message should be created with details on the exception.
        """
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

    @patch("wikiget.dl.verify_hash")
    def test_download_verify_hash_mismatch(
        self,
        mock_verify_hash: MagicMock,
        mock_file: File,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test what happens when the downloaded file hash and server hash don't match.

        An error log message should be created if there's a hash mismatch.
        """
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
        """Test that a warning message is logged if no file info was returned."""
        mock_file.image.imageinfo = {}

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
