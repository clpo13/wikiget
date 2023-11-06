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
from unittest.mock import MagicMock, patch, sentinel

import pytest
from mwclient import InvalidResponse
from requests import ConnectionError, HTTPError

from wikiget import DEFAULT_SITE
from wikiget.client import connect_to_site, query_api
from wikiget.wikiget import parse_args


class TestConnectSite:
    # this message is logged when the level is at INFO or below
    info_msg = f"Connecting to {DEFAULT_SITE}"

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
            ("wikiget.client", logging.INFO, self.info_msg),
        ]

    def test_connect_to_site_connection_error(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """
        The connect_to_site function should log the correct messages if a
        ConnectionError exception is raised.
        """
        caplog.set_level(logging.DEBUG)
        args = parse_args(["File:Example.jpg"])
        with patch("wikiget.client.Site") as mock_site:
            mock_site.side_effect = ConnectionError("connection error message")
            with pytest.raises(ConnectionError):
                _ = connect_to_site(DEFAULT_SITE, args)
        assert "Could not connect to specified site" in caplog.text
        assert caplog.record_tuples == [
            ("wikiget.client", logging.INFO, self.info_msg),
            ("wikiget.client", logging.ERROR, "Could not connect to specified site"),
            ("wikiget.client", logging.DEBUG, "connection error message"),
        ]

    def test_connect_to_site_http_error(self, caplog: pytest.LogCaptureFixture) -> None:
        """
        The connect_to_site function should log the correct messages if an HTTPError
        exception is raised.
        """
        caplog.set_level(logging.DEBUG)
        args = parse_args(["File:Example.jpg"])
        with patch("wikiget.client.Site") as mock_site:
            mock_site.side_effect = HTTPError
            with pytest.raises(HTTPError):
                _ = connect_to_site(DEFAULT_SITE, args)
        assert caplog.record_tuples == [
            ("wikiget.client", logging.INFO, self.info_msg),
            (
                "wikiget.client",
                logging.ERROR,
                "Could not find the specified wiki's api.php. "
                "Check the value of --path.",
            ),
            ("wikiget.client", logging.DEBUG, ""),
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


class TestQueryApi:
    def test_query_api(self) -> None:
        """
        The query_api function should return an Image object when given a name and a
        valid Site.
        """
        # These mock objects represent Site and Image objects that the real program
        # would have created using the MediaWiki API. The Site.images attribute is
        # normally populated during Site init, but since we're not doing that, a mock
        # dict is created for query_api to parse.
        mock_site = MagicMock()
        mock_site.images = {"Example.jpg": sentinel.mock_image}

        image = query_api("Example.jpg", mock_site)
        assert image == sentinel.mock_image
