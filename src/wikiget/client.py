# wikiget - CLI tool for downloading files from Wikimedia sites
# Copyright (C) 2018-2023 Cody Logan
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

"""Handle API calls (via mwclient) for site and image information."""

import logging
from argparse import Namespace

from mwclient import APIError, InvalidResponse, LoginError, Site
from mwclient.image import Image
from requests import ConnectionError, HTTPError

import wikiget

logger = logging.getLogger(__name__)


def connect_to_site(site_name: str, args: Namespace) -> Site:
    """Create and return a Site object using the given site name and CLI arguments.

    :param site_name: hostname of the site to connect to
    :type site_name: str
    :param args: command-line arguments and their values
    :type args: argparse.Namespace
    :return: a new Site object
    :rtype: mwclient.Site
    """
    logger.info("Connecting to %s", site_name)

    try:
        # connect to site and identify ourselves
        site = Site(site_name, path=args.path, clients_useragent=wikiget.USER_AGENT)
        if args.username and args.password:
            logger.info("Attempting to authenticate with credentials")
            site.login(args.username, args.password)
    except ConnectionError as e:
        # usually this means there is no such site, or there's no network connection,
        # though it could be a certificate problem
        logger.error("Could not connect to specified site")
        logger.debug(e)
        raise
    except HTTPError as e:
        # most likely a 403 forbidden or 404 not found error for api.php
        logger.error(
            "Could not find the specified wiki's api.php. Check the value of --path."
        )
        logger.debug(e)
        raise
    except (InvalidResponse, LoginError) as e:
        # InvalidResponse: site exists, but we couldn't communicate with the API
        # endpoint for some reason other than an HTTP error.
        # LoginError: missing or invalid credentials
        logger.error(e)
        raise

    return site


def query_api(filename: str, site: Site) -> Image:
    """Query the given Site for an Image object matching the given filename.

    Even if there's no file by that name on the site, an Image will still be returned,
    though with an empty imageinfo attribute.

    :param filename: name of the file to retrieve
    :type filename: str
    :param site: the Site object to query
    :type site: mwclient.Site
    :return: an Image object representing the requested file
    :rtype: mwclient.image.Image
    """
    try:
        # get info about the target file
        image = site.images[filename]
    except APIError as e:
        # an API error at this point likely means access is denied, which could happen
        # with a private wiki
        logger.error(
            "Access denied. Try providing credentials with --username and --password."
        )
        for i in e.args:
            logger.debug(i)
        raise

    return image
