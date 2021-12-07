# wikiget - CLI tool for downloading files from Wikimedia sites
# Copyright (C) 2018-2021 Cody Logan
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

"""Python setuptools metadata and dependencies."""

from io import open
from os import path

from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))
with open(path.join(here, "README.md"), "r") as fr:
    long_description = fr.read()

version_file = {}
with open(path.join(here, "wikiget", "version.py"), "r") as fv:
    exec(fv.read(), version_file)

setup(
    name="wikiget",
    version=version_file["__version__"],
    author="Cody Logan",
    author_email="clpo13@gmail.com",
    description="CLI tool for downloading files from MediaWiki sites",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/clpo13/wikiget",
    keywords="commons download mediawiki wikimedia wikipedia",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v3 or later "
        "(GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Multimedia",
        "Topic :: Multimedia :: Graphics",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Video",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    install_requires=["mwclient>=0.10.0", "requests", "tqdm"],
    setup_requires=["pytest-runner"],
    tests_require=["pytest", "pytest-cov"],
    project_urls={
        "Bug Reports": "https://github.com/clpo13/wikiget/issues",
    },
    entry_points={
        "console_scripts": [
            "wikiget=wikiget.wikiget:main",
        ],
    },
)
