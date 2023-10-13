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
from wikiget.dl import prep_download, query_api
from wikiget.wikiget import construct_parser


# TODO: don't hit the actual API when doing tests
@pytest.mark.skip
class TestQueryApi:
    parser = construct_parser()

    def test_query_api(self, caplog):
        caplog.set_level(logging.DEBUG)
        args = self.parser.parse_args(["File:Example.jpg"])
        file, site = query_api("Example.jpg", "commons.wikimedia.org", args)
        assert USER_AGENT in caplog.text


@pytest.mark.skip
class TestPrepDownload:
    parser = construct_parser()

    def test_prep_download(self):
        args = self.parser.parse_args(["File:Example.jpg"])
        file = prep_download(args.FILE, args)
        assert file is not None
