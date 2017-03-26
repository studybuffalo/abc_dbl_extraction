class PageContent(object):
    def __init__(self, url, html, din, ptc, bsrf, genericName, dateListed, 
                 dateDiscontinued, unitPrice, lca, unitIssue, 
                 interchangeable, manufacturer, atc, schedule, coverage, 
                 clients, coverageCriteria, specialAuth):
        self.url = url
        self.html = html
        self.din = din
        self.ptc = ptc
        self.brandName = bsrf.brand
        self.strength = bsrf.strength
        self.route = bsrf.route
        self.dosageForm = bsrf.dosageForm
        self.genericName = genericName
        self.dateListed = dateListed
        self.dateDiscontinued = dateDiscontinued
        self.unitPrice = unitPrice
        self.lca = lca
        self.unitIssue = unitIssue
        self.interchangeable = interchangeable
        self.manufacturer = manufacturer
        self.atc = atc
        self.schedule = schedule
        self.coverage = coverage
        self.clients = clients
        self.criteria = coverageCriteria
        self.specialAuth = specialAuth
        

class PTC(object):
    def __init__(self, ptcList):
        self.code1 = ptcList[0]
        self.text1 = ptcList[1]
        self.code2 = ptcList[2]
        self.text2 = ptcList[3]
        self.code3 = ptcList[4]
        self.text3 = ptcList[5]
        self.code4 = ptcList[6]
        self.text4 = ptcList[7]


class BSRF(object):
    def __init__(self, brand, strength, route, form):
        self.brand = brand
        self.strength = strength
        self.route = route
        self.form = form


class LCA(object):
    def __init__(self, value, text):
        self.value = value
        self.text = text


class ATC(object):
    def __init__(self, atcList):
        self.code1 = atcList[0]
        self.text1 = atcList[1]
        self.code2 = atcList[2]
        self.text2 = atcList[3]
        self.code3 = atcList[4]
        self.text3 = atcList[5]
        self.code4 = atcList[6]
        self.text4 = atcList[7]
        self.code5 = atcList[8]
        self.text5 = atcList[9]


class Clients(object):
    def __init__(self, list):
        self.g1 = list[0]
        self.g66 = list[1]
        self.g66a = list[2]
        self.g19823 = list[3]
        self.g19824 = list[4]
        self.g20400 = list[5]
        self.g20403 = list[6]
        self.g20514 = list[7]
        self.g22128 = list[8]
        self.g23609 = list[9]


class CoverageCriteria(object):
    def __init__(self, criteria, criteriaSA, criteriaP):
        self.criteria = criteria
        self.special = criteriaSA
        self.palliative = criteriaP


class SpecialAuthorization(object):
    def __init__(self, text, link):
        self.text = text
        self.link = link


def download_page(session, url):
    """Downloads the webpage at the provided URL"""
    response = session.get(url)
    status = response.status_code
    
    if status == 200:
        return response.text
    else:
        raise IOError("%s returned status code %d" % (url, status))


def binary_search(term, lists):
    """Searches for term in provided list
        args:
            term:   the term to be found in the provided list
            lists:  an object containg a search list (a list of search 
                    terms to match against) and an return list (a 
                    matching list to the search list that contains 
                    the desired content to return
        
        returns:
            on match:   the corresponding object to the match
            no match:   None

        raises:
            none.
    """

    searchList = lists.searchList
    returnList = lists.objectList

    # Look for match
    i = bisect_left(searchList, term)

    # If match found, return the corresponding object
    if i != len(list) and searchList[i] == term:
        return returnList[i]
    else:
        return None


def extract_page_content(url, page, parseData, log):
    """Takes the provided HTML page and extracts all relevant content
        args:
            url:        url to extract data from
            page:       A BeautifulSoup object with the content 
                        to extract
            parseData:  an object containing relevant data to parse 
                        extracted content
            log:        a logging object to send logs to

        returns:
            pageContent:    object with all the extracted data

        raises:
            none.
    """
    from bs4 import BeautifulSoup
    import re
    from bisect import bisect_left

    def truncate_content(page):
        """Extracts relevant HTML and returns a BeautifulSoup object"""

        try:
            html = BeautifulSoup(page, "html.parser")
            trunc = html.findAll("div", {"class": "columnLeftFull"})[0]
        except:
            log.exception("Unable to create Soup for %s" % url)

        return trunc
    
    def convert_date(dateString):
        """Converts the ABC date to a MySQL date format"""

        # If date is present, will be in form of dd-mmm-yyyy
        try:
            # Convert to date object
            date = datetime.strptime(dateString, "%d-%b-%Y")

            # Format for MySQL (yyyy-mm-dd)
            date = date.strftime("%y-%m-%d")
        except ValueError:
            # Expected behaviour for most situations without a date
            date = None
        except:
            log.warn("Error trying to parse date for %s" % url)
            date = None

        return date
    
    def extract_din(html):
        """Extracts the DIN"""

        try:
            din = html.p.string
        except:
            log.exception("Unable to extract DIN for %s" % url)
            din = ""

        # Extract the DIN
        # TO CONFIRM: is the DIN/PIN always 8 digits?
        # If so, would it be better to regex extract?
        din = din.replace("DIN/PIN Detail - ", "")
        
        log.debug("%s DIN = %s" % (url, din))

        return din

    def extract_ptc(html, subs):
        """Extracts the PTC numbers and descriptions"""
        def parse_ptc(ptcString):
            """Separates out each number and formats descriptions
            
                String is formatted with each number and description 
                on a single line. Sometimes a number will not have a
                description. The raw string is formatted into a list
                where each number is followed by the description, or 
                None in cases where there is no description. The list 
                is then padded to 8 entries (the maximum amount).
            """

            # Removes blank list entries
            rawList = []

            for line in ptcString.split("\n"):
                line = line.strip()

                if line:
                    rawList.append(line)

            # Identfies numbers vs. text to propery arrange list
            numPrev = False

            newList = []

            for line in rawList:
                # Check if this entry is a number
                # All codes have at least 4 digits
                match = re.match(r"\d{4}", line)

                # Entry is number
                if match:
                    # Check if the previous line was a number
                    if numPrev:
                        # Previous entry was number, therefore it did 
                        # not have a text description
                        newList.append(None)
                        newList.append(line)
                    else:
                        # Previous line was text, can just add number
                        newList.append(line)
                        numPrev = True
                
                # Entry is text        
                else:
                    exceptionFound = False

                    # Look to see if this text has a sub
                    sub = binary_search(subs, line)

                    # If there is a sub, apply it
                    if sub:
                        line = sub

                    # Otherwise, apply Title Case
                    else:
                        line = line.title()

                    newList.append(line)
                    numPrev = False

            # Pad list to 8 items
            while i < 8 - len(ptcList):
                newList.append(None)

            ptcList = PTC(newList)

            return ptcList
        
        try:
            ptcString = html.find_all('tr', class_="idblTable")[0]\
                            .td.div.p.get_text().strip()
        except:
            log.exception("Unable to extract PTC string for %s" % url)

        ptcList = parse_ptc(ptcString)

        return ptcList

    def extract_brand_strength_route_form(html, bsrfSubs, brandSubs, unitSubs):
        """Extracts the brand name, strenght, route, and dosage form"""
        
        def parse_brand_name(text):
            '''Properly formats the brand name'''
            sub = binary_search(text, brandSubs)

            # Checks if this text has a substitution
            if sub:
                text = sub

            # Otherwise apply regular processing
            else:
                # Convert to title text
                text = text.title()

                # Removes extra space characters
                text = re.sub(r"\s{2,}", " ", text)

                # Correct errors with apostrophes and "s"
                text = re.sub(r"'S\b", "'s", text)

            return text

        def parse_strength(text):
            '''Manually corrects errors not fixed by .lower().'''

            # Converts the strength to lower case
            text = text.lower()

            # Removes any extra spaces
            text = re.sub(r"\s{2,}", " ", text)

            # Remove any spaces around slashes
            text = re.sub(r"\s/\s", "/", text)

            # Remove any spaces between numbers and %
            text = re.sub(r"\s%\b", "%", text)

            # Applies any remaining corrections
            for sub in unitSubs:
                text = re.sub(r"\b%s\b" % sub.original, sub.correction, text)

            return text
        
        def parse_route(text):
            '''Properly formats the route'''

            # Convert route to lower case
            text = text.lower()

            return text

        def parse_dosage_form(text):
            '''Properly formats the dosage form'''

            # Convert route to lower case
            text = text.lower()

            return text
        
        def split_brand_strength_route_form(text):
            """Extracts brand name, strength, route, dosage form"""
            
            # Checks if the text has a substitution
            sub = binary_search(text, bsrfSubs)

            if sub:
                brandName = sub.brandName
                strength = sub.strength
                route = sub.route
                dosageForm = sub.dosageForm

            # If no substitution, apply regular processing
            else:
                # Splits text multiple strings depending on the format used
                # Formats vary with number of white space between sections
                match3 = r"\b\s{3}\b"
                match4 = r"\b\s{4}\b"

                # Format: B S   R    F
                if re.search(match4, text) and re.search(match3, text):
                    try:
                        text = text.split("   ")
                
                        brandStrength = text[0].strip()
                        route = text[1].strip()
                        dosageForm = text[2].strip()
                    except:
                        log.exception("Error extracting BSRF for %s" % url)

                        brandStrength = text
                        route = None
                        dosageForm = None

                # Format: B S    F
                elif re.search(match4, text):
                    try:
                        text = text.split("    ")
                    
                        brandStrength = text[0].strip()
                        route = None
                        dosageForm = text[1].strip()
                    except:
                        log.exception("Error extracting 4 space BSF for %s" 
                                      % url)

                        brandStrength = text
                        route = None
                        dosageForm = None

                # Format: B S   F
                elif re.search(match3, text):
                    try:
                        text = text.split("   ")

                        brandStrength = text[0].strip()
                        route = None
                        dosageForm = text[1].strip()
                    except:
                        log.exception("Error extracting 3 space BSF for %s" 
                                      % url)
                        
                        brandStrength = text
                        route = None
                        dosageForm = None

                # Format: B S
                else:
                    # B S
                    brandStrength = text
                    route = None
                    dosageForm = None
                
                # Splits the brandStrength at the first number 
                # encountered with a non-numeric character behind it 
                # (assumed to be a unit)
                search = re.search(r"\b\d.+$", text)

                if search:
                    split = search.start()

                    brandName = text[:split].strip()
                    strength = text[split:].strip()
                else:
                    brandName = text
                    strength = None

                # Apply final corrections to extracted information
                brandName = parse_brand_name(output[0])
                strength = parse_strength(output[1])
                route = parse_route(output[2])
                dosageForm = parse_dosage_form(output[3])
            
            output = BSRF(brandName, strength, route, dosageForm)

            return output

        try:
            bsrf = html.find_all('tr', class_="idblTable")[1]\
                       .td.div.string.strip()
        except:
            log.exception("Unable to extract BSRF string for %s" % url)
        
        bsrf = split_brand_strength_route_form(bsrf)

        return bsrf

    def extract_generic_name(html, subs):
        """Extracts the generic name"""
        def parse_generic(text):
            """Correct formatting of generic name to be lowercase"""

            # Remove parenthesis
            generic = text[1:len(text) - 1]

            # Check if this text has a substitution
            sub = binary_search(subs, generic)

            # If there is a sub, apply it
            if sub:
                generic = sub
            
            # Otherwise apply regular processing
            else:
                # Convert to lower case
                generic = generic.lower()

                # Removes extra space characters
                generic = re.sub(r"\s{2,}", " ", generic)

                # Remove spaces around slashes
                generic = re.sub(r"/\s", "/", generic)

            return generic
            
        genericText = html.find_all('tr', class_="idblTable")[2]\
                          .td.div.string.strip()
        
        generic = parse_generic(genericText)

        return generic

    def extract_date_listed(html):
        """Extracts the listing date and returns MySQL date"""
        try:
            dateText = html.find_all('tr', class_="idblTable")[3]\
                           .find_all('td')[1].string.strip()
        except:
            log.exception("Unable to extract date listed for %s" % url)

        dateListed = convert_date(dateText)

        return dateListed

    def extract_date_discontinued(html):
        """Extracts the discontinued date and returns MySQL date"""
        try:
            dateText  = html.find_all('tr', class_="idblTable")[4]\
                            .find_all('td')[1].string.strip()
        except:
            log.exception("Unable to extract discontinued date for %s" % url)

        dateDiscontinued = convert_date(dateText)
        
        return dateDiscontinued

    def extract_unit_price(html):
        """Extracts the unit price"""
        priceText = html.find_all('tr', class_="idblTable")[5]\
                        .find_all('td')[1].string.strip()

        if priceText == "N/A":
            unitPrice = None
        else:
            unitPrice = priceText

        return priceText

    def extract_lca(html):
        """Extract LCA price and any accompanying text"""
        lcaString = html.find_all('tr', class_="idblTable")[6]\
                        .find_all('td')[1].div.get_text().strip()

        # If the string has a space, it will have LCA text
        if " " in lcaString:
            if "N/A" in lcaString:
                # Note there is a weird case in the old code where
                # a line with a space and N/A, but I could not find
                # such an example; this is for theory only
                lca = None
                lcaText = lcaString[4:]
            else:
                # LCA with text - split at first space to extract
                index = lcaString.find(" ")

                lca = lcaString[0:index]
                lcaText = lcaString[index + 1:]
        # No LCA text present
        else:
            lcaText = None

            # Check if there is any price data
            if "N/A" in lcaString:
                lca = None
            else:
                lca = lcaString

        return LCA(lca, lcaText)

    def extract_unit_issue(html, subs):
        """Extracts the unit of issue"""
        unitText =  html.find_all('tr', class_="idblTable")[7]\
                        .find_all('td')[1].string.strip()

        # Unit of Issue
        unitIssue = unit_issue.lower()

        # Correct any formatting errors
        for sub in subs:
            unitIssue = re.sub(r"\b%s\b" % sub.original, 
                               sub.correction, 
                               unitIssue)

        return unitIssue

    def extract_interchangeable(html):
        """"""
        interchangeable = html.find_all('tr', class_="idblTable")[8]\
                              .find_all('td')[1].get_text()
          
        if "YES" in interchangeable:
            interchangeable = 1
        else:
            interchangeable = 0

    def extract_manufacturer(html, subs):
        """Extracts and parses the manufacturer"""
        def parse_manufactuer(text):
            '''Manually corrects errors that are not fixed by .title()'''
            
            # Check if this text has a substitution
            sub = binary_search(subs, text)

            # If there is a sub, apply it
            if sub:
                manufacturer = sub
            
            # Otherwise apply regular processing
            else:
                manufacturer = text.title()
            
                # Removes extra space characters
                manufacturer = re.sub(r"\s{2,}", " ", manufacturer)
            
            return manufacturer

        manufacturer = html.find_all('tr', class_="idblTable")[9]\
                           .find_all('td')[1].a.string.strip()

        manufacturer = parse_manufactuer(manufacturer)

        return manufacturer

    def extract_atc(html, descriptions):
        """Extracts the ATC codes and assigns description"""
        
        def parse_atc(text):
            '''Splits text into a list containing ATC codes and titles.'''
            atcList  = []

            # The regex matches to extract specific content
            searchList = [
                # Level 1: Anatomical Main Group
                "([a-zA-Z]).*$",
		
                # Level 2: Therapeutic Subgroup
                "([a-zA-Z]\d\d).*$",

                # Level 3: Pharmacological Subgroup
                "([a-zA-Z]\d\d[a-zA-Z]).*$",

                # Level 4: Chemical Subgroup
                "([a-zA-Z]\d\d[a-zA-Z][a-zA-Z]).*$",

                # Level 5: Chemical Substance
                "([a-zA-Z]\d\d[a-zA-Z][a-zA-Z]\d\d)*$"
            ]

            for search in searchList:
                match = re.match(search, text)
                
                if match:
                    code = match.group(1)
                    description = binary_search(descriptions, code)
                else:
                    code = None
                    description = None

                atcList.append(code)
                atcList.append(description)

            return atcList 

        atc = html.find_all('tr', class_="idblTable")[10]\
                  .find_all('td')[1].string.strip()

        atcList = parse_atc(atc)

        return ATC(atcList)

    def extract_schedule(html):
        """Extracts the provincial drug schedule"""
        schedule = html.find_all('tr', class_="idblTable")[11]\
                       .find_all('td')[1].string.strip()

        return schedule

    def extract_coverage(html):
        """Extract the coverage status"""
        coverage = html.find_all('tr', class_="idblTable")[12]\
                       .find_all('td')[1].string.strip()

        coverage = coverage.title()

        return coverage

    def extract_clients(html):
        """Extracts clients and converts to 1/0 representation"""

        clients = html.find_all('tr', class_="idblTable")[13]\
                      .find_all('td')[1].get_text().strip()

        # List of strings to match against
        stringList = ["(Group 1)", "(Group 66)", "(Group 66A", 
                      "Income Support", "(AISH)", "(Group 19824", 
                      "(Group 20400", "(Group 20403", "(Group 20514", 
                      "(Group 22128", "(Group 23609"]
        
        # If string is found in clients text, return 1, otherwise 0
        clientList = []

        for name in stringList:
            if name in clients:
                clientList.append(1)
            else:
                clientList.append(0)

        return Clients(clientList)

    def extract_coverage_criteria(html):
        """Extracts any coverage criteria data"""
        criteriaText = html.find_all('tr', class_="idblTable")[14]\
                           .find_all('td')[1].get_text()
        
        # Default values incase desired info is not found
        criteria = 0
        criteriaSA = None
        criteriaP = None

        if "coverage" in criteriaText:
            criteria = 1

            # Extracts the link element
            criteriaSA = html.find_all('tr', class_="idblTable")[14]\
                             .find_all('td')[1].p\
                             .find_all('a')[0]['onclick']

            # Extracts just the URL for the special auth criteria
            criteriaSA = ("https://idbl.ab.bluecross.ca/idbl/%s" %
                          re.search(r"\('(.+\d)','", criteriaSA).group(1))
            

        if "program" in criteriaText:
            criteria = 1

            # Palliative care link is always the same
            criteriaP = ("http://www.health.alberta.ca/services/"
                            "drugs-palliative-care.html")

        return CoverageCriteria(criteria, criteriaSA, criteriaP)

    def extract_special_auth():
        """Extract any special authorization links"""

        specialElem = html.find_all('tr', class_="idblTable")[15]\
                          .find_all('td')[1]
        
        specialAuth = []
      
        if "N/A" not in specialElem.get_text():
            for a in special_auth_temp.find_all('a'):
                # Grab the text for the special auth link
                text = a.string.strip()

                # Grab and format the pdf link
                link = a['onclick']
                link = ("https://idbl.ab.bluecross.ca%s" 
                        % re.search(r"\('(.+\.pdf)','", link).group(1))

                specialAuth.append(SpecialAuthorization(text, link))

        return specialAuth
        

    # Truncate extra content to improve extraction
    html = truncate_content(page)

    din = extract_din(html)
    ptc = extract_ptc(html, parseData.ptc)
    bsrf = extract_brand_strength_route_form(html, parseData.bsrf, 
                                             parseData.brand, parseData.units)
    genericName = extract_generic_name(html, parseData.generic)
    dateListed = extract_date_listed(html)
    dateDiscontinued = extract_date_discontinued(html)
    unitPrice = extract_unit_price(html)
    lca = extract_lca(html)
    unitIssue = extract_unit_issue(html, parseData.units)
    interchangeable = extract_interchangeable(html)
    manufacturer = extract_manufacturer(html, parseData.manufacturer)
    atc = extract_atc(html, parseData.atc)
    schedule = extract_schedule(html)
    coverage = extract_coverage(html)
    clients = extract_clients(html)
    coverageCriteria = extract_coverage_criteria(html)
    specialAuth = extract_special_auth(html)

    # Generate the final object
    pageContent = PageContent(
        url, page, din, ptc, brandName, strength, route, dosageForm, 
        genericName, dateListed, dateDiscontinued, unitPrice, lca, 
        unitIssue, interchangeable, manufacturer, atc, schedule, coverage, 
        clients, coverageCriteria, specialAuth)

    return pageContent


def collect_content(url, session, parseData, log):
    """Takes a list of URLs and extracts drug pricing information
        args:
            url:        url to extract data from
            session:    requests session object connected to the site
            cursor:     PyMySQL cursor to query database
            log:        a logging object to send logs to

        returns:
            content:    the PageContent object with all extracted data

        raises:
            none.
    """
    
    # Download the page content
    try:
        page = download_page(session, url)
    except Exception as e:
        log.warn("Unable to download %s content: %s"
                    % (url, e))
        page = None
        pageContent = None

    # Extract relevant information out from the page content
    if page:
        try:
            pageContent = extract_page_content(url, page, parseData, log)
        except:
            log.exception("Unable to extract %s page content" % url)
            pageContent = None

    return pageContent

def debug_data(url, htmlLoc, parseData, log):
    """Collects HTML data from provided location instead of website"""
    htmlFile = htmlLoc.child("%.html" % url).absolute()

    with open(htmlFile, "w") as html:
        page = html.read()

        try:
            pageContent = extract_page_content(url, page, parseData)
        except Exception as e:
            log.warn("Unable to extract %s page content: %s" 
                        % (url, e))
            pageContent = None
    
    return pageContent