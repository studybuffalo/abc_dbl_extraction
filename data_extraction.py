class PageContent(object):
    def __init__(self, din):
        self.din = din
        
def download_page(session, url):
    response = session.get(url)
    status = response.status_code

    if status == 200:
        return response.text()
    else:
        raise IOError("%s returned status code %d" % (url, status))

def extract_page_content(page):
    def truncate_content(page):
        """Extracts relevant HTML and returns a BeautifulSoup object

            This was determined with trial and error; the start and 
            end parts appear to be unique strings that reasonably
            extract the relevant HTML sections from the page.
        """
        start = page.find("columnLeftFull")
        end = page.find("A drug classification system")

        page = html[start:end]

        html = BeautifulSoup(page, 'html.parser')

        return html
        
    def extract_din(html):
        """Extracts the DIN the HTML content"""
        # Get the main HTML element
        din = html.p.string

        # Remove exccess content
        din = din.replace("DIN/PIN Detail - ", "")

        return din

    def extract_ptc():
        """"""
        ptc = html.find_all('tr', class_="idblTable")[0].td.div.p.get_text().strip()
    
    def extract_brand_name():
        """"""
        brand_name = html.find_all('tr', class_="idblTable")[1].td.div.string.strip()

    def extract_generic_name():
        """"""
        generic_name = html.find_all('tr', class_="idblTable")[2].td.div.string.strip()

    def extract_date_listed():
        """"""
        date_listed = html.find_all('tr', class_="idblTable")[3].find_all('td')[1].string.strip()

    def extract_date_discontinued():
        """"""
        date_discontinued = html.find_all('tr', class_="idblTable")[4].find_all('td')[1].string.strip()

    def extract_unit_price():
        """"""
        unit_price = html.find_all('tr', class_="idblTable")[5].find_all('td')[1].string.strip()

    def extract_lca():
        """"""
        lca = html.find_all('tr', class_="idblTable")[6].find_all('td')[1].div.get_text().strip()

    def extract_unit_issue():
        """"""
        unit_issue =  html.find_all('tr', class_="idblTable")[7].find_all('td')[1].string.strip()

    def extract_interchangeable():
        """"""
        interchangeable = html.find_all('tr', class_="idblTable")[8].find_all('td')[1].get_text()
          
        if "YES" in interchangeable:
            interchangeable = 1
        else:
            interchangeable = 0

    def extract_manufacturer():
        """"""
        manufacturer = html.find_all('tr', class_="idblTable")[9].find_all('td')[1].a.string.strip()

    def extract_atc():
        """"""
        atc = html.find_all('tr', class_="idblTable")[10].find_all('td')[1].string.strip()

    def extract_schedule():
        """"""
        schedule = html.find_all('tr', class_="idblTable")[11].find_all('td')[1].string.strip()

    def extract_coverage():
        """"""
        coverage = html.find_all('tr', class_="idblTable")[12].find_all('td')[1].string.strip()

    def extract_clients():
        """"""
        clients = html.find_all('tr', class_="idblTable")[13].find_all('td')[1].get_text().strip()

    def extract_coverage_criteria():
        """"""
        coverage_criteria = html.find_all('tr', class_="idblTable")[14].find_all('td')[1].get_text()
        
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

    def extract_special_auth():
        """"""
        special_auth_temp = html.find_all('tr', class_="idblTable")[15].find_all('td')[1]
        
        special_auth = []
        special_auth_link = []
      
        if "N/A" in special_auth_temp.get_text():
            special_auth = ["N/A"]
            special_auth_link = ["N/A"]
        else:
            for a in special_auth_temp.find_all('a'):
                special_auth.append(a.string.strip())
                special_auth_link.append(a['onclick'])

    html = truncate_content(page)

    # Extract HTML content
    din = extract_din(html)
    ptc = extract_ptc(html)
    brandName = extract_brand_name(html)
    genericName = extract_generic_name(html)
    dateListed = extract_date_listed(html)
    dateDiscontinued = extract_date_discontinued(html)
    unitPrice = extract_unit_price(html)
    lca = extract_lca(html)
    unitIssue = extract_unit_issue(html)
    interchangeable = extract_interchangeable(html)
    manufacturer = extract_manufacturer(html)
    atc = extract_atc(html)
    schedule = extract_schedule(html)
    coverage = extract_coverage(html)
    clients = extract_clients(html)
    coverageCriteria = extract_coverage_criteria(html)
    specialAuth = extract_special_auth(html)

    # Generate the final object
    pageContent = PageContent()

    return pageContent

def collect_content(config, session, urlList, today, crawlDelay):
    """Takes a list of URLs and extracts drug pricing information
        args:
            config:     config object holding extraction details
            urlList:    a list of valid URL strings
            today:      todays date as a string (yyyy-mm-dd)
            crawlDelay: time to pause between each request

        returns:
            content:    a lost of object containing the pricing data

        raises:
            none.
    """
    
    from bs4 import BeautifulSoup
    import time

    # List to hold all the extracted content
    content = []

    # Gets folder path to save files to
    dataLocation = config.get("misc", "data_location")

    # Opens text files to save extracted data
    pricePath = dataLocation.child("%s_price.csv" % today).absolute()
    coveragePath = dataLocation.child("%s_coverage.csv" % today).absolute()
    specialPath = dataLocation.child("%s_special.csv" % today).absolute()
    ptcPath = dataLocation.child("%s_ptc.csv" % today).absolute()
    atcPath = dataLocation.child("%s_atc.csv" % today).absolute()
    extraPath = dataLocation.child("%s_extra.csv" % today).absolute()
    errorPath = dataLocation.child("%s_price.txt" % today).absolute()
    
    with open(pricePath, "w") as priceCSV,\
            open(coveragePath, "w") as coverageCSV,\
            open(specialPath, "w") as specialCSV,\
            open(ptcPath, "w") as ptcCSV,\
            open(atcPath, "w") as atcCSV,\
            open(extraPath, "w") as extraCSV,\
            open(errorPath, "w") as errorText:

        # DOWNLOAD WEB PAGE CONTENT
        
        for url in urlList:
            try:
                page = download_page(session, url)
            except Exception as e:
                log.warn("Unable to download page content: %e"
                         % (url, e))
                page = None

            if page:
                try:
                    pageContent = extract_page_content(page)
                except Exception as e:
                    log.warn("Unable to extract %s page content: %s" 
                             % (url, e))
                    pageContent = None

            if pageContent:
                content.append(pageContent)
                # Write content to file

        return content
"""
        
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
        time.sleep(0.25)
"""