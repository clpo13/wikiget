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

from wikiget.dl import prep_download
from wikiget.wikiget import construct_parser


# TODO: don't hit the actual API when doing tests
@pytest.mark.skip(reason="skip tests that query a live API")
class TestPrepDownload:
    def test_prep_download(self) -> None:
        args = construct_parser().parser.parse_args(["File:Example.jpg"])
        file = prep_download(args.FILE, args)
        assert file is not None
