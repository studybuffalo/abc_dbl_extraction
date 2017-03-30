class PageContent(object):
    def __init__(self, url, html, din, ptc, bsrf, genericName, dateListed, 
                 dateDiscontinued, unitPrice, lca, unitIssue, 
                 interchangeable, manufacturer, atc, schedule, coverage, 
                 clients, coverageCriteria, specialAuth):
        self.url = url
        self.html = html
        self.din = din
        self.ptc = ptc
        self.bsrf = bsrf
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


class BasicParse(object):
    def __init__(self, parse, html):
        self.parse = parse
        self.html = html


class PTC(object):
    def __init__(self, ptcList, html, matchList):
        self.code1 = ptcList[0]
        self.text1 = ptcList[1]
        self.matched1 = matchList[0]
        self.code2 = ptcList[2]
        self.text2 = ptcList[3]
        self.matched2 = matchList[1]
        self.code3 = ptcList[4]
        self.text3 = ptcList[5]
        self.matched3 = matchList[2]
        self.code4 = ptcList[6]
        self.text4 = ptcList[7]
        self.matched4 = matchList[3]
        self.html = html


class BSRF(object):
    def __init__(self, brand, strength, route, form, html, matched):
        self.brand = brand
        self.strength = strength
        self.route = route
        self.form = form
        self.html = html
        self.matched = matched


class Generic(object):
    def __init__(self, parse, html, matched):
        self.parse = parse
        self.html = html
        self.matched = matched


class LCA(object):
    def __init__(self, value, text, html):
        self.value = value
        self.text = text
        self.html = html


class Manufacturer(object):
    def __init__(self, parse, html, matched):
        self.parse = parse
        self.html = html
        self.matched = matched


class ATC(object):
    def __init__(self, atcList, html):
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
        self.html = html


class Clients(object):
    def __init__(self, list, html):
        self.g1 = list[0]
        self.g66 = list[1]
        self.g66a = list[2]
        self.g19823 = list[3]
        self.g19823a = list[4]
        self.g19824 = list[5]
        self.g20400 = list[6]
        self.g20403 = list[7]
        self.g20514 = list[8]
        self.g22128 = list[9]
        self.g23609 = list[10]
        self.html = html


class CoverageCriteria(object):
    def __init__(self, criteria, criteriaSA, criteriaP, html):
        self.criteria = criteria
        self.special = criteriaSA
        self.palliative = criteriaP
        self.html = html


class SpecialAuthorization(object):
    def __init__(self, text, link, html):
        self.text = text
        self.link = link
        self.html = html


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
    from bisect import bisect_left

    searchList = lists.original
    returnList = lists.correction
    
    # Look for match
    i = bisect_left(searchList, term)

    # If match found, return the corresponding object
    if i != len(searchList) and searchList[i] == term:
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
        from datetime import datetime

        # If date is present, will be in form of dd-mmm-yyyy
        try:
            # Convert to date object
            date = datetime.strptime(dateString, "%d-%b-%Y")

            # Format for MySQL (yyyy-mm-dd)
            date = date.strftime("%y-%m-%d")
        except ValueError:
            # Expected behaviour for most situations without a date
            date = None
        except Exception as e:
            log.warn("Error trying to parse date for %s - %s" % (url, e))
            date = None

        return date
    
    def extract_din(html):
        """Extracts the DIN"""

        try:
            dinText = html.p.string
            din = dinText.replace("DIN/PIN Detail - ", "")
        except:
            log.exception("Unable to extract DIN for %s" % url)
            din = ""

        # Extract the DIN
        # TO CONFIRM: is the DIN/PIN always 8 digits?
        # If so, would it be better to regex extract?
        
        return BasicParse(din, dinText)

    def extract_ptc(html, subs):
        """Extracts the PTC numbers and descriptions"""

        def parse_ptc(ptcList, html):
            """Corrects formatting of description"""
            i = 1
            matchList = []

            while i <= 7:
                if ptcList[i]:
                    # Look to see if this text has a sub
                    sub = binary_search(ptcList[i], subs)

                    # If there is a sub, apply it
                    if sub:
                        ptcList[i] = sub
                        matchList.append(True)

                    # Otherwise, apply Title Case
                    else:
                        ptcList[i] = ptcList[i].title()
                        matchList.append(False)
                else:
                    matchList.append(False)

                i = i + 2

            return PTC(ptcList, html, matchList)

        def collect_ptc_strings(ptcString):
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
                    newList.append(line)
                    numPrev = False

            # Pad list to 8 items
            for i in range(0, 8 - len(newList)):
                newList.append(None)

            return newList
        
        try:
            ptcString = html.find_all('tr', class_="idblTable")[0]\
                            .td.div.p.get_text().strip()
        except:
            log.exception("Unable to extract PTC string for %s" % url)

        ptcStrings = collect_ptc_strings(ptcString)
        ptcList = parse_ptc(ptcStrings, ptcString)

        return ptcList

    def extract_brand_strength_route_form(html, bsrfSubs, unitSubs):
        """Extracts the brand name, strength, route, and dosage form"""

        def parse_brand_name(text):
            """Properly formats the brand name"""
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
            text = re.sub(r"\s%", "%", text)

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
        
        def split_brand_strength_route_form(text, html):
            """Extracts brand name, strength, route, dosage form"""
            
            # Checks if the text has a substitution
            # Remove extra white space from searchText
            searchText = re.sub("\s{2,}", " ", text)
            sub = binary_search(searchText, bsrfSubs)

            if sub:
                brandName = sub.brandName
                strength = sub.strength
                route = sub.route
                dosageForm = sub.dosageForm
                matched = True

            # If no substitution, apply regular processing
            else:
                # Splits text multiple strings depending on the format 
                # used
                # Formats vary with number of white space between 
                # sections
                match3 = r"\S\s{3}\S"
                match4 = r"\S\s{4}\S"

                # Format: B S    R   F
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

                # Format: B S   F   or   B R   F
                # Note: cannot properly extract the B R   F cases
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
                # (excluding commas in numbers, as this is assumed
                # to be a unit)
                search = re.search(r"\s\b[0-9,]+\D+", brandStrength)

                if search:
                    split = search.start()

                    brandName = brandStrength[:split].strip()
                    strength = brandStrength[split:].strip()
                else:
                    brandName = brandStrength
                    strength = None

                # Apply final corrections to extracted information
                if brandName:
                    brandName = parse_brand_name(brandName)

                if strength:
                    strength = parse_strength(strength)

                if route:
                    route = parse_route(route)

                if dosageForm:
                    dosageForm = parse_dosage_form(dosageForm)
            
                # Flags html as not having sub match
                matched = False


            output = BSRF(brandName, strength, route, dosageForm, 
                          html, matched)

            return output

        try:
            bsrf = html.find_all('tr', class_="idblTable")[1]\
                       .td.div.string.strip()
        except:
            log.exception("Unable to extract BSRF string for %s" % url)
        
        bsrf = split_brand_strength_route_form(bsrf, bsrf)

        return bsrf

    def extract_generic_name(html, subs):
        """Extracts the generic name"""
        def parse_generic(text, html):
            """Correct formatting of generic name to be lowercase"""

            # Remove parenthesis
            generic = text[1:len(text) - 1]

            # Check if this text has a substitution
            sub = binary_search(generic, subs)

            # If there is a sub, apply it
            if sub:
                generic = sub
                matched = True
            
            # Otherwise apply regular processing
            else:
                # Convert to lower case
                generic = generic.lower()

                # Removes extra space characters
                generic = re.sub(r"\s{2,}", " ", generic)

                # Remove spaces around slashes
                generic = re.sub(r"/\s", "/", generic)

                matched = False

            return Generic(generic, html, matched)
            
        genericText = html.find_all('tr', class_="idblTable")[2]\
                          .td.div.string.strip()
        
        generic = parse_generic(genericText, genericText)

        return generic

    def extract_date_listed(html):
        """Extracts the listing date and returns MySQL date"""
        try:
            dateText = html.find_all('tr', class_="idblTable")[3]\
                           .find_all('td')[1].string.strip()
        except:
            log.exception("Unable to extract date listed for %s" % url)

        dateListed = convert_date(dateText)

        return BasicParse(dateListed, dateText)

    def extract_date_discontinued(html):
        """Extracts the discontinued date and returns MySQL date"""
        try:
            dateText  = html.find_all('tr', class_="idblTable")[4]\
                            .find_all('td')[1].string.strip()
        except:
            log.exception("Unable to extract discontinued date for %s" % url)

        dateDiscontinued = convert_date(dateText)
        
        return BasicParse(dateDiscontinued, dateText)

    def extract_unit_price(html):
        """Extracts the unit price"""
        priceText = html.find_all('tr', class_="idblTable")[5]\
                        .find_all('td')[1].string.strip()

        if priceText == "N/A":
            unitPrice = None
        else:
            unitPrice = priceText

        return BasicParse(unitPrice, priceText)

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
                lcaText = lcaString[4:].strip()
            else:
                # LCA with text - split at first space to extract
                index = lcaString.find(" ")

                lca = lcaString[0:index]
                lcaText = lcaString[index + 1:].strip()
        # No LCA text present
        else:
            lcaText = None

            # Check if there is any price data
            if "N/A" in lcaString:
                lca = None
            else:
                lca = lcaString

        return LCA(lca, lcaText, lcaString)

    def extract_unit_issue(html, subs):
        """Extracts the unit of issue"""
        unitText =  html.find_all('tr', class_="idblTable")[7]\
                        .find_all('td')[1].string.strip()

        # Unit of Issue
        unitIssue = unitText.lower()

        return BasicParse(unitIssue, unitText)

    def extract_interchangeable(html):
        """Extracts if drug is interchangeable or not"""
        interText = html.find_all('tr', class_="idblTable")[8]\
                              .find_all('td')[1].get_text()
          
        if "YES" in interText:
            interchangeable = 1
        else:
            interchangeable = 0

        return BasicParse(interchangeable, interText)

    def extract_manufacturer(html, subs):
        """Extracts and parses the manufacturer"""
        def parse_manufactuer(text):
            '''Manually corrects errors that are not fixed by .title()'''
            
            # Check if this text has a substitution
            sub = binary_search(text, subs)

            # If there is a sub, apply it
            if sub:
                manufacturer = sub
                matched = True
            
            # Otherwise apply regular processing
            else:
                manufacturer = text.title()
            
                # Removes extra space characters
                manufacturer = re.sub(r"\s{2,}", " ", manufacturer)

                matched = False
            
            return Manufacturer(manufacturer, text, matched)

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
                    description = binary_search(code, descriptions)
                else:
                    code = None
                    description = None

                atcList.append(code)
                atcList.append(description)

            return atcList 

        atc = html.find_all('tr', class_="idblTable")[10]\
                  .find_all('td')[1].string.strip()

        atcList = parse_atc(atc)

        return ATC(atcList, atc)

    def extract_schedule(html):
        """Extracts the provincial drug schedule"""
        schedule = html.find_all('tr', class_="idblTable")[11]\
                       .find_all('td')[1].string.strip()

        return BasicParse(schedule, schedule)

    def extract_coverage(html):
        """Extract the coverage status"""
        coverageText = html.find_all('tr', class_="idblTable")[12]\
                           .find_all('td')[1].string.strip()

        coverage = coverageText.title()

        return BasicParse(coverage, coverageText)

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

        return Clients(clientList, clients)

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

        return CoverageCriteria(criteria, criteriaSA, criteriaP, criteriaText)

    def extract_special_auth(html):
        """Extract any special authorization links"""

        specialElem = html.find_all('tr', class_="idblTable")[15]\
                          .find_all('td')[1]
        
        specialAuth = []
      
        if "N/A" not in specialElem.get_text():
            for a in specialElem.find_all('a'):
                # Grab the text for the special auth link
                text = a.string.strip()

                # Grab and format the pdf link
                link = a['onclick']
                link = ("https://idbl.ab.bluecross.ca%s" 
                        % re.search(r"\('(.+\.pdf)','", link).group(1))

                specialAuth.append(
                    SpecialAuthorization(text, link, specialElem)
                )

        return specialAuth
        

    # Truncate extra content to improve extraction
    html = truncate_content(page)

    din = extract_din(html)
    ptc = extract_ptc(html, parseData.ptc)
    bsrf = extract_brand_strength_route_form(html, parseData.bsrf, 
                                             parseData.units)
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
        url, page, din, ptc, bsrf, genericName, dateListed, dateDiscontinued, 
        unitPrice, lca, unitIssue, interchangeable, manufacturer, atc, 
        schedule, coverage, clients, coverageCriteria, specialAuth
    )

    return pageContent


def collect_content(urlData, session, parseData, log):
    """Extracts the page content from the provided url
        args:
            urlData:    a URL data object with the url to extract
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
        page = download_page(session, urlData.url)
    except Exception as e:
        log.warn("Unable to download %s content: %s"
                    % (urlData.id, e))
        page = None
        pageContent = None

    # Extract relevant information out from the page content
    if page:
        try:
            pageContent = extract_page_content(urlData.id, page, parseData, 
                                               log)
        except:
            log.exception("Unable to extract %s page content" % urlData.id)
            pageContent = None

    return pageContent


def debug_data(urlData, htmlLoc, parseData, log):
    """Collects HTML data from provided location instead of website"""
    htmlFile = htmlLoc.child("%s.html" % urlData.id).absolute()
    log.debug("Extracting data from %s" % htmlFile)

    with open(htmlFile, "r") as html:
        page = html.read()

        try:
            pageContent = extract_page_content(urlData.id, page, parseData, 
                                               log)
        except Exception as e:
            log.warn("Unable to extract %s page content: %s" 
                        % (urlData.id, e))
            pageContent = None
    
    return pageContent