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

import pytest

from wikiget import USER_AGENT, __version__
from wikiget.wikiget import cli


class TestCli:
    def test_cli_no_params(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("sys.argv", ["wikiget"])
        with pytest.raises(SystemExit) as e:
            cli()
        assert e.value.code == 2

    def test_cli_completed_successfully(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def mock_process_download(*args, **kwargs) -> int:  # noqa: ARG001
            """A successful call to process_download returns 0."""
            return 0

        with monkeypatch.context() as m:
            m.setattr("sys.argv", ["wikiget", "File:Example.jpg"])
            m.setattr("wikiget.wikiget.process_download", mock_process_download)

            with pytest.raises(SystemExit) as e:
                cli()
            assert e.value.code == 0

    def test_cli_completed_with_problems(self, monkeypatch: pytest.MonkeyPatch) -> None:
        def mock_process_download(*args, **kwargs) -> int:  # noqa: ARG001
            """An unsuccessful call to process_download returns 1."""
            return 1

        with monkeypatch.context() as m:
            m.setattr("sys.argv", ["wikiget", "File:Example.jpg"])
            m.setattr("wikiget.wikiget.process_download", mock_process_download)

            with pytest.raises(SystemExit) as e:
                cli()
            assert e.value.code == 1

    def test_cli_logs(
        self, monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
    ) -> None:
        def mock_process_download(*args, **kwargs) -> int:  # noqa: ARG001
            """A successful call to process_download returns 0."""
            return 0

        with monkeypatch.context() as m:
            m.setattr("sys.argv", ["wikiget", "File:Example.jpg"])
            m.setattr("wikiget.wikiget.process_download", mock_process_download)

            with pytest.raises(SystemExit):
                cli()
            assert (
                f"Starting download session using wikiget {__version__}" in caplog.text
            )
            assert USER_AGENT in caplog.text
