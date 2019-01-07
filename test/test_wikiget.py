# -*- coding: utf-8 -*-
"""wikiget
Simple wget clone for downloading files from Wikimedia sites.
Copyright (C) 2018 Cody Logan; licensed GPLv3+
SPDX-License-Identifier: GPL-3.0-or-later
"""

from wikiget import wikiget


def test_invalid_site_input():
    invalid_input = ["example.com", "vim.wikia.com",
                     "en.wikipedia.com", "en.wikimpedia.org"]
    for i in invalid_input:
        site_match = wikiget.valid_site(i)
        assert site_match is None


def test_valid_site_input():
    valid_input = ["en.wikipedia.org", "commons.wikimedia.org",
                   "de.wikipedia.org", "meta.wikimedia.org"]
    for i in valid_input:
        site_match = wikiget.valid_site(i)
        assert site_match is not None


def test_file_regex():
    i = "File:Example.jpg"
    file_match = wikiget.valid_file(i)
    assert file_match.group(0)
    assert file_match.group(1) == "File:"
    assert file_match.group(2) == "Example.jpg"


def test_invalid_file_input():
    invalid_input = ["file:example", "example.jpg", "Foo Bar.gif",
                     "Fil:Example.jpg"]
    for i in invalid_input:
        file_match = wikiget.valid_file(i)
        assert file_match is None


def test_valid_file_input():
    valid_input = ["Image:example.jpg", "file:example.jpg", "File:example.file-01.jpg",
                   "File:ß handwritten sample.gif"]
    for i in valid_input:
        file_match = wikiget.valid_file(i)
        assert file_match is not None
