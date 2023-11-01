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
from unittest.mock import MagicMock, patch

import pytest

from wikiget import USER_AGENT
from wikiget.client import connect_to_site, query_api
from wikiget.wikiget import construct_parser


# TODO: don't hit the actual API when doing tests
class TestQueryApi:
    @patch("mwclient.Site.__new__")
    def test_connect_to_site(
        self, mock_site: MagicMock, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        The connect_to_site function should create a debug log message recording the
        name of the site we're connecting to.
        """
        caplog.set_level(logging.DEBUG)
        mock_site.return_value = MagicMock()
        args = construct_parser(["File:Example.jpg"])
        _ = connect_to_site("commons.wikimedia.org", args)
        assert mock_site.called
        assert "Connecting to commons.wikimedia.org" in caplog.text

    @pytest.mark.skip(reason="skip tests that query a live API")
    def test_query_api(self, caplog: pytest.LogCaptureFixture) -> None:
        """
        The query_api function should create a debug log message containing the user
        agent we're sending to the API.
        """
        caplog.set_level(logging.DEBUG)
        args = construct_parser(["File:Example.jpg"])
        site = connect_to_site("commons.wikimedia.org", args)
        _ = query_api("Example.jpg", site)
        assert USER_AGENT in caplog.text
