# wikiget - CLI tool for downloading files from Wikimedia sites
# Copyright (C) 2018, 2019, 2020 Cody Logan and contributors
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

from mwclient import __version__ as mwclient_version

from .version import __version__ as wikiget_version

# set some global constants
BLOCKSIZE = 65536
DEFAULT_SITE = 'commons.wikimedia.org'
DEFAULT_PATH = '/w/'
USER_AGENT = ('wikiget/{} (https://github.com/clpo13/wikiget) '
              'mwclient/{}'.format(wikiget_version, mwclient_version))
