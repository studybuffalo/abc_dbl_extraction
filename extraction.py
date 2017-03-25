#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''Extracts and saves the Alberta Blue Cross idbl.

  Last Update: 2017-Feb-19

  Copyright (c) Notices
	2017	Joshua R. Torrance	<studybuffalo@studybuffalo.com>
	
  This software may be used in any medium or format and adapated to
  any purpose under the following terms:
    - You must give appropriate credit, provide a link to the
      license, and indicate if changes were made. You may do so in
      any reasonable manner, but not in any way that suggests the
      licensor endorses you or your use.
    - You may not use the material for commercial purposes.
    - If you remix, transform, or build upon the material, you must 
      distribute your contributions under the same license as the 
      original.
	
  Alternative uses may be discussed on an individual, case-by-case 
  basis by contacting one of the noted copyright holders.

  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
  EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
  OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
  HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
  WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
  OTHER DEALINGS IN THE SOFTWARE.
'''

import sys
from unipath import Path
import configparser
import python_logging
import datetime
from urllib import robotparser
import requests
import csv


class FileNames(object):
    def __init__(self, url, html, price, coverage, 
                 specialAuth, ptc, atc, extra):
        self.url = url
        self.html = html
        self.price = price
        self.coverage = coverage
        self.specialAuth = specialAuth
        self.ptc = ptc
        self.atc = atc
        self.extra = extra


def setup_config():
	config = configparser.ConfigParser()
	config.read(root.parent.child("config", "python_config.cfg").absolute())

	return config


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


def collect_file_paths(con):
    """Collects extraction file paths and creates needed directories"""
    # Get Current today
    today = get_today()

    # Assemble URL filepath
    url = Path(con.get("locations", "url")).child(today, "url.txt")
    url.parent.mkdir(parents=True, exist_ok=True)

    # Assemble HTML file path
    html = Path(con.get("locations", "html").child(today, "html"))
    html.mkdir(parents=True, exist_ok=True)

    # Assemble price file path
    price = Path(con.get("locations", "price").child(today, "price.csv"))
    price.parent.mkdir(parents=True, exist_ok=True)

    # Assemble coverage file path
    cov = Path(con.get("locations", "coverage").child(today, "coverage.csv"))
    cov.parent.mkdir(parents=True, exist_ok=True)

    # Assemble special authorization file path
    special = Path(con.get("locations", "special").child(today, "special.csv"))
    special.parent.mkdir(parents=True, exist_ok=True)

    # Assemble PTC file path
    ptc = Path(con.get("locations", "ptc").child(today, "ptc.csv"))
    ptc.parent.mkdir(parents=True, exist_ok=True)

    # Assemble ATC file path
    atc = Path(con.get("locations", "atc").child(today, "atc.csv"))
    atc.parent.mkdir(parents=True, exist_ok=True)

    # Assemble extra information file path
    extra = Path(con.get("locations", "extra").child(today, "extra.csv"))
    extra.parent.mkdir(parents=True, exist_ok=True)

    return FileNames(url, html, price, cov, special, ptc, atc, extra)


def save_data(content, fURL, cPrice, cCoverage, cSpecial, cPTC, cATC, 
              cExtra, pHTML):
    """Saves the information in content to respective files"""
    # Save URL data
    fURL.write("%s\n" % content.url)

    # Save the price data
    price = []
    cPrice.writerow(price)

    # Save the coverage data
    coverage = []
    cCoverage.writerow(coverage)

    # Save the special authorization data
    special = []
    cSpecial.writerow(special)

    # Save the PTC data
    ptc = []
    cPTC.writerow(ptc)

    # Save the ATC data
    atc = []
    cATC.writerow(atc)

    # Save the extra information data
    extra = []
    cExtra.writerow(extra)

    # Save a copy of the HTML page
    with open(pHTML.child("%s.html" % content.url).absolute(), "w") as fHTML:
        fHTML.write(content.html)


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

# Get robot details
userAgent = pubCon.get("robot", "user_agent", raw=True)
userFrom = pubCon.get("robot", "from", raw=True)
crawlDelay = pubCon.getfloat("misc", "crawl_delay")

# Create a requests session for use to access data
session = requests.Session()
session.headers.update({"User-Agent": userAgent, "From": userFrom})

log.info("ALBERTA BLUE CROSS DRUG BENEFIT LIST EXTRACTION TOOL STARTED")

# SCRAPE ACTIVE URLS FROM WEBSITE
# Checking the robots.txt file for permission to crawl
can_crawl = get_permission()

# If crawling is permitted, run the program
if can_crawl:
    from url_scrape import scrape_urls
    from data_extraction import collect_content
    import data_upload
    from update_website import update_details

    log.info("Permissing granted to crawl site")
    log.info("Starting URL extraction")

    # Create a database cursor and connection cursor to run queries
    dbConn = data_upload.return_connection(priCon)
    dbCursor = data_upload.return_cursor(dbConn)

    # Open required files for data extraction logging
    files = collect_file_paths(pubCon)

    with open(files.url.absolute(), "w") as fURL, \
            open(files.price.absolute(), "w") as fPrice, \
            open(files.coverage.absolute(), "w") as fCoverage, \
            open(files.specialAuth.absolute(), "w") as fSpecial, \
            open(files.ptc.absolute(), "w") as fPTC, \
            open(files.atc.absolute(), "w") as fATC, \
            open(files.extra.absolute(), "w") as fExtra:

        # Create appropriate CSV writers
        quoteStyle = csv.QUOTE_NONNUMERIC

        cPrice = csv.writer(fPrice, quoting=quoteStyle)
        cCoverage = csv.writer(fCoverage, quoting=quoteStyle)
        cSpecial = csv.writer(fSpecial, quoting=quoteStyle)
        cPTC = csv.writer(fPTC, quoting=quoteStyle)
        cATC = csv.writer(fATC, quoting=quoteStyle)
        cExtra = csv.writer(fExtra, quoting=quoteStyle)

        # Get filepath for HTML files
        pHTML = files.html
        
        for i in range (start, end + 1):
            # Remove old entry from the database
            remove_data(cursor, url)

            # Get the URL data
            urlData = scrape_url(i, session, crawlDelay, log)

            # Collect the content for active URLs
            if urlData.status == "active":
                content = collect_content(urlData.url, session, crawlDelay, 
                                          dbCursor, log)

            if content:
                # UPLOAD INFORMATION TO DATABASE
                data_upload.upload_data(content, dbCursor)

                # UPDATE WEBSITE DETAILS
                update_details(priCon, today)

                # SAVE BACKUP COPY OF DATA TO SERVER
                save_data(content, fURL, cPrice, cCoverage, cSpecial, 
                          cPTC, cATC, cExtra, pHTML)

            # Commit the database queries
            dbConn.commit()

    # Close Database Connection
    dbConn.close()