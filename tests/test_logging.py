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

import logging

import pytest

from wikiget.logging import FileLogAdapter, configure_logging
from wikiget.wikiget import construct_parser


@pytest.fixture
def create_logger():
    def _create_logger(args):
        configure_logging(args.verbose, args.logfile, quiet=args.quiet)
        return logging.getLogger()
    return _create_logger


def test_custom_log_adapter(create_logger, caplog):
    args = construct_parser().parse_args(["File:Example.jpg"])
    logger = create_logger(args)
    adapter = FileLogAdapter(logger, {"filename": "Example.jpg"})
    adapter.warning("test log")
    assert "[Example.jpg] test log" in caplog.text


def test_default_logging(create_logger):
    args = construct_parser().parse_args(["File:Example.jpg"])
    logger = create_logger(args)
    assert logger.level == logging.WARNING


@pytest.mark.xfail(reason="logging level can't be changed mid-test")
def test_verbose_logging(create_logger):
    args = construct_parser().parse_args(["File:Example.jpg", "-v"])
    logger = create_logger(args)
    assert logger.level == logging.INFO


@pytest.mark.xfail(reason="logging level can't be changed mid-test")
def test_very_verbose_logging(create_logger):
    args = construct_parser().parse_args(["File:Example.jpg", "-vv"])
    logger = create_logger(args)
    assert logger.level == logging.DEBUG


@pytest.mark.xfail(reason="logging level can't be changed mid-test")
def test_quiet_logging(create_logger):
    args = construct_parser().parse_args(["File:Example.jpg", "-q"])
    logger = create_logger(args)
    assert logger.level == logging.ERROR
