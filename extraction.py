#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Extracts and saves the Alberta Blue Cross idbl.

    Last Update: 2017-Mar-30

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

    SHOULD YOU REQUIRE ANY EXCEPTIONS TO THIS LICENSE, PLEASE CONTACT 
    THE COPYRIGHT HOLDERS.
"""

import sys
from unipath import Path
import configparser
import python_logging
import datetime
from urllib import robotparser
import requests
import csv
import time
from modules import extraction, saving, database, website, debugging

def get_today():
    today = datetime.date.today()
    year = today.year
    month = "%02d" % today.month
    day = "%02d" % today.day
    
    today = "%s-%s-%s" % (year, month, day)
    
    return today

def get_permission():
    textURL = "https://www.ab.bluecross.ca/robots.txt"
    pageURL = "https://idbl.ab.bluecross.ca/idbl/load.do"

    robot = robotparser.RobotFileParser()
    robot.set_url(textURL)
    robot.read()
    
    can_crawl = robot.can_fetch(userAgent, pageURL)

    return can_crawl


log.info("ALBERTA BLUE CROSS DRUG BENEFIT LIST EXTRACTION TOOL STARTED")

# APPLICATION SETUP
# Set up root path to generate absolute paths to files
root = Path(sys.argv[1])


# Get the public config file
pubCon = configparser.ConfigParser()
pubCon.read(root.child("abc_config.cfg").absolute())

# Get the private config file
priCon = configparser.ConfigParser()
priCon.read(Path(pubCon.get("misc", "private_config")).absolute())


# Set up logging
log = python_logging.start(priCon)


# Collect debug status
debugData = debugging.get_debug_status(pubCon, log)


# Get robot details
userAgent = pubCon.get("robot", "user_agent", raw=True)
userFrom = pubCon.get("robot", "from", raw=True)
crawlDelay = pubCon.getfloat("misc", "crawl_delay")

# Create a requests session for use to access data
session = requests.Session()
session.headers.update({"User-Agent": userAgent, "From": userFrom})



# Create a database cursor and connection cursor to run queries
dbConn = return_connection(priCon, log)
dbCursor = return_cursor(dbConn, log)

# Collects relevant data from database to enable data parsing
parseData = collect_parse_data(dbCursor)

# Open required files for data extraction logging
fileNames = collect_file_paths(pubCon)

# SCRAPE ACTIVE URLS FROM WEBSITE
# Checking the robots.txt file for permission to crawl
if debug.scrapeUrl:
    can_crawl = get_permission()
else:
    can_crawl = True

# If crawling is permitted, run the program
if can_crawl:
    log.info("Permissing granted to crawl site")
    log.info("Starting URL extraction")

    # Assemble the files to save data
    with open(fileNames.url.absolute(), "w") as fURL, \
            open(fileNames.price.absolute(), "w") as fPrice, \
            open(fileNames.coverage.absolute(), "w") as fCoverage, \
            open(fileNames.specialAuth.absolute(), "w") as fSpecial, \
            open(fileNames.ptc.absolute(), "w") as fPTC, \
            open(fileNames.atc.absolute(), "w") as fATC, \
            open(fileNames.extra.absolute(), "w") as fExtra:

        # Save all opened files into on object for easier use
        files = organize_save_files(fURL, files.html, fPrice, fCoverage, 
                                    fSpecial, fPTC, fATC, fExtra)

        # Set the start and end for loop
        if debug.scrapeUrl or debug.scrapeData:
            start = int(sys.argv[2])
            end = int(sys.argv[3])
        else:
            urlList = debug.urlList
            start = debug.start
            end = debug.end
            

        # Cycle through the range of URLs
        for i in range(start, end + 1):
            # Remove old entry from the database
            if debug.uploadData:
                remove_data(dbCursor, i)
            
            
            # Get the URL data
            if debug.scrapeUrl:
                # Apply delay before crawling URL
                time.sleep(crawlDelay)
            
                urlData = scrape_url(i, session, log)
            else:
                urlData = urlList[i]


            # Collect the content for active URLs
            if urlData.status == "active":
                if debug.scrapeData:
                    # Apply delay before accessing page
                    time.sleep(crawlDelay)

                    content = collect_content(urlData, session, 
                                              parseData, log)
                else:
                    content = debug_data(urlData, debug.htmlLoc, parseData, 
                                         log)
            else:
                content = None

            if content:
                # UPLOAD INFORMATION TO DATABASE
                if debug.uploadData:
                    upload_data(content, dbCursor, log)

                # UPLOAD SUBS INFORMATION TO DATABASE
                if debug.uploadSubs:
                    upload_sub(content, dbCursor, log)

                # UPDATE WEBSITE DETAILS
                if debug.updateWebsite:
                    update_details(priCon, today, log)


                # SAVE BACKUP COPY OF DATA TO SERVER
                save_data(content, fURL, cPrice, cCoverage, cSpecial, 
                          cPTC, cATC, cExtra, pHTML)

            # Commit the database queries
            try:
                dbConn.commit()
            except:
                log.exception("Unable to update database for %s" % i)

    # Close Database Connection
    dbConn.close()