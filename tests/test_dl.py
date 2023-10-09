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

# import logging
import pytest

# from wikiget import USER_AGENT
from wikiget.wikiget import construct_parser
# from wikiget.dl import get_dest, query_api, prep_download
from wikiget.dl import get_dest


class TestGetDest:
    parser = construct_parser()

    def test_get_dest_with_filename(self):
        args = self.parser.parse_args(["File:Example.jpg"])
        filename, dest, site_name = get_dest(args.FILE, args)
        assert filename == "Example.jpg"
        assert dest == "Example.jpg"
        assert site_name == "commons.wikimedia.org"

    def test_get_dest_with_url(self):
        args = self.parser.parse_args([
            "https://en.wikipedia.org/wiki/File:Example.jpg",
        ])
        filename, dest, site_name = get_dest(args.FILE, args)
        assert filename == "Example.jpg"
        assert dest == "Example.jpg"
        assert site_name == "en.wikipedia.org"

    def test_get_dest_with_bad_filename(self):
        args = self.parser.parse_args(["Example.jpg"])
        with pytest.raises(SystemExit):
            filename, dest, site_name = get_dest(args.FILE, args)

    def test_get_dest_with_different_site(self, caplog):
        args = self.parser.parse_args([
            "https://commons.wikimedia.org/wiki/File:Example.jpg",
            "--site",
            "commons.wikimedia.org",
        ])
        filename, dest, site_name = get_dest(args.FILE, args)
        assert "target is a URL, ignoring site specified with --site" in caplog.text


# TODO: don't hit the actual API when doing tests
# class TestQueryApi:
#     parser = construct_parser()
#
#     def test_query_api(self, caplog):
#         caplog.set_level(logging.DEBUG)
#         args = self.parser.parse_args(["File:Example.jpg"])
#         file, site = query_api("Example.jpg", "commons.wikimedia.org", args)
#         assert USER_AGENT in caplog.text
#
#
# class TestPrepDownload():
#     parser = construct_parser()
#
#     def test_prep_download(self):
#         args = self.parser.parse_args(["File:Example.jpg"])
#         file = prep_download(args.FILE, args)
#         assert file is not None
