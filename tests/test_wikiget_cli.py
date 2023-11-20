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

"""Define tests related to the wikiget.wikiget module."""

from __future__ import annotations

import logging
from unittest.mock import MagicMock, patch

import pytest

from wikiget import USER_AGENT, __version__
from wikiget.wikiget import cli


@patch("wikiget.wikiget.process_download")
class TestWikigetCli:
    """Define tests related to wikiget.wikiget.cli."""

    def test_cli_no_args(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """If no arguments are passed, the program should exit with code 2."""
        with monkeypatch.context() as m:
            m.setattr("sys.argv", ["wikiget"])

            with pytest.raises(SystemExit) as e:
                cli()

        assert e.value.code == 2

    def test_cli_completed_successfully(
        self, mock_process_download: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """If everything is successful, the program should exit with code 0."""
        with monkeypatch.context() as m:
            # pretend process_download was successful
            mock_process_download.return_value = 0
            m.setattr("sys.argv", ["wikiget", "File:Example.jpg"])

            with pytest.raises(SystemExit) as e:
                cli()

        assert e.value.code == 0

    def test_cli_completed_with_problems(
        self, mock_process_download: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """If there are problems during execution, the exit code should be 1."""
        with monkeypatch.context() as m:
            # pretend process_download was unsuccessful
            mock_process_download.return_value = 1
            m.setattr("sys.argv", ["wikiget", "File:Example.jpg"])

            with pytest.raises(SystemExit) as e:
                cli()

        assert e.value.code == 1

    def test_cli_logs(
        self,
        mock_process_download: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """When program execution starts, it should create the right log messages.

        There should be an info log record with the program version as well as a debug
        record with the user agent we're sending to the API.
        """
        with monkeypatch.context() as m:
            # pretend process_download was successful
            mock_process_download.return_value = 0
            m.setattr("sys.argv", ["wikiget", "File:Example.jpg"])

            with pytest.raises(SystemExit):
                cli()

        assert caplog.record_tuples == [
            (
                "wikiget.wikiget",
                logging.INFO,
                f"Starting download session using wikiget {__version__}",
            ),
            (
                "wikiget.wikiget",
                logging.DEBUG,
                f"User agent: {USER_AGENT}",
            ),
        ]

    def test_cli_interrupt(
        self,
        mock_process_download: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Test what happens when KeyboardInterrupt is raised during processing.

        A critical log message should be printed and the exit code should be 130.
        """
        with monkeypatch.context() as m:
            mock_process_download.side_effect = KeyboardInterrupt
            m.setattr("sys.argv", ["wikiget", "File:Example.jpg"])

            with pytest.raises(SystemExit) as e:
                cli()

        assert e.value.code == 130
        # ignore the first two messages, since they're tested elsewhere
        assert caplog.record_tuples[2] == (
            "wikiget.wikiget",
            logging.CRITICAL,
            "Interrupted by user",
        )
