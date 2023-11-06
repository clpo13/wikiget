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
from unittest.mock import MagicMock, patch

import pytest
from mwclient import Site
from mwclient.image import Image

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
        mock_site = MagicMock(Site)
        mock_image = MagicMock(Image)

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
    def test_batch_download(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A successful batch download should not return any errors."""

        def mock_batch_download(*args, **kwargs):  # noqa: ARG001
            return 0

        with monkeypatch.context() as m:
            m.setattr("wikiget.dl.batch_download", mock_batch_download)

            args = parse_args(["-a", "batch.txt"])
            exit_code = process_download(args)
            assert exit_code == 0

    def test_batch_download_with_errors(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        Any errors during batch download should create a log message containing the
        number of errors and result in a non-zero exit code.
        """

        def mock_batch_download(*args, **kwargs):  # noqa: ARG001
            return 4

        with monkeypatch.context() as m:
            m.setattr("wikiget.dl.batch_download", mock_batch_download)

            args = parse_args(["-a", "batch.txt"])
            exit_code = process_download(args)
            assert exit_code == 1
            assert "4 problems encountered during batch processing" in caplog.text

    def test_single_download(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """A successful download should not return any errors."""

        def mock_download(*args, **kwargs):  # noqa: ARG001
            return 0

        def mock_prep_download(*args, **kwargs):  # noqa ARG001
            return File("Example.jpg")

        with monkeypatch.context() as m:
            m.setattr("wikiget.dl.download", mock_download)
            m.setattr("wikiget.dl.prep_download", mock_prep_download)

            args = parse_args(["File:Example.jpg"])
            exit_code = process_download(args)
            assert exit_code == 0

    def test_single_download_with_errors(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Any errors during download should result in a non-zero exit code."""

        def mock_download(*args, **kwargs):  # noqa: ARG001
            return 1

        def mock_prep_download(*args, **kwargs):  # noqa ARG001
            return File("Example.jpg")

        with monkeypatch.context() as m:
            m.setattr("wikiget.dl.download", mock_download)
            m.setattr("wikiget.dl.prep_download", mock_prep_download)

            args = parse_args(["File:Example.jpg"])
            exit_code = process_download(args)
            assert exit_code == 1
