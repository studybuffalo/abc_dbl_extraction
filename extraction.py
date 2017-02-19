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
import os
from unipath import Path
import datetime
from urllib import robotparser, request
import requests
import codecs
import math
import pymysql
import configparser
import time
from bs4 import BeautifulSoup
from ftplib import FTP
import parse
from upload import generate_statement


def setup_config():
	config = configparser.ConfigParser()
	config.read(root.parent.child("config", "python_config.cfg").absolute())

	return config


def get_date():
	today = datetime.date.today()
	year = today.year
	month = "%02d" % today.month
	day = "%02d" % today.day
	date = "%s-%s-%s" % (year, month, day)

	return date


def get_permission():
	robot = robotparser.RobotFileParser()
	robot.set_url("https://www.ab.bluecross.ca/robots.txt")
	robot.read()

	can_crawl = robot.can_fetch(
		"Study Buffalo Data Extraction (http://www.studybuffalo.com/dataextraction/)",
		"https://idbl.ab.bluecross.ca/idbl/load.do")

	return can_crawl


def check_url(session, url, scriptHeader, active, error):
	'''Checks URL and saves/returns active ones.'''
	try:
		response = session.head(url, headers=scriptHeader, allow_redirects=False)
		code = response.status_code
	except:
		code = 0
	
	if code == 200:
		active.write(url + "\n")
		return url
	elif code != 302:
		error.write(url + "\n")
		return None


def progress_bar(title, curPos, start, stop):
	'''Generates progress bar in console.'''

	# Normalize start, stop, curPos
	curPos = (curPos - start) + 1
	stop = (stop - start) + 1 
	start = 1

	# Determine current progress
	prog = 100.00 * (curPos / stop)
	
	if prog != 100:
		progComp = "#" * math.floor(prog / 2)
		progRem = " " * (50 - math.floor(prog / 2))
		prog = "%.2f%%" % prog
		print(("%s [%s%s] %s  \r" % (title, progComp, progRem, prog)), end='')
		sys.stdout.flush()
	else:
		progComp = "#" * 50
		print("%s [%s] Complete!" % (title, progComp))
	

# APPLICATION SETUP
# Set up root path to generate absolute paths to files
root = Path("/", "home", "joshua", "scripts", "abc_price")

# Setup config file
config = setup_config()

# Get Current Date
date = get_date()


'''Crawls the website looking for active URLs'''
# Creates file path (and folder if needed) to save active urls
listLocation = root.child("active_urls", date)

if not listLocation.exists():
	os.mkdir(listLocation.absolute())

# Generates .txt files with all the valid URLs and the URLs with errors
active_list = listLocation.child("active.txt").absolute()
error_list = listLocation.child("error.txt").absolute()


print ("\nALBERTA BLUE CROSS DRUG BENEFIT LIST EXTRACTION TOOL")
print ("----------------------------------------------------")
print ("Created by Joshua Torrance, 2017-02-19\n\n")


# Checking the robots.txt file for permission to crawl
print ("CHECKING PERMISSIONS")
print ("--------------------")
print("Checking robot.txt for permission to crawl")
	
can_crawl = get_permission()
# can_crawl = True

# If crawling is permitted, begins crawling URLs to look for active ones
if can_crawl == True:
	print ("Permission Granted!\n\n")

	print ("URL LIST GENERATION")
	print ("-------------------")
	print ("Screening URLs and generating lists")
	
	# Script header to identify script
	scriptHeader = {
		'User-Agent': 'Study Buffalo Data Extraction (http://www.studybuffalo.com/dataextraction/)',
		'From': 'studybuffalo@studybuffalo.com'
	}
	
	# Session to request HTML headers
	session = requests.Session()
	
	# Variables to generate urls
	base = "https://idbl.ab.bluecross.ca/idbl/lookupDinPinDetail.do?productID="
	start = 0
	end = 85000
	url_list = []
	
	# Goes through each URL; saves active ones to text file and list
	with open(active_list, 'w') as active, open(error_list, 'w') as error:
		for i in range (start, end + 1):
			url = "%s%010d" % (base, i)
			
			temp_url = check_url(session, url, scriptHeader, active, error)
			
			if temp_url != None:
				url_list.append(temp_url)
			
			# Progress Bar
			progress_bar("Screening", i, start, end)

			time.sleep(0.25)
	
	print("List generated\n\n")
	

'''Scrapes the active URLs, processes them, and saves them.'''
# Creates folder for extracted data if necessary
save_location = root.child("extracted_data", date)
	
if not save_location.exists():
	os.mkdir(save_location.absolute())

# Opens text files to save extracted data
price_file_path = save_location.child("price.txt").absolute()
price_file = codecs.open(price_file_path, 'w', encoding='utf-8')

coverage_file_path = save_location.child("coverage.txt").absolute()
coverage_file = codecs.open(coverage_file_path, 'w', encoding='utf-8')

special_file_path = save_location.child("special_auth.txt").absolute()
special_file = codecs.open(special_file_path, 'w', encoding='utf-8')

ptc_file_path = save_location.child("ptc.txt").absolute()
ptc_file = codecs.open(ptc_file_path, 'w', encoding='utf-8')

atc_file_path = save_location.child("atc.txt").absolute()
atc_file = codecs.open(atc_file_path, 'w', encoding='utf-8')

extra_file_path = save_location.child("extra.txt").absolute()
extra_file = codecs.open(extra_file_path, 'w', encoding='utf-8')

error_file_path = save_location.child("error.txt").absolute()
error_file = codecs.open(error_file_path, 'w', encoding='utf-8')

# Connecting to page and downloading html
print ("DRUG BENEFIT LIST DATA EXTRACTION")
print ("---------------------------------")
print("Web crawl extraction and processing")
length = len(url_list) - 1
i = 0

# Lists to hold data for database upload
price_list = []
coverage_list = []
special_list = []
ptc_list = []
atc_list = []
extra_list = []

for url in url_list:
	try:
		
		# Connect to webpage
		response = request.urlopen(url)
		html = response.read().decode('utf-8')
		
		start = html.find("columnLeftFull")
		end = html.find("A drug classification system")
		html = html[start:end]
		html = BeautifulSoup(html, 'html.parser')
		
		# Extract HTML content
		din = html.p.string
		ptc = html.find_all('tr', class_="idblTable")[0].td.div.p.get_text().strip()
		brand_name = html.find_all('tr', class_="idblTable")[1].td.div.string.strip()
		generic_name = html.find_all('tr', class_="idblTable")[2].td.div.string.strip()
		date_listed = html.find_all('tr', class_="idblTable")[3].find_all('td')[1].string.strip()
		date_discontinued = html.find_all('tr', class_="idblTable")[4].find_all('td')[1].string.strip()
		unit_price = html.find_all('tr', class_="idblTable")[5].find_all('td')[1].string.strip()
		lca = html.find_all('tr', class_="idblTable")[6].find_all('td')[1].div.get_text().strip()
		unit_issue =  html.find_all('tr', class_="idblTable")[7].find_all('td')[1].string.strip()
		interchangeable = html.find_all('tr', class_="idblTable")[8].find_all('td')[1].get_text()
		manufacturer = html.find_all('tr', class_="idblTable")[9].find_all('td')[1].a.string.strip()
		atc = html.find_all('tr', class_="idblTable")[10].find_all('td')[1].string.strip()
		schedule = html.find_all('tr', class_="idblTable")[11].find_all('td')[1].string.strip()
		coverage = html.find_all('tr', class_="idblTable")[12].find_all('td')[1].string.strip()
		clients = html.find_all('tr', class_="idblTable")[13].find_all('td')[1].get_text().strip()
		coverage_criteria = html.find_all('tr', class_="idblTable")[14].find_all('td')[1].get_text()
		special_auth_temp = html.find_all('tr', class_="idblTable")[15].find_all('td')[1]
			
		# Basic processing of content
		special_auth = []
		special_auth_link = []
		
		if "YES" in interchangeable:
			interchangeable = 1
		else:
			interchangeable = 0

		if "Click" in coverage_criteria:
			if "coverage" in coverage_criteria and "program" in coverage_criteria:
				coverage_criteria_sa = html.find_all('tr', class_="idblTable")[14].find_all('td')[1].p.find_all('a')[0]['onclick']
				coverage_criteria_p = "http://www.health.alberta.ca/services/drugs-palliative-care.html"
			elif "coverage" in coverage_criteria:
				coverage_criteria_sa = html.find_all('tr', class_="idblTable")[14].find_all('td')[1].p.find_all('a')[0]['onclick']
				coverage_criteria_p = None
			elif "program" in coverage_criteria:
				coverage_criteria_sa = None
				coverage_criteria_p = "http://www.health.alberta.ca/services/drugs-palliative-care.html"
				
			coverage_criteria = 1
		else:
			coverage_criteria = 0
			coverage_criteria_sa = None
			coverage_criteria_p = None


		if "N/A" in special_auth_temp.get_text():
			special_auth = ["N/A"]
			special_auth_link = ["N/A"]
		else:
			for a in special_auth_temp.find_all('a'):
				special_auth.append(a.string.strip())
				special_auth_link.append(a['onclick'])

		# Parsing HTML content into formatted lists
		price_data = parse.price_data(url, din, brand_name,
									  generic_name, unit_price, lca,
									  unit_issue)

		coverage_data = parse.coverage_data(url, coverage, clients,
											coverage_criteria,
											coverage_criteria_sa,
											coverage_criteria_p)

		special_data = parse.special_auth_data(url, special_auth,
											   special_auth_link)
		
		ptc_data = parse.ptc_data(url, ptc)
		
		atc_data = parse.atc_data(url, atc)
		
		extra_data = parse.extra_data(url, date_listed, 
									  date_discontinued, manufacturer,
									  schedule, interchangeable)
		
		# Adding parsed lists to list for database upload/saving to .txt
		price_list.append(price_data)
		coverage_list.append(coverage_data)
		ptc_list.append(ptc_data)
		atc_list.append(atc_data)
		extra_list.append(extra_data)
		
		for item in special_data:
			special_list.append(item)
		
		
		# Saving parsed lists to .txt files
		price_file.write(('"%s","%s","%s","%s","%s","%s","%s","%s",'
						  '"%s","%s","%s"\n') % 
						  (price_data[0], price_data[1], price_data[2],
						   price_data[3], price_data[4], price_data[5],
						   price_data[6], price_data[7], price_data[8],
						   price_data[9], price_data[10]))
			
		coverage_file.write(('"%s","%s","%s","%s","%s","%s","%s","%s",'
							 '"%s","%s","%s","%s","%s","%s","%s",'
							 '"%s"\n') % 
							 (coverage_data[0], coverage_data[1],
							  coverage_data[2], coverage_data[3],
							  coverage_data[4], coverage_data[5],
							  coverage_data[6], coverage_data[7],
							  coverage_data[8], coverage_data[9],
							  coverage_data[10], coverage_data[11],
							  coverage_data[12], coverage_data[13],
							  coverage_data[14], coverage_data[15]))
		
		for item in special_data:
			special_file.write('"%s","%s","%s"\n' % 
							   (item[0], item[1], item[2]))
		
		ptc_file.write(('"%s","%s","%s","%s","%s","%s","%s","%s","%s"'
						'\n') %
						(ptc_data[0], ptc_data[1], ptc_data[2],
						 ptc_data[3], ptc_data[4], ptc_data[5],
						 ptc_data[6], ptc_data[7], ptc_data[8]))
		
		atc_file.write(('"%s","%s","%s","%s","%s","%s","%s","%s",'
						'"%s","%s","%s"\n') % 
						(atc_data[0], atc_data[1], atc_data[2], 
						 atc_data[3], atc_data[4], atc_data[5], 
						 atc_data[6], atc_data[7], atc_data[8], 
						 atc_data[9], atc_data[10]))
		
		extra_file.write(('"%s","%s","%s","%s","%s","%s"\n') % 
						  (extra_data[0], extra_data[1], extra_data[2],
						   extra_data[3], extra_data[4], extra_data[5]))
		
		# Progress bar
		progress_bar("Extracting", i, 0, length)
		i += 1
		
		time.sleep(0.25)
	except Exception as e:
		error_file.write("Error involving %s - %s\n" % (url, e))

print("Crawling and Processing Complete!\n\n")

# Closes files
price_file.close()
coverage_file.close()
special_file.close()
ptc_file.close()
atc_file.close()
extra_file.close()

'''Uploading the parsed lists to the appropriate databases.'''
print ("UPLOADING TO DATABASE")
print ("---------------------")

# Connect to database
mysql_user = config.get('mysql_user_abc_ent', 'user')
mysql_password = config.get('mysql_user_abc_ent', 'password')
mysql_db = config.get('mysql_db_abc_dbl', 'db')
mysql_host = config.get('mysql_db_abc_dbl', 'host')

conn = pymysql.connect(user = mysql_user,
					   passwd = mysql_password,
					   db = mysql_db, 
					   host = mysql_host,
					   charset='utf8',
					   use_unicode=True)
cursor = conn.cursor()

table_list = [["abc_price", price_list],
			  ["abc_coverage", coverage_list],
			  ["abc_special_authorization", special_list],
			  ["abc_ptc", ptc_list],
			  ["abc_atc", atc_list],
			  ["abc_extra_information", extra_list]]

# Upload each list to the appropriate database table
for upload_item in table_list:			  
	print (("Uploading to '%s' table... " % upload_item[0]), end='')
	
	#Truncates table to prepare for new entries
	try:
		cursor.execute("TRUNCATE %s" % upload_item[0])
		conn.commit()
	except MySQLdb.Error as e:
		print ("Error Truncating Table: %s" % e)
		pass

	# Generates MySQL statement and loads into database
	statement = generate_statement(upload_item[0])
	
	# Attempts insertion into database
	try:
		cursor.executemany(statement, upload_item[1])
		conn.commit()
		print ("Complete!")
	except MySQLdb.Error as e:
		print ("Error trying insert entry %s into database: %s" % (i, e))
		pass

print("\n")

'''Connects to website server to update $update in details.php.'''
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
			   "\t$update = '%s';" % date)

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