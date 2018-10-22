#!/usr/bin/env python3

"""Scrapes the ABC iDBL and uploads content to database.

    Last Update: 2018-Oct-21

    Copyright (c) Notices
        2017	Joshua R. Torrance	<studybuffalo@studybuffalo.com>

    This program is free software: you can redistribute it and/or
    modify it under the terms of the GNU General Public License as
    published by the Free Software Foundation, either version 3 of
    the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not,
    see <http://www.gnu.org/licenses/>.
"""

import configparser
import logging
import logging.config
import sys

import sentry_sdk
from unipath import Path

from modules import configuration, manage


# Connect to the external configuration file
CONFIG_PATH = Path(sys.argv[1])
CONFIG = configparser.ConfigParser()
CONFIG.read(CONFIG_PATH)

# Set up logging & Sentry
logging.config.dictConfig(configuration.LOGGING_DICT)
LOG = logging.getLogger(__name__)

sentry_sdk.init(CONFIG['sentry_dsn'])

manage.run_application(CONFIG)
