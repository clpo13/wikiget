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

import logging
import sys
from argparse import Namespace
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from mwclient import APIError, InvalidResponse, LoginError
from requests import ConnectionError, HTTPError
from tqdm import tqdm

import wikiget
from wikiget.client import connect_to_site, query_api
from wikiget.exceptions import ParseError
from wikiget.file import File
from wikiget.logging import FileLogAdapter
from wikiget.parse import get_dest, read_batch_file
from wikiget.validations import verify_hash

logger = logging.getLogger(__name__)


def prep_download(dl: str, args: Namespace) -> File:
    file = get_dest(dl, args)

    # check if the destination file already exists; don't overwrite unless the user says
    if Path(file.dest).is_file() and not args.force:
        msg = f"[{file.dest}] File already exists; skipping download (use -f to force)"
        raise FileExistsError(msg)

    site = connect_to_site(file.site, args)
    file.image = query_api(file.name, site)
    return file


def process_download(args: Namespace) -> int:
    exit_code = 0

    if args.batch:
        # batch download mode
        errors = batch_download(args)
        if errors:
            # return non-zero exit code if any problems were encountered, even if some
            # downloads completed successfully
            logger.warning(
                "%i problem%s encountered during batch processing",
                errors,
                "s"[: errors ^ 1],
            )
            exit_code = 1  # completed with errors
    else:
        # single download mode
        try:
            file = prep_download(args.FILE, args)
        except ParseError as e:
            logger.error(e)
            exit_code = 1
        except FileExistsError as e:
            logger.warning(e)
            exit_code = 1
        except (ConnectionError, HTTPError, InvalidResponse, LoginError, APIError):
            exit_code = 1
        else:
            errors = download(file, args)
            if errors:
                exit_code = 1  # completed with errors
    return exit_code


def batch_download(args: Namespace) -> int:
    errors = 0

    # parse batch file
    try:
        dl_dict = read_batch_file(args.FILE)
    except OSError as e:
        logger.error("File could not be read: %s", str(e))
        sys.exit(1)

    # TODO: validate file contents before download process starts
    with ThreadPoolExecutor(max_workers=args.threads) as executor:
        futures = []
        for line_num, line in dl_dict.items():
            # keep track of batch file line numbers for debugging/logging purposes
            logger.info("Processing '%s' at line %i", line, line_num)
            try:
                file = prep_download(line, args)
            except ParseError as e:
                logger.warning("%s (line %i)", str(e), line_num)
                errors += 1
                continue
            except FileExistsError as e:
                logger.warning(e)
                errors += 1
                continue
            except (ConnectionError, HTTPError, InvalidResponse, LoginError, APIError):
                logger.warning(
                    "Unable to download '%s' (line %i) due to an error",
                    line,
                    line_num,
                )
                errors += 1
                continue
            future = executor.submit(download, file, args)
            futures.append(future)
        # wait for downloads to finish
        for future in futures:
            errors += future.result()
    return errors


def download(f: File, args: Namespace) -> int:
    file = f.image
    filename = f.name
    dest = f.dest
    site = file.site

    errors = 0

    adapter = FileLogAdapter(logger, {"filename": filename})

    if file.exists:
        # file exists either locally or at a common repository, like Wikimedia Commons
        file_url = file.imageinfo["url"]
        file_size = file.imageinfo["size"]
        file_sha1 = file.imageinfo["sha1"]

        filename_log = f"Downloading '{filename}' ({file_size} bytes) from {site.host}"
        if args.output:
            filename_log += f" to '{dest}'"
        adapter.info(filename_log)
        adapter.info(f"{file_url}")

        if args.dry_run:
            adapter.warning("Dry run; download skipped")
            return errors

        try:
            with tqdm(
                desc=dest,
                leave=args.verbose >= wikiget.STD_VERBOSE,
                total=file_size,
                unit="B",
                unit_scale=True,
                unit_divisor=wikiget.CHUNKSIZE,
            ) as progress_bar, Path(dest).open("wb") as fd:
                # download the file using the existing Site session
                res = site.connection.get(file_url, stream=True)
                for chunk in res.iter_content(wikiget.CHUNKSIZE):
                    fd.write(chunk)
                    progress_bar.update(len(chunk))
        except OSError as e:
            adapter.error(f"File could not be written: {e}")
            errors += 1
            return errors

        # verify file integrity and log the details
        try:
            dl_sha1 = verify_hash(dest)
        except OSError as e:
            adapter.error(f"File downloaded but could not be verified: {e}")
            errors += 1
            return errors

        adapter.info(f"Remote file SHA1 is {file_sha1}")
        adapter.info(f"Local file SHA1 is {dl_sha1}")
        if dl_sha1 == file_sha1:
            adapter.info("Hashes match!")
            # at this point, we've successfully downloaded the file
            success_log = f"'{filename}' downloaded"
            if args.output:
                success_log += f" to '{dest}'"
            adapter.info(success_log)
        else:
            adapter.error("Hash mismatch! Downloaded file may be corrupt.")
            errors += 1

    else:
        # no file information returned
        adapter.warning("Target does not appear to be a valid file")
        errors += 1

    return errors
