# -*- coding: utf-8 -*-
# ###
# Copyright (c) 2013, Rice University
# This software is subject to the provisions of the GNU Affero General
# Public License version 3 (AGPLv3).
# See LICENCE.txt for details.
# ###
"""Helpers Used in Multiple Views."""
import logging

import psycopg2
import psycopg2.extras
from pyramid import httpexceptions
from pyramid.threadlocal import get_current_registry

from .. import config
from ..database import SQL

from ..utils import portaltype_to_mimetype

logger = logging.getLogger('cnxarchive')


# #################### #
#   Helper functions   #
# #################### #


def get_uuid(shortid):
    settings = get_current_registry().settings
    with psycopg2.connect(settings[config.CONNECTION_STRING]) as db_connection:
        with db_connection.cursor() as cursor:
            cursor.execute(SQL['get-module-uuid'], {'id': shortid})
            try:
                return cursor.fetchone()[0]
            except (TypeError, IndexError,):  # None returned
                logger.debug("Short ID was supplied and could not discover "
                             "UUID.")
                raise httpexceptions.HTTPNotFound()


def get_latest_version(uuid_):
    settings = get_current_registry().settings
    with psycopg2.connect(settings[config.CONNECTION_STRING]) as db_connection:
        with db_connection.cursor() as cursor:
            cursor.execute(SQL['get-module-versions'], {'id': uuid_})
            try:
                return cursor.fetchone()[0]
            except (TypeError, IndexError,):  # None returned
                raise httpexceptions.HTTPNotFound()


def get_content_metadata(id, version, cursor):
    """Return metadata related to the content from the database."""
    # Do the module lookup
    args = dict(id=id, version=version)
    # FIXME We are doing two queries here that can hopefully be
    #       condensed into one.
    cursor.execute(SQL['get-module-metadata'], args)
    try:
        result = cursor.fetchone()[0]
        # version is what we want to return, but in the sql we're using
        # current_version because otherwise there's a "column reference is
        # ambiguous" error
        result['version'] = result.pop('current_version')

        # FIXME We currently have legacy 'portal_type' names in the database.
        #       Future upgrades should replace the portal type with a mimetype
        #       of 'application/vnd.org.cnx.(module|collection|folder|<etc>)'.
        #       Until then we will do the replacement here.
        result['mediaType'] = portaltype_to_mimetype(result['mediaType'])

        return result
    except (TypeError, IndexError,):  # None returned
        raise httpexceptions.HTTPNotFound()
