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

"""Define a File class for representing individual files to be downloaded."""

from __future__ import annotations

from pathlib import Path
from typing import TYPE_CHECKING

from wikiget import DEFAULT_SITE

if TYPE_CHECKING:
    from mwclient.image import Image


class File:
    """A file object."""

    def __init__(
        self, name: str, dest: str = "", site: str = "", image: Image = None
    ) -> None:
        """Initialize a new file with the given parameters.

        Only the name is required. If a destination isn't specified, the provided name
        will be used as the output name, and if no site is given, the default site will
        be used (commons.wikimedia.org).

        Args:
            name (str): name of the file
            dest (str, optional): output name of the file; defaults to the value given
                to name
            site (str, optional): name of the site hosting the file; defaults to the
                global default site
            image (mwclient.image.Image): mwclient image object retrieved from the host
                site
        """
        self.name = name
        self.dest = Path(dest) if dest else Path(name)
        self.site = site if site else DEFAULT_SITE
        self.image = image

    def __eq__(self, other: object) -> bool:
        """Compare this File object with another for equality.

        Args:
            other (wikiget.file.File): another File to compare

        Returns:
            bool: True if the Files are equal and False otherwise
        """
        if not isinstance(other, File):
            return NotImplemented
        return (
            self.name == other.name
            and self.dest == other.dest
            and self.site == other.site
            and self.image == other.image
        )

    def __str__(self) -> str:
        """Return a basic string representation of this class, for str().

        Returns:
            str: string form of the class
        """
        return str(self.__dict__)

    def __repr__(self) -> str:
        """Return a formal string representation of this class, for repr().

        Returns:
            str: string form of the class
        """
        attr_list = [self.name, self.dest, self.site]
        return '{}("{}", {})'.format(
            self.__class__.__name__,
            '", "'.join(map(str, attr_list)),
            self.image,
        )
