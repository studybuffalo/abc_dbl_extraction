"""Functions to handle data extraction from iDBL."""
from datetime import datetime
from pathlib import Path
import time

import click
from bs4 import BeautifulSoup

from modules.exceptions import ExtractionError


class IDBLData:
    """Object to handle iDBL data."""
    def __init__(self, abc_id, html):
        self.abc_id = abc_id
        self.raw_html = html
        self.html = self.extract_relevant_html(html)
        self.data = {}

    @staticmethod
    def extract_relevant_html(html):
        """Extracts the relevant section from raw HTML.

            Parameters:
                html (str): the raw HTML page.

            Returns:
                obj: the relevant HTML as a BeautifulSoup object.
        """
        soup = BeautifulSoup(html, 'lxml')

        return soup.find(id='theContent').find(class_='container printable')

    def extract_data(self): # pylint: disable=too-many-locals
        """Extracts data from the HTML page."""
        din = self._extract_din()
        bsrf = self._extract_bsrf()
        generic_name = self._extract_generic_name()
        ptc = self._extract_ptc()
        date_listed = self._extract_date_listed()
        unit_price = self._extract_unit_price()
        lca_price = self._extract_lca_price()
        mac_price, mac_text = self._extract_mac()
        unit_of_issue = self._extract_unit_of_issue()
        manufactuer = self._extract_manufacturer()
        atc = self._extract_atc()
        schedule = self._extract_schedule()
        interchangeable = self._extract_interchangeable()
        coverage_status = self._extract_coverage_status()
        clients = self._extract_clients()
        special_authorization = self._extract_special_authorization()
        coverage_criteria = self._extract_coverage_criteria()

        self.data = {
            'din': din,
            'abc_id': self.abc_id,
            'bsrf': bsrf,
            'generic_name': generic_name,
            'ptc': ptc,
            'date_listed': date_listed,
            'unit_price': unit_price,
            'lca_price': lca_price,
            'mac_price': mac_price,
            'mac_text': mac_text,
            'unit_of_issue': unit_of_issue,
            'manufacturer': manufactuer,
            'atc': atc,
            'schedule': schedule,
            'interchangeable': interchangeable,
            'coverage_status': coverage_status,
            'clients': clients,
            'special_authorization': special_authorization,
            'coverage_criteria': coverage_criteria,
        }

    def _extract_din(self):
        """Extracts the DIN."""
        din_element = self.html.find(
            class_='abc-search-header'
        ).table.tr.td.find_all(
            'span'
        )[0]

        din = din_element.text.strip().split()[1]

        return din

    def _extract_bsrf(self):
        """Extracts the brand name, strength, route, and form (BSRF)."""
        bsrf_element = self.html.find(
            class_='abc-search-header'
        ).table.tr.td.find_all(
            'span'
        )[1]

        bsrf = bsrf_element.text.strip()

        return bsrf

    def _extract_generic_name(self):
        """Extracts the generic name."""
        generic_element = self.html.find(
            class_='abc-search-header'
        ).table.tr.td.find_all(
            'span'
        )[2]

        generic_name = generic_element.text.strip()

        return generic_name

    def _extract_ptc(self):
        """Extracts the most accurate PTC code."""
        ptc_elements = self.html.find(
            class_='abc-drug-detail-table'
        ).find_all(
            'tr', recursive=False
        )[1].table.find_all(
            'tr'
        )[-1].td

        ptc = list(ptc_elements.stripped_strings)[0]

        return ptc

    def _extract_date_listed(self):
        """Extracts the listing date.

            Dates are extracted in the format DD-MMM-YYYY and returned
            as datetime object.
        """
        date_listed_element = self.html.find(
            class_='abc-drug-detail-table'
        ).find_all(
            'tr', recursive=False
        )[2].find_all(
            'td', recursive=False
        )[1]

        date_listed_text = date_listed_element.text.strip()

        try:
            date_listed = datetime.strptime(
                date_listed_text, '%d-%b-%Y'
            ).strftime('%Y-%m-%d')
        except (ValueError, AttributeError):
            date_listed = None

        return date_listed

    def _extract_unit_price(self):
        """Extracts the unit price"""
        unit_price_element = self.html.find(
            class_='abc-drug-detail-table'
        ).find_all(
            'tr', recursive=False
        )[4].find_all(
            'td', recursive=False
        )[1]

        unit_price = unit_price_element.text.strip().replace(',', '')

        if unit_price == 'N/A':
            unit_price = None

        return unit_price

    def _extract_lca_price(self):
        """Extract LCA price and any accompanying text"""
        lca_price_element = self.html.find(
            class_='abc-drug-detail-table'
        ).find_all(
            'tr', recursive=False
        )[5].find_all(
            'td', recursive=False
        )[1]

        lca_price = lca_price_element.text.strip().replace(',', '')

        if lca_price == 'N/A':
            lca_price = None

        return lca_price

    def _extract_mac(self):
        """Extracts the MAC price and any associated text."""
        mac_element = self.html.find(
            class_='abc-drug-detail-table'
        ).find_all(
            'tr', recursive=False
        )[6].find_all(
            'td', recursive=False
        )[1].find_all(
            'p', recursive=False
        )

        # Extract MAC price (if available)
        mac_price = mac_element[0].text.strip().replace(',', '')

        if mac_price == 'N/A':
            mac_price = None

        # Extract any MAC price comments (if available)
        try:
            mac_text = mac_element[1].text.strip()
        except IndexError:
            mac_text = None

        return mac_price, mac_text

    def _extract_unit_of_issue(self):
        """Extracts the unit of issue."""
        unit_of_issue_element = self.html.find(
            class_='abc-drug-detail-table'
        ).find_all(
            'tr', recursive=False
        )[8].find_all(
            'td', recursive=False
        )[1]

        unit_of_issue = unit_of_issue_element.text.strip()

        return unit_of_issue

    def _extract_manufacturer(self):
        """Extracts the manufacturer."""
        manufacturer_element = self.html.find(
            class_='abc-drug-detail-table'
        ).find_all(
            'tr', recursive=False
        )[9].find_all(
            'td', recursive=False
        )[1]

        manufacturer = list(manufacturer_element.stripped_strings)[0]

        return manufacturer

    def _extract_atc(self):
        """Extracts the ATC code."""
        atc_element = self.html.find(
            class_='abc-drug-detail-table'
        ).find_all(
            'tr', recursive=False
        )[10].find_all(
            'td', recursive=False
        )[1]

        atc = atc_element.text.strip()

        return atc

    def _extract_schedule(self):
        """Extracts the provincial drug schedule."""
        schedule_element = self.html.find(
            class_='abc-drug-detail-table'
        ).find_all(
            'tr', recursive=False
        )[11].find_all(
            'td', recursive=False
        )[1]

        schedule = schedule_element.text.strip()

        return schedule

    def _extract_interchangeable(self):
        """Extracts if drug is interchangeable or not"""
        interchangeable_element = self.html.find(
            class_='abc-drug-detail-table'
        ).find_all(
            'tr', recursive=False
        )[12].find_all(
            'td', recursive=False
        )[1]

        interchangeable_string = list(
            interchangeable_element.stripped_strings
        )[0]

        # Convert response to boolean
        interchangeable = interchangeable_string.upper() == 'YES'

        return interchangeable

    def _extract_coverage_status(self):
        """Extract the coverage status"""
        coverage_status_element = self.html.find_all(
            class_='abc-drug-detail-table'
        )[1].find_all(
            'tr', recursive=False
        )[0].find_all(
            'td', recursive=False
        )[1]

        coverage_status = coverage_status_element.text.strip().title()

        return coverage_status

    def _extract_clients(self):
        """Extracts and determines which clients are present."""
        clients_elements = list(
            self.html.find_all(
                class_='abc-drug-detail-table'
            )[1].find_all(
                'tr', recursive=False
            )[1].find_all(
                'td', recursive=False
            )[1].stripped_strings
        )

        clients = {
            'group_1': False,
            'group_66': False,
            'group_19823': False,
            'group_19823a': False,
            'group_19824': False,
            'group_20400': False,
            'group_20403': False,
            'group_20514': False,
            'group_22128': False,
            'group_23609': False,
        }

        # Checks if any elements present
        if clients_elements[0] == 'N/A':
            return clients

        # Strings to match upon to see if group is present
        client_matches = [
            ['non-group coverage', 'group_1'],
            ['coverage for seniors', 'group_66'],
            ['income support', 'group_19823'],
            ['alberta human services', 'group_19823a'],
            ['children and youth services', 'group_19824'],
            ['alberta child health benefit', 'group_20400'],
            ['child and family services', 'group_20403'],
            ['palliative coverage', 'group_20514'],
            ['learners program', 'group_22128'],
            ['alberta adult health benefit', 'group_23609'],
        ]

        # Loops through elements and checks which groups are present
        for client in clients_elements:
            for match in client_matches:
                if match[0] in client.lower():
                    clients[match[1]] = True

        return clients

    def _extract_special_authorization(self):
        """Extract special authorization links and titles."""
        special_elements = self.html.find_all(
            class_='abc-drug-detail-table'
        )[1].find_all(
            'tr', recursive=False
        )[2].find_all(
            'td', recursive=False
        )[1].find_all(
            'p', recursive=False,
        )

        special_authorizations = []

        if list(special_elements[0].stripped_strings)[0] == 'N/A':
            return special_authorizations

        for element in special_elements:
            file_name = element['data-pdf']
            pdf_title = list(element.stripped_strings)[0]

            special_authorizations.append({
                'file_name': file_name,
                'pdf_title': pdf_title,
            })

        return special_authorizations

    def _extract_coverage_criteria(self):
        """Extracts any coverage criteria data"""
        criteria_elements = self.html.find_all(
            class_='abc-drug-detail-table'
        )[1].find_all(
            'tr', recursive=False
        )[3].find_all(
            'td', recursive=False
        )

        criteria = []

        # Extract all text from the first TD element
        title_text = ''.join(
            list(criteria_elements[0].stripped_strings)
        ).lower()

        # Check for 'expand all' in first cell
        # If absent: single element to assess in sibling cell
        # If present: multiple elements need to  extracte in next row
        if 'expand all' not in title_text:
            # Get the paragraph elements from table cell
            criteria_paragraphs = criteria_elements[1].find_all(
                'p', recursive=False
            )

            # Check number of paragraphs
            # If 2: this is "N/A" and can return empty list
            # if 1: this has extractable content
            if len(criteria_paragraphs) == 2:
                return criteria

            # Extract text and preserve <br> elements
            criteria_text = criteria_paragraphs[0].contents
            criteria_text = ''.join(str(text) for text in criteria_text)

            criteria.append({
                'header': None,
                'criteria': criteria_text,
            })

            return criteria

        # Otherwise, handle multiple criteria elements
        criteria_elements = self.html.find_all(
            class_='abc-drug-detail-table'
        )[1].find_all(
            'tr', recursive=False
        )[4].td.find_all(
            'div', recursive=False
        )

        # Loop over all elements and extract details
        for element in criteria_elements:
            criteria_divs = element.find_all('div', recursive=False)
            criteria_header = list(criteria_divs[0].stripped_strings)[0]
            criteria_text = str(criteria_divs[1].div).strip()
            criteria.append({
                'header': criteria_header,
                'criteria': criteria_text,
            })

        return criteria

def assemble_idbl_url(settings, abc_id):
    """Assembles a URL to query the iDBL."""
    return '{}?detailId={}'.format(settings['abc_url'], abc_id)

def extract_from_file(abc_id, path):
    """Retrieves HTML data from file."""
    file_path = Path(path, str(abc_id)).with_suffix('.html')

    try:
        with open(file_path, 'rb') as idbl_file:
            return idbl_file.read()
    except FileNotFoundError:
        # Expected errors if files don't exist
        pass

    return None

def extract_from_idbl(abc_id, session, settings):
    """Retrieves HTML data from iDBL."""
    # Assemble URL
    abc_url = '{}?detailId={}'.format(settings['abc_url'], abc_id)

    # Check for a 200 status code
    head_response = session.head(abc_url, allow_redirects=False)

    if head_response.status_code == 200:
        body_response = session.get(abc_url, allow_redirects=False)

        if body_response.status_code == 200:
            return body_response.text

    return None

def extract_data(abc_id, session, settings):
    """Manages extraction of iDBL details."""
    # Obtain the HTML content
    if settings['files']['use_html']:
        html = extract_from_file(abc_id, settings['files']['use_html'])
    else:
        html = extract_from_idbl(abc_id, session, settings)

    if html:
        # Extract relevant content from HTML
        idbl_data = IDBLData(abc_id, html)
        idbl_data.extract_data()

        return idbl_data

    return None

def assemble_console_message(base, counter):
    """Updates console to show program still running."""
    spinner = ['.  ', '.. ', '...']

    click.echo('\r{}{}'.format(base, spinner[counter % 3]), nl=False)

    return counter + 1

def overflow_check(counter):
    """Runs check that the overflow condition is not triggered."""
    if counter > 20:
        raise ExtractionError(
            'Endpoint extraction overflow counter triggered.'
        )

    return counter + 1

def identify_endpoint(target, session, settings, lower, upper):
    """Identifies exact endpoint between  upper and lower limits."""
    endpoint = None # Records the last iDBL hit
    overflow_counter = 0 # Counter to prevent a infinite loop

    # Setup console messaging
    echo_message = 'Identifying initial {} point ID'.format(target)
    echo_counter = 0

    while upper - lower > 1:
        # Check program has not entered infinite loop
        overflow_counter = overflow_check(overflow_counter)

        # Apply crawl delay and update console
        time.sleep(settings['crawl_delay'])
        echo_counter = assemble_console_message(echo_message, echo_counter)

        # Get the midpoint
        mid = int((upper + lower) / 2)

        # Check for a 200 status code
        abc_url = assemble_idbl_url(settings, mid)
        head_response = session.head(abc_url, allow_redirects=False)

        if head_response.status_code == 200:
            # Positive hit
            endpoint = mid

            if target == 'start':
                # Looking for start point - upper needs to be lowered
                upper = mid
            else:
                # Looking for end point - lower needs to be increased
                lower = mid
        else:
            # Negative hit
            if target == 'start':
                # Looking for start point - lower needs to be increased
                lower = mid
            else:
                # Looking for end point - upper needs to be decreased
                upper = mid

    # Update console
    click.echo('\r{}{}'.format(echo_message, '...'), nl=False)
    click.echo(click.style(' {}'.format(endpoint), fg='green'))

    return endpoint

def identify_payload(session, settings, start, end, step):
    """Identifies location of the iDBL payload."""
    idbl_hit = None

    # Setup console messaging
    echo_message = 'Identifying initial payload'
    echo_counter = 0

    # Increment from start ID until a 200 response obtained
    for i in range(start, end, step):
        # Apply crawl delay and update console
        time.sleep(settings['crawl_delay'])
        echo_counter = assemble_console_message(echo_message, echo_counter)

        # Check for a 200 status code
        abc_url = assemble_idbl_url(settings, i)
        head_response = session.head(abc_url, allow_redirects=False)

        if head_response.status_code == 200:
            # Record the hit and break loop
            idbl_hit = i
            break

    if idbl_hit:
        # Update console
        click.echo('\r{}{}'.format(echo_message, '...'), nl=False)
        click.echo(click.style(' {}'.format(idbl_hit), fg='green'))

        return idbl_hit

    raise ExtractionError('No initial iDBL payload identified.')

def identify_endpoints(session, settings):
    """Identifies the start and endpoints for extractions."""
    start = settings['abc_id_start']
    end = settings['abc_id_end']
    step = settings['abc_id_increment']

    # If using HTML files, can just use start and stop IDs
    if settings['files']['use_html']:
        return start, end

    # Find a valid iDBL ID to start narrowing from
    idbl_hit = identify_payload(session, settings, start, end, step)

    # Find the specific start and end points
    start_id = identify_endpoint(
        'start', session, settings, idbl_hit - step, idbl_hit
    )
    end_id = identify_endpoint(
        'end', session, settings, idbl_hit, idbl_hit + step
    )

    return start_id, end_id
