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
import time
from url_scrape import scrape_url, debug_url, debug_url_data
from data_extraction import collect_content, debug_data

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


class Debug(object):
    def __init__(self, scrapeUrl, urlList, start, end, scrapeData, htmlLoc,
               uploadData, updateWebsite):
        self.scrapeUrl = scrapeUrl
        self.urlList = urlList
        self.start = start
        self.end = end
        self.scrapeData = scrapeData
        self.htmlLoc = htmlLoc
        self.uploadData = uploadData
        self.updateWebsite = updateWebsite


def get_debug(conf):
    # Check if the URLs will be scrapped
    scrapeUrl = conf.getboolean("debug", "scrape_urls")

    if scrapeUrl:
        log.debug("URL SCRAPING ENABLED")
        urlList = None
        start = None
        end = None
    else:
        log.debug("DEBUG MODE - SKIPPING URL SCRAPING")

        urlList = debug_url(Path(conf.get("debug", "url_loc")))
        start = 0
        end = len(urlList) - 1
        
    # Check if pages will be scraped
    scrapeData = conf.getboolean("debug", "scrape_data")

    if scrapeData:
        log.debug("WEBSITE SCRAPING ENABLED")
        htmlLoc = None
    else:
        log.debug("DEBUG MODE - SKIPPING WEBSITE SCRAPING")
        htmlLoc = Path(conf.get("debug", "data_loc"))

        # Replaces any urlList data with the html content
        urlList = debug_url_data(htmlLoc)
        start = 0
        end = len(urlList) - 1
    
    # Check if data will be uploaded to database    
    uploadData = conf.getboolean("debug", "upload_data")
    
    if uploadData:
        log.debug("DATA UPLOAD ENABLED")
    else:
        log.debug("DEBUG MODE - SKIPPING DATABASE UPLOADS")

    # Check if details.php will be updated
    updateWebsite = conf.getboolean("debug", "update_website")

    if updateWebsite:
        log.debug("UPDATING 'details.php' ENABLED")
    else:
        log.debug("DEBUG MODE - SKIPPING 'details.php' UPDATE")

    debug = Debug(scrapeUrl, urlList, start, end, scrapeData, htmlLoc, 
                  uploadData, updateWebsite)

    return debug


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
    url.parent.mkdir(parents=True)

    # Assemble HTML file path
    html = Path(con.get("locations", "html")).child(today, "html")
    html.mkdir(parents=True)

    # Assemble price file path
    price = Path(con.get("locations", "price")).child(today, "price.csv")
    price.parent.mkdir(parents=True)

    # Assemble coverage file path
    cov = Path(con.get("locations", "coverage")).child(today, "coverage.csv")
    cov.parent.mkdir(parents=True)

    # Assemble special authorization file path
    special = Path(con.get("locations", "special")).child(today, "special.csv")
    special.parent.mkdir(parents=True)

    # Assemble PTC file path
    ptc = Path(con.get("locations", "ptc")).child(today, "ptc.csv")
    ptc.parent.mkdir(parents=True)

    # Assemble ATC file path
    atc = Path(con.get("locations", "atc")).child(today, "atc.csv")
    atc.parent.mkdir(parents=True)

    # Assemble extra information file path
    extra = Path(con.get("locations", "extra")).child(today, "extra.csv")
    extra.parent.mkdir(parents=True)

    return FileNames(url, html, price, cov, special, ptc, atc, extra)


def create_csv_writer(path):
    writer = csv.writer(path, 
                        quoting=csv.QUOTE_NONNUMERIC, 
                        lineterminator="\n")

    return writer


def save_data(content, fURL, cPrice, cCoverage, cSpecial, cPTC, cATC, 
              cExtra, pHTML):
    """Saves the information in content to respective files"""
    # Save URL data
    fURL.write("%s\n" % content.url)

    # Save the price data
    price = [content.url, content.din.parse, content.bsrf.brand, 
             content.bsrf.strength, content.bsrf.route, content.bsrf.form, 
             content.genericName.parse, content.unitPrice.parse, 
             content.lca.value, content.lca.text, content.unitIssue.parse]

    try:
        cPrice.writerow(price)
    except:
        log.exception("Unable to write %s to price.csv" % content.url)

    # Save the coverage data
    coverage = [content.url, content.coverage.parse, 
                content.criteria.criteria, content.criteria.special, 
                content.criteria.palliative, content.clients.g1, 
                content.clients.g66, content.clients.g66a,
                content.clients.g19823, content.clients.g19824, 
                content.clients.g20400, content.clients.g20403,
                content.clients.g20514, content.clients.g22128,
                content.clients.g23609]
    
    try:
        cCoverage.writerow(coverage)
    except:
        log.exception("Unable to write %s to coverage.csv" % content.url)

    # Save the special authorization data
    special = []
    
    for item in content.specialAuth:
        special.append([content.url, item.text, item.link])

    try:
        cSpecial.writerows(special)
    except:
        log.exception("Unable to write %s to special.csv" % content.url)

    # Save the PTC data
    ptc = [content.url, content.ptc.code1, content.ptc.text1, 
           content.ptc.code2, content.ptc.text2, 
           content.ptc.code3, content.ptc.text3, 
           content.ptc.code4, content.ptc.text4]

    try:
        cPTC.writerow(ptc)
    except:
        log.exception("Unable to write %s to ptc.csv" % content.url)

    # Save the ATC data
    atc = [content.url, content.atc.code1, content.atc.text1, 
           content.atc.code2, content.atc.text2, 
           content.atc.code3, content.atc.text3, 
           content.atc.code4, content.atc.text4, 
           content.atc.code5, content.atc.text5]

    try:
        cATC.writerow(atc)
    except:
        log.exception("Unable to write %s to atc.csv" % content.url)

    # Save the extra information data
    extra = [content.url, content.dateListed.parse, 
             content.dateDiscontinued.parse, content.manufacturer.parse, 
             content.schedule.parse, content.interchangeable.parse]

    try:
        cExtra.writerow(extra)
    except:
        log.exception("Unable to write %s to extra.csv" % content.url)

    # Save a copy of the HTML page
    htmlPath = pHTML.child("%s.html" % content.url).absolute()
    try:
        with open(htmlPath, "w") as fHTML:
            fHTML.write(content.html)
    except:
        log.exception("Unable to save HTML for %s" % content.url)


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
debug = get_debug(pubCon)

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
if debug.scrapeUrl:
    can_crawl = get_permission()
else:
    can_crawl = True


# If crawling is permitted, run the program
if can_crawl:
    from collect_parse_data import collect_parse_data
    from database_functions import return_connection, return_cursor, \
                                   remove_data, upload_data
    from update_website import update_details

    log.info("Permissing granted to crawl site")
    log.info("Starting URL extraction")

    # Create a database cursor and connection cursor to run queries
    dbConn = return_connection(priCon, log)
    dbCursor = return_cursor(dbConn, log)

    # Collects relevant data from database to enable data parsing
    parseData = collect_parse_data(dbCursor)

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
        cPrice = create_csv_writer(fPrice)
        cCoverage = create_csv_writer(fCoverage)
        cSpecial = create_csv_writer(fSpecial)
        cPTC = create_csv_writer(fPTC)
        cATC = create_csv_writer(fATC)
        cExtra = create_csv_writer(fExtra)

        # Get filepath for HTML files
        pHTML = files.html

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