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

"""Define tests related to the wikiget.client module."""

import logging
from unittest.mock import MagicMock, patch, sentinel

import pytest
from mwclient import APIError, InvalidResponse
from requests import ConnectionError, HTTPError

from wikiget import DEFAULT_SITE
from wikiget.client import connect_to_site, query_api
from wikiget.wikiget import parse_args


class TestConnectSite:
    """Define tests related to wikiget.client.connect_to_site."""

    # this message is logged when the level is at INFO or below;
    # defined here for ease of maintenance
    info_msg = f"Connecting to {DEFAULT_SITE}"

    def test_connect_to_site(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that an info log message is created with the name of the site."""
        caplog.set_level(logging.INFO)
        args = parse_args(["File:Example.jpg"])

        with patch("wikiget.client.Site"):
            _ = connect_to_site(DEFAULT_SITE, args)

        assert caplog.record_tuples == [
            ("wikiget.client", logging.INFO, self.info_msg),
        ]

    def test_connect_to_site_with_creds(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that an info log message is created when credentials are used.

        If a username and password are provided, connect_to_site should use them to
        log in to the site.
        """
        caplog.set_level(logging.INFO)
        args = parse_args(["-u", "username", "-p", "password", "File:Example.jpg"])

        with patch("wikiget.client.Site"):
            _ = connect_to_site(DEFAULT_SITE, args)

        # TODO: it should be possible to test if Site.login was called, making the log
        # message unnecessary
        assert caplog.record_tuples[1] == (
            "wikiget.client",
            logging.INFO,
            "Attempting to authenticate with credentials",
        )

    def test_connect_to_site_connection_error(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Test that the correct log messages are created if ConnectionError is raised.

        In addition to the info-level site connection message, there should be error
        and debug level messages with details about the problem.
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
        """Test that the correct log messages are created if HTTPError is raised.

        In addition to the info-level site connection message, there should be error
        and debug level messages with details about the problem.
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
        """Test that log messages are created if other exceptions are raised.

        When an exception other than ConnectionError or HTTPError is raised, an
        error-level log message should be created.
        """
        args = parse_args(["File:Example.jpg"])

        with patch("wikiget.client.Site") as mock_site:
            mock_site.side_effect = InvalidResponse
            with pytest.raises(InvalidResponse):
                _ = connect_to_site("commons.wikimedia.org", args)

            for record in caplog.records:
                assert record.levelname == "ERROR"


class TestQueryApi:
    """Define tests related to wikiget.client.query_api."""

    def test_query_api(self) -> None:
        """Test that query_api returns the expected Image object."""
        # These mock objects represent Site and Image objects that the real program
        # would have created using the MediaWiki API. The Site.images attribute is
        # normally populated during Site init, but since we're not doing that, a mock
        # dict is created for query_api to parse.
        mock_site = MagicMock()
        mock_site.images = {"Example.jpg": sentinel.mock_image}

        image = query_api("Example.jpg", mock_site)

        assert image == sentinel.mock_image

    def test_query_api_error(self, caplog: pytest.LogCaptureFixture) -> None:
        """Test that the correct log messages are created when APIError is raised.

        The query_api function should log an error if an APIError exception is caught,
        as well as debug log entries with additional information about the error.
        """
        caplog.set_level(logging.DEBUG)

        mock_site = MagicMock()
        mock_site.images = MagicMock()
        # Normally, APIError is raised during the processing of the API call that
        # creates the site.images attribute. Since we're faking all of that, the
        # exception needs to be raised elsewhere, so that it's caught when query_api
        # tries to read the items in site.images.
        mock_site.images.__getitem__.side_effect = APIError(
            "error code", "error info", "error kwargs"
        )

        with pytest.raises(APIError):
            _ = query_api("Example.jpg", mock_site)

        assert caplog.record_tuples == [
            (
                "wikiget.client",
                logging.ERROR,
                "Access denied. Try providing credentials with "
                "--username and --password.",
            ),
            ("wikiget.client", logging.DEBUG, "error code"),
            ("wikiget.client", logging.DEBUG, "error info"),
            ("wikiget.client", logging.DEBUG, "error kwargs"),
        ]
