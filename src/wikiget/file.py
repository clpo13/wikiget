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


class File:
    def __init__(self, name, dest=""):
        """
        Initializes a new file with the specified name and an optional destination name.

        :param name: name of the file
        :type name: str
        :param dest: destination of the file, if different from the name; if not
            specified, defaults to the name
        :type dest: str, optional
        """
        self.object = None
        self.site = None
        self.name = name
        self.dest = dest if dest else name
