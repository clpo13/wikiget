# wikiget - CLI tool for downloading files from Wikimedia sites
# Copyright (C) 2018-2023 Cody Logan and contributors
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

"""A tool for downloading files from MediaWiki sites.

Wikiget is similar in conception to download tools like wget, but wikiget can use the
name of the file or the URL of its description page to get the actual file's URL and
download it. Additionally, it can download multiple files at once by reading the targets
from a given text file.

Further documentation can be found in the accompanying README.md file or at
<https://github.com/clpo13/wikiget>.

Basic usage::

    wikiget [options] FILE
    wikiget [options] [-a|--batch] BATCHFILE

Examples::

    wikiget File:Example.jpg
    wikiget --site en.wikipedia.org File:Example.jpg
    wikiget https://en.wikipedia.org/wiki/File:Example.jpg -o output.jpg
    wikiget -a -j4 batch.txt

"""

from mwclient import __version__ as mwclient_version

from wikiget.version import __version__

# set some global constants
BLOCKSIZE = 65536
CHUNKSIZE = 1024
DEFAULT_SITE = "commons.wikimedia.org"
DEFAULT_PATH = "/w/"
USER_AGENT = (
    f"wikiget/{__version__} (https://github.com/clpo13/wikiget) "
    f"mwclient/{mwclient_version}"
)
STD_VERBOSE = 1
VERY_VERBOSE = 2
