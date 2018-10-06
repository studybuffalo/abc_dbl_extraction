#!/usr/bin/env python3

"""Extracts and saves the Alberta Blue Cross iDBL.

    Last Update: 2018-Oct-05

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
from django.core.wsgi import get_wsgi_application
import logging
import logging.config
from modules import extraction, saving, database, debugging
import os
from raven import Client
import requests
import sys
import time
from unipath import Path

# APPLICATION SETUP
# Set up root path to generate absolute paths to files
root = Path(sys.argv[1])


# Get the config file
config = configparser.ConfigParser()
config.read(Path(root.parent, "config", "abc_dbl_extraction.cfg"))

# Set up logging & Sentry
client = Client(config.get("sentry", "dsn"))

log_config = Path(root.parent, "config", "abc_dbl_extraction_logging.cfg")
logging.config.fileConfig(log_config)
log = logging.getLogger(__name__)

# Collect debug status
debugData = debugging.get_debug_status(config)


# Setup robot details and create session
userAgent = config.get("robot", "user_agent", raw=True)
userFrom = config.get("robot", "from", raw=True)
crawlDelay = config.getfloat("misc", "crawl_delay")

session = requests.Session()
session.headers.update({"User-Agent": userAgent, "From": userFrom})

# Set up the connection to the Django models
# Connect to to Django database
djangoApp = config.get("django", "location")

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "studybuffalo.settings")
sys.path.append(djangoApp)
application = get_wsgi_application()

from drug_price_calculator.models import ( # pylint: disable=import-error
    ATC, Coverage, ExtraInformation, PTC, Price, SpecialAuthorization, 
    ATCDescriptions, SubsBSRF, SubsGeneric, SubsManufacturer, SubsPTC, 
    SubsUnit, PendBSRF, PendGeneric, PendManufacturer, PendPTC
) 

db = {
    "atc": ATC,
    "coverage": Coverage,
    "extra": ExtraInformation,
    "ptc": PTC,
    "price": Price,
    "special": SpecialAuthorization,
}

subs = {
    "atc": ATCDescriptions,
    "bsrf": SubsBSRF,
    "generic": SubsGeneric,
    "manufacturer": SubsGeneric,
    "ptc": SubsPTC,
    "unit": SubsUnit,
}

pend = {
    "bsrf": PendBSRF,
    "generic": PendGeneric,
    "manufacturer": PendManufacturer,
    "ptc": PendPTC,
}

parseData = database.collect_parse_data(subs)

# Collect locations to save all files
fileNames = saving.collect_file_paths(config)


log.info("ALBERTA BLUE CROSS DRUG BENEFIT LIST EXTRACTION TOOL STARTED")

# Create all save files
with open(fileNames.url.absolute(), "w") as fURL, \
        open(fileNames.price.absolute(), "w") as fPrice, \
        open(fileNames.coverage.absolute(), "w") as fCoverage, \
        open(fileNames.specialAuth.absolute(), "w") as fSpecial, \
        open(fileNames.ptc.absolute(), "w") as fPTC, \
        open(fileNames.atc.absolute(), "w") as fATC, \
        open(fileNames.extra.absolute(), "w") as fExtra:

    # Save all opened files into on object for easier use
    saveFiles = saving.organize_save_files(
        fURL, fileNames.html, fPrice, fCoverage, fSpecial, fPTC, fATC, fExtra
    )


    # Checking the robots.txt file for permission to crawl
    if debugData.scrapeUrl:
        can_crawl = extraction.get_permission(userAgent)
    else:
        # Program set to debug - use pre-set data
        can_crawl = True

    # If crawling is permitted, run the program
    if can_crawl:
        log.info("Permission granted to crawl site")
        log.info("Starting URL extraction")
        
        # Set the start and end for loop
        if debugData.scrapeUrl or debugData.scrapeData:
            start = int(sys.argv[2])
            end = int(sys.argv[3])
        else:
            # Program set to debug - use pre-set data
            urlList = debugData.urlList
            start = debugData.start
            end = debugData.end
            

        # Cycle through the range of URLs
        for i in range(start, end + 1):
            if debugData.uploadData:
                database.remove_data(db, i)
            
            # TEST FOR ACTIVE URL
            if debugData.scrapeUrl:
                # Apply delay before crawling URL
                time.sleep(crawlDelay)
            
                urlData = extraction.scrape_url(i, session)
            else:
                 # Program set to debug - use pre-set data
                urlData = urlList[i]


            # SCRAPE DATA FROM ACTIVE URLS
            if urlData.status == "active":
                if debugData.scrapeData:
                    # Apply delay before accessing page
                    time.sleep(crawlDelay)

                    content = extraction.collect_content(
                        urlData, session, parseData
                    )
                else:
                    # Program set to debug - use pre-saved data
                    content = extraction.debug_data(
                        urlData, debugData.htmlLoc, parseData, log
                    )
            else:
                content = None
            
            if content:
                if debugData.uploadData:
                    database.upload_data(content, db)
                
                # UPLOAD SUBS INFORMATION TO DATABASE
                if debugData.uploadSubs:
                    database.upload_sub(content, pend)
                
                # SAVE BACKUP COPY OF DATA
                saving.save_data(content, saveFiles)

log.info("ALBERTA BLUE CROSS DRUG BENEFIT LIST EXTRACTION COMPLETE")