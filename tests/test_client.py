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
from unittest.mock import patch

import pytest
from mwclient import InvalidResponse
from requests import ConnectionError, HTTPError

from wikiget import DEFAULT_SITE, USER_AGENT
from wikiget.client import connect_to_site, query_api
from wikiget.wikiget import parse_args


class TestClient:
    def test_connect_to_site(self, caplog: pytest.LogCaptureFixture) -> None:
        """
        The connect_to_site function should create an info log message recording the
        name of the site we're connecting to.
        """
        caplog.set_level(logging.INFO)
        args = parse_args(["File:Example.jpg"])
        with patch("wikiget.client.Site"):
            _ = connect_to_site(DEFAULT_SITE, args)
        assert caplog.record_tuples == [
            ("wikiget.client", logging.INFO, f"Connecting to {DEFAULT_SITE}"),
        ]

    def test_connect_to_site_connection_error(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        The connect_to_site function should log an error if a ConnectionError exception
        is raised.
        """
        caplog.set_level(logging.DEBUG)
        args = parse_args(["File:Example.jpg"])
        with patch("wikiget.client.Site") as mock_site:
            mock_site.side_effect = ConnectionError("connection error message")
            with pytest.raises(ConnectionError):
                _ = connect_to_site(DEFAULT_SITE, args)
        assert "Could not connect to specified site" in caplog.text
        assert caplog.record_tuples == [
            ("wikiget.client", logging.INFO, f"Connecting to {DEFAULT_SITE}"),
            ("wikiget.client", logging.ERROR, "Could not connect to specified site"),
            ("wikiget.client", logging.DEBUG, "connection error message"),
        ]

    def test_connect_to_site_http_error(self, caplog: pytest.LogCaptureFixture) -> None:
        """
        The connect_to_site function should log an error if an HTTPError exception
        is raised.
        """
        caplog.set_level(logging.DEBUG)
        args = parse_args(["File:Example.jpg"])
        with patch("wikiget.client.Site") as mock_site:
            mock_site.side_effect = HTTPError
            with pytest.raises(HTTPError):
                _ = connect_to_site(DEFAULT_SITE, args)
        assert caplog.record_tuples == [
            ("wikiget.client", logging.INFO, f"Connecting to {DEFAULT_SITE}"),
            (
                "wikiget.client",
                logging.ERROR,
                "Could not find the specified wiki's api.php. "
                "Check the value of --path.",
            ),
            ("wikiget.client", logging.DEBUG, "")
        ]

    def test_connect_to_site_other_error(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        The connect_to_site function should log an error if some other exception type
        is raised.
        """
        args = parse_args(["File:Example.jpg"])
        with patch("wikiget.client.Site") as mock_site:
            mock_site.side_effect = InvalidResponse
            with pytest.raises(InvalidResponse):
                _ = connect_to_site("commons.wikimedia.org", args)
            for record in caplog.records:
                assert record.levelname == "ERROR"

    # TODO: don't hit the actual API when doing tests
    @pytest.mark.skip(reason="skip tests that query a live API")
    def test_query_api(self, caplog: pytest.LogCaptureFixture) -> None:
        """
        The query_api function should create a debug log message containing the user
        agent we're sending to the API.
        """
        caplog.set_level(logging.DEBUG)
        args = parse_args(["File:Example.jpg"])
        site = connect_to_site("commons.wikimedia.org", args)
        _ = query_api("Example.jpg", site)
        assert USER_AGENT in caplog.text
