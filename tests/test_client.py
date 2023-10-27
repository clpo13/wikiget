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

import pytest

from wikiget import USER_AGENT
from wikiget.client import connect_to_site, query_api
from wikiget.wikiget import construct_parser


# TODO: don't hit the actual API when doing tests
@pytest.mark.skip(reason="skip tests that query a live API")
class TestQueryApi:
    args = construct_parser().parse_args(["File:Example.jpg"])

    def test_connect_to_site(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.DEBUG)
        _ = connect_to_site("commons.wikimedia.org", self.args)
        assert "Connecting to commons.wikimedia.org" in caplog.text

    def test_query_api(self, caplog: pytest.LogCaptureFixture) -> None:
        caplog.set_level(logging.DEBUG)
        site = connect_to_site("commons.wikimedia.org", self.args)
        _ = query_api("Example.jpg", site)
        assert USER_AGENT in caplog.text
