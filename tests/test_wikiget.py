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

from unittest.mock import MagicMock, patch

import pytest

from wikiget import USER_AGENT
from wikiget.wikiget import main


def test_main_no_params(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setattr("sys.argv", ["wikiget"])
    with pytest.raises(SystemExit) as e:
        main()
    assert e.value.code == 2


@patch("wikiget.wikiget.process_download")
def test_main_success(
    mock_process_download: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("sys.argv", ["wikiget", "File:Example.jpg"])
    mock_process_download.return_value = 0
    with pytest.raises(SystemExit) as e:
        main()
    assert mock_process_download.called
    assert e.value.code == 0


@patch("wikiget.wikiget.process_download")
def test_main_failure(
    mock_process_download: MagicMock, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("sys.argv", ["wikiget", "File:Example.jpg"])
    mock_process_download.return_value = 1
    with pytest.raises(SystemExit) as e:
        main()
    assert mock_process_download.called
    assert e.value.code == 1


@patch("wikiget.wikiget.process_download")
def test_main_logs(
    mock_process_download: MagicMock,
    monkeypatch: pytest.MonkeyPatch,
    caplog: pytest.LogCaptureFixture,
) -> None:
    monkeypatch.setattr("sys.argv", ["wikiget", "File:Example.jpg"])
    mock_process_download.return_value = 0
    with pytest.raises(SystemExit):
        main()
    assert mock_process_download.called
    assert USER_AGENT in caplog.text
