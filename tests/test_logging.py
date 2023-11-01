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
from pathlib import Path

from pytest import LogCaptureFixture

from wikiget.logging import FileLogAdapter, configure_logging
from wikiget.wikiget import parse_args

logger = logging.getLogger()


def test_custom_log_adapter(caplog: LogCaptureFixture) -> None:
    """
    The custom log adapter should prepend the filename to log messages.
    """
    args = parse_args(["File:Example.jpg"])
    configure_logging(args.verbose, args.logfile, quiet=args.quiet)
    adapter = FileLogAdapter(logger, {"filename": "Example.jpg"})
    adapter.warning("test log")
    assert "[Example.jpg] test log" in caplog.text


def test_file_logging(tmp_path: Path) -> None:
    """
    Logging to a file should create the file in the specified location.
    """
    logfile_location = tmp_path / "test.log"
    args = parse_args(["File:Example.jpg", "-l", str(logfile_location)])
    configure_logging(args.verbose, args.logfile, quiet=args.quiet)
    assert logfile_location.is_file()


def test_default_logging() -> None:
    """
    The default log level should be set to WARNING.
    """
    args = parse_args(["File:Example.jpg"])
    configure_logging(args.verbose, args.logfile, quiet=args.quiet)
    # each call of configure_logging() adds a new handler to the logger, so we need to
    # grab the most recently added one to test
    handler = logger.handlers[-1]
    assert handler.level == logging.WARNING


def test_verbose_logging() -> None:
    """
    When -v is passed, the log level should be set to INFO.
    """
    args = parse_args(["File:Example.jpg", "-v"])
    configure_logging(args.verbose, args.logfile, quiet=args.quiet)
    handler = logger.handlers[-1]
    assert handler.level == logging.INFO


def test_very_verbose_logging() -> None:
    """
    When -vv is passed, the log level should be set to DEBUG.
    """
    args = parse_args(["File:Example.jpg", "-vv"])
    configure_logging(args.verbose, args.logfile, quiet=args.quiet)
    handler = logger.handlers[-1]
    assert handler.level == logging.DEBUG


def test_quiet_logging() -> None:
    """
    When -q is passed, the log level should be set to ERROR.
    """
    args = parse_args(["File:Example.jpg", "-q"])
    configure_logging(args.verbose, args.logfile, quiet=args.quiet)
    handler = logger.handlers[-1]
    assert handler.level == logging.ERROR
