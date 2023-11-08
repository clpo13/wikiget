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

from unittest.mock import MagicMock, patch

import pytest

from wikiget import USER_AGENT, __version__
from wikiget.wikiget import cli


class TestCli:
    """Define tests related to wikiget.wikiget.cli."""

    def test_cli_no_args(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """If no arguments are passed, the program should exit with code 2."""
        with monkeypatch.context() as m:
            m.setattr("sys.argv", ["wikiget"])
            with pytest.raises(SystemExit) as e:
                cli()
            assert e.value.code == 2

    @patch("wikiget.wikiget.process_download")
    def test_cli_completed_successfully(
        self, mock_process_download: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """If everything is successful, the program should exit with code 0."""
        # a successful call to process_download returns 0
        mock_process_download.return_value = 0

        with monkeypatch.context() as m:
            m.setattr("sys.argv", ["wikiget", "File:Example.jpg"])

            with pytest.raises(SystemExit) as e:
                cli()
            assert e.value.code == 0

    @patch("wikiget.wikiget.process_download")
    def test_cli_completed_with_problems(
        self, mock_process_download: MagicMock, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """If there are problems during execution, the exit code should be 1."""
        # an unsuccessful call to process_download returns 1
        mock_process_download.return_value = 1

        with monkeypatch.context() as m:
            m.setattr("sys.argv", ["wikiget", "File:Example.jpg"])

            with pytest.raises(SystemExit) as e:
                cli()
            assert e.value.code == 1

    @patch("wikiget.wikiget.process_download")
    def test_cli_logs(
        self,
        mock_process_download: MagicMock,
        monkeypatch: pytest.MonkeyPatch,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """When program execution starts, it should create the right log messages.

        There should be an info log record with the program version as well as a debug
        record with the program's user agent.
        """
        # a successful call to process_download returns 0
        mock_process_download.return_value = 0

        with monkeypatch.context() as m:
            m.setattr("sys.argv", ["wikiget", "File:Example.jpg"])

            with pytest.raises(SystemExit):
                cli()
            assert (
                f"Starting download session using wikiget {__version__}" in caplog.text
            )
            assert USER_AGENT in caplog.text
