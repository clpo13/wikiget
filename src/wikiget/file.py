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
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from mwclient.image import Image

from wikiget import DEFAULT_SITE


class File:
    """A file object.

    Represents a file with the attributes name, destination, host site, and
    mwclient.image.Image object as retrieved from the host site.
    """

    def __init__(self, name: str, dest: str = "", site: str = "") -> None:
        """Initialize a new file.

        The file name is required. If a destination and/or site are provided, those will
        be used instead of the defaults.

        :param name: name of the file
        :type name: str
        :param dest: output destination of the file, if different from the name; if not
            specified, defaults to the name
        :type dest: str, optional
        :param site: name of the site hosting the file; if not specified, defaults to
            the global default site
        :type site: str, optional
        """
        self.image: Image = None
        self.name = name
        self.dest = Path(dest) if dest else Path(name)
        self.site = site if site else DEFAULT_SITE

    def __eq__(self, other: object) -> bool:
        """Compare this File object with another for equality.

        :param other: another File to compare
        :type other: File
        :return: True if the Files are equal and False otherwise
        :rtype: bool
        """
        if not isinstance(other, File):
            return NotImplemented
        return (
            self.image == other.image
            and self.name == other.name
            and self.dest == other.dest
            and self.site == other.site
        )
