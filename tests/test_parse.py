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

from wikiget.exceptions import ParseError
from wikiget.parse import get_dest
from wikiget.wikiget import construct_parser


class TestGetDest:
    parser = construct_parser()

    def test_get_dest_with_filename(self):
        args = self.parser.parse_args(["File:Example.jpg"])
        file = get_dest(args.FILE, args)
        assert file.name == "Example.jpg"
        assert file.dest == "Example.jpg"
        assert file.site == "commons.wikimedia.org"

    def test_get_dest_with_url(self):
        args = self.parser.parse_args(
            [
                "https://en.wikipedia.org/wiki/File:Example.jpg",
            ]
        )
        file = get_dest(args.FILE, args)
        assert file.name == "Example.jpg"
        assert file.dest == "Example.jpg"
        assert file.site == "en.wikipedia.org"

    def test_get_dest_with_bad_filename(self):
        args = self.parser.parse_args(["Example.jpg"])
        with pytest.raises(ParseError):
            _ = get_dest(args.FILE, args)

    def test_get_dest_with_different_site(self, caplog: pytest.LogCaptureFixture):
        args = self.parser.parse_args(
            [
                "https://commons.wikimedia.org/wiki/File:Example.jpg",
                "--site",
                "commons.wikimedia.org",
            ]
        )
        _ = get_dest(args.FILE, args)
        assert "Target is a URL, ignoring site specified with --site" in caplog.text
