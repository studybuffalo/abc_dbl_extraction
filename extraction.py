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
from urllib import robotparser, request

import csv
import codecs
import math
import pymysql

import time
from bs4 import BeautifulSoup
from ftplib import FTP
import parse
from upload import generate_statement


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

# APPLICATION SETUP
# Set up root path to generate absolute paths to files
root = Path(sys.argv[1])

# Get the public config file
pubCon = configparser.ConfigParser()
pubCon = root.child("abc_config.cfg")

# Get the private config file
priCon = configparser.ConfigParser()
priCon = Path(pubCon.get("misc", "private_config"))

# Set up logging
log = python_logging.start(priCon)

# Get Current Date
today = get_today()

# Get robot details
userAgent = pubCon.get("robot", "user_agent", raw=True)
userAgentContact = pubCon.get("robot", "user_email")
crawlDelay = pubCon.getfloat("misc", "crawl_delay")

log.info("ALBERTA BLUE CROSS DRUG BENEFIT LIST EXTRACTION TOOL STARTED")

# SCRAPE ACTIVE URLS FROM WEBSITE
# Checking the robots.txt file for permission to crawl
can_crawl = get_permission()

# If crawling is permitted, run url scraper
if can_crawl:
    from url_scrape import scrape_urls
    urlList = scrape_urls(pubCon, today)
    
# SCRAPES DATA FROM ACTIVE URLS
if len(urlList):
    from data_extraction import extract_content
    content = extract_content(pubCon, urlList, today, crawlDelay)


# UPLOAD INFORMATION TO DATABASE
# Connect to database
if content:
    from data_upload import upload_data
    upload_data(content, priCon)


# UPDATE WEBSITE DETAILS
print ("WEBSITE UPDATE")
print ("--------------")

# Connect to server
ftp_address = config.get('ftp_sb', 'address')
ftp_user = config.get('ftp_sb', 'user')
ftp_password = config.get('ftp_sb', 'password')

print("Connecting to Study Buffalo server")
ftp = FTP(ftp_address, ftp_user, ftp_password)

# Change to proper directory
ftp.cwd('/public_html/studybuffalo/practicetools/albertadrugprice')

# Create the details.php file
with open('details.php', 'w') as file:
	file.write("<?\n"
			   "\t$title = 'Alberta Drug Price Calculator';\n"
			   "\t$description = 'Calculates the cost of a list "
			   "of medications for your patient. Also identifies "
			   "any requirements for drug coverage under Alberta "
			   "Blue Cross.';\n"
			   "\t$update = '%s';" % today)

# Access the details file to upload
phpFile = open('details.php', 'rb')

# Upload the temp file
print (("Uploading new 'details.php'... "), end='')
ftp.storlines('STOR details.php', phpFile)

phpFile.close()
ftp.quit()

os.remove('details.php')

print("Complete!\n\n")


print("Alberta Blue Cross Drug Benefit List Extraction Complete!\n")