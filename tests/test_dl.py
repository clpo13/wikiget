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

from pathlib import Path

import pytest

from wikiget.dl import prep_download
from wikiget.wikiget import construct_parser


# TODO: don't hit the actual API when doing tests
class TestPrepDownload:
    @pytest.mark.skip(reason="skip tests that query a live API")
    def test_prep_download(self) -> None:
        """
        The prep_download function should create a file object.
        """
        args = construct_parser().parse_args(["File:Example.jpg"])
        file = prep_download(args.FILE, args)
        assert file is not None

    def test_prep_download_with_existing_file(self, tmp_path: Path) -> None:
        """
        Attempting to download a file with the same destination name as an existing file
        should raise a FileExistsError.
        """
        tmp_file = tmp_path / "File:Example.jpg"
        tmp_file.write_text("nothing")
        args = construct_parser().parse_args(["File:Example.jpg", "-o", str(tmp_file)])
        with pytest.raises(FileExistsError):
            _ = prep_download(args.FILE, args)
