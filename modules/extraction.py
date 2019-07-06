import logging


log = logging.getLogger(__name__) # pylint: disable=invalid-name

class URLData(object):
    def __init__(self, url_id, url, status):
        self.id = url_id
        self.url = url
        self.status = status

class PageContent(object):
    def __init__(self, url, html, din, ptc, bsrf, generic_name, date_listed,
                 date_discontinued, unit_price, lca, unit_issue,
                 interchangeable, manufacturer, atc, schedule, coverage,
                 clients, coverageCriteria, special_auth):
        self.url = url
        self.html = html
        self.din = din
        self.ptc = ptc
        self.bsrf = bsrf
        self.generic_name = generic_name
        self.date_listed = date_listed
        self.date_discontinued = date_discontinued
        self.unit_price = unit_price
        self.lca = lca
        self.unit_issue = unit_issue
        self.interchangeable = interchangeable
        self.manufacturer = manufacturer
        self.atc = atc
        self.schedule = schedule
        self.coverage = coverage
        self.clients = clients
        self.criteria = coverageCriteria
        self.special_auth = special_auth

class BasicParse(object):
    def __init__(self, parse, html):
        self.parse = parse
        self.html = html

class PTC(object):
    def __init__(self, ptcList, html, matchList):
        self.code1 = ptcList[0]
        self.text1 = ptcList[1]
        self.html1 = html[0]
        self.matched1 = matchList[0]
        self.code2 = ptcList[2]
        self.text2 = ptcList[3]
        self.html2 = html[1]
        self.matched2 = matchList[1]
        self.code3 = ptcList[4]
        self.text3 = ptcList[5]
        self.html3 = html[2]
        self.matched3 = matchList[2]
        self.code4 = ptcList[6]
        self.text4 = ptcList[7]
        self.html4 = html[3]
        self.matched4 = matchList[3]

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
    def __init__(self, atc_list, html):
        self.code1 = atc_list[0]
        self.text1 = atc_list[1]
        self.code2 = atc_list[2]
        self.text2 = atc_list[3]
        self.code3 = atc_list[4]
        self.text3 = atc_list[5]
        self.code4 = atc_list[6]
        self.text4 = atc_list[7]
        self.code5 = atc_list[8]
        self.text5 = atc_list[9]
        self.html = html

class Clients(object):
    def __init__(self, coverage_list, html):
        self.g1 = coverage_list[0]
        self.g66 = coverage_list[1]
        self.g66a = coverage_list[2]
        self.g19823 = coverage_list[3]
        self.g19823a = coverage_list[4]
        self.g19824 = coverage_list[5]
        self.g20400 = coverage_list[6]
        self.g20403 = coverage_list[7]
        self.g20514 = coverage_list[8]
        self.g22128 = coverage_list[9]
        self.g23609 = coverage_list[10]
        self.html = html

class CoverageCriteria(object):
    def __init__(self, criteria, criteriaSA, criteriaP, html):
        self.criteria = criteria
        self.special = criteriaSA
        self.palliative = criteriaP
        self.html = html

class special_authorization(object):
    def __init__(self, text, link, html):
        self.text = text
        self.link = link
        self.html = html

# ROBOT PARSING FUNCTIONS
def get_permission(user_agent):
    """Checks robots.txt for permission to crawl site"""
    from urllib import robotparser

    textURL = 'https://www.ab.bluecross.ca/robots.txt'
    pageURL = 'https://idbl.ab.bluecross.ca/idbl/load.do'

    robot = robotparser.RobotFileParser()
    robot.set_url(textURL)
    robot.read()

    can_crawl = robot.can_fetch(user_agent, pageURL)

    return can_crawl


# URL SCRAPING FUNCTIONS
def assemble_url(item_id):
    """Constructs a valid iDBL url based on the drug ID"""
    # Base URL to construct final URL from
    base = ('https://idbl.ab.bluecross.ca/idbl/'
            'lookupDinPinDetail.do?productID=')

    # Assembles the url form the base + 10 digit productID
    url = '%s%010d' % (base, item_id)

    return url

def check_url(item_id, url, session):
    """Checks the provided URL for an active status code"""
    # Request the header for the provided url
    try:
        response = session.head(url, allow_redirects=False)
        code = response.status_code
    except Exception as error:
        log.warning('Unable to retriever header for %s: %s', url, error)
        code = 0

    # Check status and create the URL Status object
    if code == 200:
        log.debug('URL %s: ACTIVE', item_id)
        status = URLData(id, url, 'active')

    elif code == 302:
        log.debug('URL %s: INACTIVE', item_id)
        status = URLData(id, url, 'inactive')

    else:
        log.warning('URL %s: Unexpected %d error', item_id, code)
        status = URLData(id, url, 'error')

    return status

def scrape_url(item_id, session):
    """Takes the provided ID # and checks if it returns active URL
        args:
            session:    a requests session to request headers
            delay:      the seconds delay between header requests
            log:        a logging object to send logs to

        returns:
            data:       a url_data object with server response data

        raises:
            none.
    """
    url = assemble_url(item_id)

    data = check_url(item_id, url, session)

    # Return the URL
    return data

def debug_url(fileLoc):
    """Returns data from text file instead of website"""
    with open(fileLoc.absolute(), 'r') as file:
        urls = file.read().split('\n')

    url_list = []

    for item_id in urls:
        if item_id:
            # Construct the full URL
            item_id = int(item_id)
            url = assemble_url(item_id)

            # Create the url_data object and append it
            url_list.append(URLData(item_id, url, 'active'))

    return url_list

def debug_url_data(html_loc):
    """Builds a url_list out of the html file names"""
    # Get all the file names in the directory
    files = html_loc.listdir(pattern='*.html', names_only=True)

    # Extracts all the ids from the file names
    id_list = []

    for file in files:
        id_list.append(int(file[:-5]))

    # Sorts the ids numerically
    id_list = sorted(id_list, key=int)

    # Creates a URL list from the sorted IDs
    url_list = []

    for item_id in id_list:
        url = assemble_url(item_id)

        # Create the url_data object and append it
        url_list.append(URLData(item_id, url, 'active'))

    return url_list


# DATA SCRAPING FUNCTIONS
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

def download_page(session, url):
    """Downloads the webpage at the provided URL"""
    response = session.get(url)
    status = response.status_code

    if status == 200:
        return response.text
    else:
        raise IOError('%s returned status code %d' % (url, status))

def extract_page_content(url, page, parse_data):
    """Takes the provided HTML page and extracts all relevant content
        args:
            url:        url to extract data from
            page:       A BeautifulSoup object with the content
                        to extract
            parse_data:  an object containing relevant data to parse
                        extracted content

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
            # Can hopefully extract on <div class="container printable">
            html = BeautifulSoup(page, 'html.parser')
            trunc = html.findAll('div', {'class': 'columnLeftFull'})[0]
        except Exception:
            log.exception('URL %s: unable to create Soup', url)

        return trunc

    def convert_date(dateString):
        """Converts the ABC date to a MySQL date format"""
        from datetime import datetime

        # If date is present, will be in form of dd-mmm-yyyy
        try:
            # Convert to date object
            date = datetime.strptime(dateString, '%d-%b-%Y')

            # Format for MySQL (yyyy-mm-dd)
            date = date.strftime('%Y-%m-%d')
        except ValueError:
            # Expected behaviour for most situations without a date
            date = None
        except Exception as error:
            log.warning('URL %s: error trying to parse date: %s', url, error)
            date = None

        return date

    def extract_din(html):
        """Extracts the DIN"""
        # Can search for DIN/NPN/PIN
        # limit by table structure
        try:
            dinText = html.p.string
            din = dinText.replace('DIN/PIN Detail - ', '')
        except Exception:
            log.critical('URL %s: unable to extract DIN', url)
            din = ''

        # Extract the DIN
        # TO CONFIRM: is the DIN/PIN always 8 digits?
        # If so, would it be better to regex extract?

        return BasicParse(din, dinText)

    def extract_ptc(html, subs):
        """Extracts the PTC numbers and descriptions"""

        def parse_ptc(ptcList):
            """Corrects formatting of description"""

            i = 1
            original = []
            matchList = []

            while i <= 7:
                if ptcList[i]:
                    # Collect original text before parsing
                    original.append(ptcList[i])

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
                    original.append(None)
                    matchList.append(False)

                i = i + 2

            return PTC(ptcList, original, matchList)

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

            for line in ptcString.split('\n'):
                line = line.strip()

                if line:
                    rawList.append(line)

            # Identfies numbers vs. text to propery arrange list
            numPrev = False

            newList = []

            for line in rawList:
                # Check if this entry is a number
                # All codes have at least 4 digits
                match = re.match(r'\d{4}', line)

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
            for _ in range(0, 8 - len(newList)):
                newList.append(None)

            return newList

        # PTC is now in a table with code and description separated
        # Also have to handle links within tables

        try:
            ptc_string = html.find_all('tr', class_='idblTable')[0]\
                            .td.div.p.get_text().strip()
        except Exception:
            log.critical('URL %s: unable to extract PTC string', url)

        ptc_strings = collect_ptc_strings(ptc_string)
        ptc_list = parse_ptc(ptc_strings)

        return ptc_list

    def extract_brand_strength_route_form(html, bsrfSubs, unitSubs):
        """Extracts the brand name, strength, route, and dosage form"""

        def parse_brand_name(text):
            """Properly formats the brand name"""
            # Convert to title text
            text = text.title()

            # Removes extra space characters
            text = re.sub(r'\s{2,}', ' ', text)

            # Correct errors with apostrophes and 's'
            text = re.sub(r"'S\b'", "'s", text)

            return text

        def parse_strength(text):
            """Manually corrects errors not fixed by .lower()."""

            # Converts the strength to lower case
            text = text.lower()

            # Removes any extra spaces
            text = re.sub(r'\s{2,}', ' ', text)

            # Remove any spaces around slashes
            text = re.sub(r'\s/\s', '/', text)

            # Remove any spaces between numbers and %
            text = re.sub(r'\s%', '%', text)

            # Applies any remaining corrections
            for sub in unitSubs:
                text = re.sub(r'\b%s\b' % sub.original, sub.correction, text)

            return text

        def parse_route(text):
            """Properly formats the route"""

            # Convert route to lower case
            text = text.lower()

            return text

        def parse_dosage_form(text):
            """Properly formats the dosage form"""

            # Convert route to lower case
            text = text.lower()

            return text

        def split_brand_strength_route_form(text):
            """Extracts brand name, strength, route, dosage form"""

            # Checks if the text has a substitution
            # Remove extra white space from searchText
            searchText = re.sub(r'\s{2,}', ' ', text)
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
                match3 = r'\S\s{3}\S'
                match4 = r'\S\s{4}\S'

                # Format: B S    R   F
                if re.search(match4, text) and re.search(match3, text):
                    try:
                        text = text.split('   ')

                        brandStrength = text[0].strip()
                        route = text[1].strip()
                        dosageForm = text[2].strip()
                    except Exception:
                        log.critical('URL %s: Error extracting BSRF', url)

                        brandStrength = text
                        route = None
                        dosageForm = None

                # Format: B S    F
                elif re.search(match4, text):
                    try:
                        text = text.split('    ')

                        brandStrength = text[0].strip()
                        route = None
                        dosageForm = text[1].strip()
                    except Exception:
                        log.critical(
                            'URL %s: Error extracting 4 space BSF', url
                        )

                        brandStrength = text
                        route = None
                        dosageForm = None

                # Format: B S   F   or   B R   F
                # Note: cannot properly extract the B R   F cases
                elif re.search(match3, text):
                    try:
                        text = text.split('   ')

                        brandStrength = text[0].strip()
                        route = None
                        dosageForm = text[1].strip()
                    except Exception:
                        log.critical(
                            'URL %s: Error extracting 3 space BSF', url
                        )

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
                search = re.search(r'\s\b[0-9,]+\D+', brandStrength)

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
                          searchText, matched)

            return output

        try:
            bsrf = html.find_all('tr', class_='idblTable')[1]\
                       .td.div.string.strip()
        except:
            log.critical('URL %s: unable to extract BSRF string' % url)

        bsrf = split_brand_strength_route_form(bsrf)

        return bsrf

    def extract_generic_name(html, subs):
        """Extracts the generic name"""
        def parse_generic(text):
            """Correct formatting of generic name to be lowercase"""
            # Remove parenthesis
            original = text[1:len(text) - 1]

            # Check if this text has a substitution
            sub = binary_search(original, subs)

            # If there is a sub, apply it
            if sub:
                generic = sub
                matched = True

            # Otherwise apply regular processing
            else:
                # Convert to lower case
                generic = original.lower()

                # Removes extra space characters
                generic = re.sub(r'\s{2,}', ' ', generic)

                # Remove spaces around slashes
                generic = re.sub(r'/\s', '/', generic)

                matched = False

            return Generic(generic, original, matched)

        try:
            genericText = html.find_all('tr', class_='idblTable')[2]\
                              .td.div.string.strip()

            generic = parse_generic(genericText)
        except:
            log.critical('URL %s: unable to extract generic name' % url)

        return generic

    def extract_date_listed(html):
        """Extracts the listing date and returns MySQL date"""
        try:
            dateText = html.find_all('tr', class_='idblTable')[3]\
                           .find_all('td')[1].string.strip()
            date_listed = convert_date(dateText)
        except:
            log.critical('URL %s: unable to extract date listed' % url)

        return BasicParse(date_listed, dateText)

    def extract_date_discontinued(html):
        """Extracts the discontinued date and returns MySQL date"""
        try:
            dateText  = html.find_all('tr', class_='idblTable')[4]\
                            .find_all('td')[1].string.strip()
            date_discontinued = convert_date(dateText)
        except:
            log.critical('URL %s: unable to extract discontinued date' % url)

        return BasicParse(date_discontinued, dateText)

    def extract_unit_price(html):
        """Extracts the unit price"""
        try:
            priceText = html.find_all('tr', class_='idblTable')[5]\
                            .find_all('td')[1].string.strip()

            if priceText == 'N/A':
                unit_price = None
            else:
                unit_price = priceText
        except:
            log.critical('URL %s: unable to extra unit price' % url)

        return BasicParse(unit_price, priceText)

    def extract_lca(html):
        """Extract LCA price and any accompanying text"""
        def parse_lca(lcaString):
            # If the string has a space, it will have LCA text
            if ' ' in lcaString:
                if 'N/A' in lcaString:
                    # Note there is a weird case in the old code where
                    # a line with a space and N/A, but I could not find
                    # such an example; this is for theory only
                    lca = None
                    lcaText = lcaString[4:].strip()
                else:
                    # LCA with text - split at first space to extract
                    index = lcaString.find(' ')

                    lca = lcaString[0:index]
                    lcaText = lcaString[index + 1:].strip()
            # No LCA text present
            else:
                lcaText = None

                # Check if there is any price data
                if 'N/A' in lcaString:
                    lca = None
                else:
                    lca = lcaString

            return LCA(lca, lcaText, lcaString)

        try:
            lcaString = html.find_all('tr', class_='idblTable')[6]\
                            .find_all('td')[1].div.get_text().strip()
            lca = parse_lca(lcaString)
        except:
            log.critical('URL: %s: unable to extract LCA' % url)

        return lca

    # TODO: MAC Pricing and comment now added - e.g. lansoprazole

    def extract_unit_issue(html, subs):
        """Extracts the unit of issue"""
        def parse_unit_issue(unitText):
            unit_issue = unitText.lower()

            return BasicParse(unit_issue, unitText)

        try:
            unitText =  html.find_all('tr', class_='idblTable')[7]\
                            .find_all('td')[1].string.strip()
            unit_issue = parse_unit_issue(unitText)
        except:
            log.critical('URL %s: unable to extract unit of issue' % url)

        return unit_issue

    def extract_interchangeable(html):
        """Extracts if drug is interchangeable or not"""
        def parse_interchange(text):
            if 'YES' in interText:
                interchangeable = 1
            else:
                interchangeable = 0

            return BasicParse(interchangeable, interText)

        try:
            interText = html.find_all('tr', class_='idblTable')[8]\
                            .find_all('td')[1].get_text()
            interchangeable = parse_interchange(interText)
        except:
            log.critical('URL %s: unable to extract interchangeable' % url)

        return interchangeable

    def extract_manufacturer(html, subs):
        """Extracts and parses the manufacturer"""
        def parse_manufactuer(text):
            """Manually corrects errors that are not fixed by .title()"""

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
                manufacturer = re.sub(r'\s{2,}', ' ', manufacturer)

                matched = False

            return Manufacturer(manufacturer, text, matched)

        try:
            manuText = html.find_all('tr', class_='idblTable')[9]\
                           .find_all('td')[1].a.string.strip()
            manufacturer = parse_manufactuer(manuText)
        except:
            log.critical('URL %s: unable to extract manufacturer' % url)

        return manufacturer

    def extract_atc(html, descriptions):
        """Extracts the ATC codes and assigns description"""

        def parse_atc(text):
            """Splits text into a list containing ATC codes and titles."""
            atcList  = []

            # The regex matches to extract specific content
            searchList = [
                # Level 1: Anatomical Main Group
                r'([a-zA-Z]).*$',

                # Level 2: Therapeutic Subgroup
                r'([a-zA-Z]\d\d).*$',

                # Level 3: Pharmacological Subgroup
                r'([a-zA-Z]\d\d[a-zA-Z]).*$',

                # Level 4: Chemical Subgroup
                r'([a-zA-Z]\d\d[a-zA-Z][a-zA-Z]).*$',

                # Level 5: Chemical Substance
                r'([a-zA-Z]\d\d[a-zA-Z][a-zA-Z]\d\d)*$'
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

        try:
            atcText = html.find_all('tr', class_='idblTable')[10]\
                      .find_all('td')[1].string.strip()
            atcList = parse_atc(atcText)
            atc = ATC(atcList, atcText)
        except:
            log.critical('URL %s: unable to extract ATC' % url)

        return atc

    def extract_schedule(html):
        """Extracts the provincial drug schedule"""
        try:
            schedText = html.find_all('tr', class_='idblTable')[11]\
                            .find_all('td')[1].string.strip()
            schedule = BasicParse(schedText, schedText)
        except:
            log.critical('URL %s: unable to extract schedule' % url)

        return schedule

    def extract_coverage(html):
        """Extract the coverage status"""
        def parse_coverage(text):
            coverage = text.title()

            return BasicParse(coverage, text)

        try:
            coverageText = html.find_all('tr', class_='idblTable')[12]\
                               .find_all('td')[1].string.strip()
            coverage = parse_coverage(coverageText)
        except:
            log.critical('URL %s: unable to extract coverage' % url)

        return coverage

    def extract_clients(html):
        """Extracts clients and converts to 1/0 representation"""
        def parse_clients(clientText):
            # List of strings to match against
            stringList = ['(Group 1)', '(Group 66)', '(Group 66A',
                          'Income Support', '(AISH)', '(Group 19824',
                          '(Group 20400', '(Group 20403', '(Group 20514',
                          '(Group 22128', '(Group 23609']

            # If string is found in clients text, return 1, otherwise 0
            clientList = []

            for name in stringList:
                if name in clientText:
                    clientList.append(1)
                else:
                    clientList.append(0)

            return Clients(clientList, clientText)

        try:
            clientText = html.find_all('tr', class_='idblTable')[13]\
                             .find_all('td')[1].get_text().strip()
            clients = parse_clients(clientText)
        except:
            log.critical('URL %s: unable to extract clients' % url)

        return clients

    def extract_coverage_criteria(html):
        """Extracts any coverage criteria data"""
        def parse_criteria(criteriaText):
            # Default values incase desired info is not found
            criteria = 0
            criteriaSA = None
            criteriaP = None

            if 'coverage' in criteriaText:
                criteria = 1

                # Extracts the link element
                criteriaSA = html.find_all('tr', class_='idblTable')[14]\
                                 .find_all('td')[1].p\
                                 .find_all('a')[0]['onclick']

                # Extracts just the URL for the special auth criteria
                criteriaSA = ('https://idbl.ab.bluecross.ca/idbl/%s' %
                              re.search(r"\('(.+\d)",'', criteriaSA).group(1))


            if 'program' in criteriaText:
                criteria = 1

                # Palliative care link is always the same
                criteriaP = ('http://www.health.alberta.ca/services/'
                                'drugs-palliative-care.html')

            return CoverageCriteria(criteria, criteriaSA, criteriaP,
                                    criteriaText)

        try:
            criteriaText = html.find_all('tr', class_='idblTable')[14]\
                               .find_all('td')[1].get_text()
            criteria = parse_criteria(criteriaText)
        except:
            log.critical('URL %s: unable to extract criteria' % url)

        return criteria

    def extract_special_auth(html):
        """Extract any special authorization links"""
        def parse_special(elem):
            special_auth = []

            if 'N/A' not in elem.get_text():
                for a in elem.find_all('a'):
                    # Grab the text for the special auth link
                    text = a.string.strip()

                    # Grab and format the pdf link
                    link = a['onclick']
                    link = ('https://idbl.ab.bluecross.ca%s'
                            % re.search(r"\('(.+\.pdf)",'', link).group(1))

                    special_auth.append(
                        special_authorization(text, link, elem)
                    )

            return special_auth

        # the parent P containing the link has a data attribute data-pdf
        # data-pdf contains the pdf name (e.g. 60001.pdf)
        # https://idbl.ab.bluecross.ca/idbl/DBL/ + pdf name

        try:
            specialElem = html.find_all('tr', class_='idblTable')[15]\
                              .find_all('td')[1]
            special_auth = parse_special(specialElem)
        except:
            log.critical('URL %s: unable to extract special authorization'
                         % url)

        return special_auth


    # Truncate extra content to improve extraction
    html = truncate_content(page)

    din = extract_din(html)
    ptc = extract_ptc(html, parse_data.ptc)
    bsrf = extract_brand_strength_route_form(html, parse_data.bsrf,
                                             parse_data.units)
    generic_name = extract_generic_name(html, parse_data.generic)
    date_listed = extract_date_listed(html)
    date_discontinued = extract_date_discontinued(html)
    unit_price = extract_unit_price(html)
    lca = extract_lca(html)
    unit_issue = extract_unit_issue(html, parse_data.units)
    interchangeable = extract_interchangeable(html)
    manufacturer = extract_manufacturer(html, parse_data.manufacturer)
    atc = extract_atc(html, parse_data.atc)
    schedule = extract_schedule(html)
    coverage = extract_coverage(html)
    clients = extract_clients(html)
    coverageCriteria = extract_coverage_criteria(html)
    special_auth = extract_special_auth(html)

    # Generate the final object
    pageContent = PageContent(
        url, page, din, ptc, bsrf, generic_name, date_listed, date_discontinued,
        unit_price, lca, unit_issue, interchangeable, manufacturer, atc,
        schedule, coverage, clients, coverageCriteria, special_auth
    )

    return pageContent

def collect_content(url_data, session, parse_data):
    """Extracts the page content from the provided url
        args:
            url_data:    a URL data object with the url to extract
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
        page = download_page(session, url_data.url)
        log.debug('URL %s: page downloaded successfully' % url_data.id)
    except Exception as error:
        log.warning('{} - URL {}: unable to download content'.format(e, url_data.id))
        page = None
        pageContent = None

    # Extract relevant information out from the page content
    if page:
        try:
            pageContent = extract_page_content(url_data.id, page, parse_data, log)
            log.debug('URL %s: content extracted successfully' % url_data.id)
        except:
            log.exception('URL %s: unable to extract content' % url_data.id)
            pageContent = None

    return pageContent

def debug_data(url_data, html_loc, parse_data, log):
    """Collects HTML data from provided location instead of website"""
    htmlFile = html_loc.child('%s.html' % url_data.id).absolute()
    log.debug('File %s.html: extracting data' % url_data.id)

    with open(htmlFile, 'r') as html:
        page = html.read()

        try:
            pageContent = extract_page_content(url_data.id, page, parse_data,
                                               log)
        except Exception as error:
            log.warning('File %s: unable to extract page content: %s'
                        % (url_data.id, e))
            pageContent = None

    return pageContent

def extract_data(abc_id, session, settings):
    """Manages extraction of iDBL details."""
