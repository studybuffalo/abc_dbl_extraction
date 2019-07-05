"""Module to help with debugging errors."""
import logging
from unipath import Path

from modules import extraction


log = logging.getLogger(__name__) # pylint: disable=invalid-name

class Debug(object):
    """Object to hold debug data."""
    def __init__(
            self, scrape_url, url_list, start, end, scrape_data, html_loc,
            upload_data, upload_subs, update_website
    ):
        self.scrape_url = scrape_url
        self.url_list = url_list
        self.start = start
        self.end = end
        self.scrape_data = scrape_data
        self.html_loc = html_loc
        self.upload_data = upload_data
        self.upload_subs = upload_subs
        self.update_website = update_website


def get_debug_status(conf):
    """Collects all required data to enable program debugging modes"""
    # Check if the URLs will be scrapped
    try:
        scrape_url = conf.getboolean('debug', 'scrape_urls')
    except Exception as error:
        log.warning('Unable to determine URL debugging status: %s', error)
        scrape_url = True

    if scrape_url:
        log.debug('URL SCRAPING ENABLED')
        url_list = None
        start = None
        end = None
    else:
        log.debug('DEBUG MODE - SKIPPING URL SCRAPING')

        url_list = extraction.debug_url(Path(conf.get('debug', 'url_loc')))
        start = 0
        end = len(url_list) - 1


    # Check if pages will be scraped
    try:
        scrape_data = conf.getboolean('debug', 'scrape_data')
    except Exception as error:
        log.warning(
            'Unable to determine data scraping debugging status: %s', error
        )
        scrape_data = True

    if scrape_data:
        log.debug('WEBSITE SCRAPING ENABLED')
        html_loc = None
    else:
        log.debug('DEBUG MODE - SKIPPING WEBSITE SCRAPING')
        html_loc = Path(conf.get('debug', 'data_loc'))

        # Replaces any url_list data with the html content
        url_list = extraction.debug_url_data(html_loc)
        start = 0
        end = len(url_list) - 1


    # Check if data will be uploaded to database
    try:
        upload_data = conf.getboolean('debug', 'upload_data')
    except Exception as error:
        log.warning('Unable to determine upload debugging status: %s', error)
        upload_data = True

    if upload_data:
        log.debug('DATA UPLOAD ENABLED')
    else:
        log.debug('DEBUG MODE - SKIPPING DATABASE UPLOADS')


    # Check if sub data will be uploaded to database
    try:
        upload_sub = conf.getboolean('debug', 'upload_sub')
    except Exception as error:
        log.warning(
            'Unable to determine substitute upload debugging status: %s', error
        )
        upload_sub = True

    if upload_sub:
        log.debug('SUB UPLOAD ENABLED')
    else:
        log.debug('DEBUG MODE - SKIPPING SUB UPLOADS')

    # Check if details.php will be updated
    try:
        update_website = conf.getboolean('debug', 'update_website')
    except Exception as error:
        log.warning(
            'Unable to determine website update debugging status: %s', error
        )
        update_website = True

    if update_website:
        log.debug('UPDATING "details.php" ENABLED')
    else:
        log.debug('DEBUG MODE - SKIPPING "details.php" UPDATE')

    # Compile all debug data and return object
    debug_data = Debug(
        scrape_url, url_list, start, end, scrape_data, html_loc, upload_data,
        upload_sub, update_website
    )

    return debug_data
