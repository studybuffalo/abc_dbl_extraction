"""Functions to manage steps of application functioning."""
import sys

import logging
import requests
import time

from modules import database, debugging, extraction, saving


log = logging.getLogger(__name__) # pylint: disable=invalid-name

def run_application(config):
    # Setup robot details and create session
    user_agent = config.get("robot", "user_agent", raw=True)
    user_from = config.get("robot", "from", raw=True)
    crawl_delay = config.getfloat("misc", "crawl_delay")

    session = requests.Session()
    session.headers.update({"User-Agent": user_agent, "From": user_from})

    from drug_price_calculator.models import ( # pylint: disable=import-error
        ATC, Coverage, ExtraInformation, PTC, Price, special_authorization,
        ATCDescriptions, SubsBSRF, SubsGeneric, SubsManufacturer, SubsPTC,
        SubsUnit, PendBSRF, PendGeneric, PendManufacturer, PendPTC
    )

    db = { # pylint: disable=invalid-name
        "atc": ATC,
        "coverage": Coverage,
        "extra": ExtraInformation,
        "ptc": PTC,
        "price": Price,
        "special": special_authorization,
    }

    subs = {
        "atc": ATCDescriptions,
        "bsrf": SubsBSRF,
        "generic": SubsGeneric,
        "manufacturer": SubsGeneric,
        "ptc": SubsPTC,
        "unit": SubsUnit,
    }

    pend = {
        "bsrf": PendBSRF,
        "generic": PendGeneric,
        "manufacturer": PendManufacturer,
        "ptc": PendPTC,
    }

    parse_data = database.collect_parse_data(subs)

    # Collect locations to save all files
    file_names = saving.collect_file_paths(config)


    log.info("ALBERTA BLUE CROSS DRUG BENEFIT LIST EXTRACTION TOOL STARTED")

    # Create all save files
    with open(file_names.url.absolute(), "w") as fURL, \
            open(file_names.price.absolute(), "w") as fPrice, \
            open(file_names.coverage.absolute(), "w") as fCoverage, \
            open(file_names.special_auth.absolute(), "w") as fSpecial, \
            open(file_names.ptc.absolute(), "w") as fPTC, \
            open(file_names.atc.absolute(), "w") as fATC, \
            open(file_names.extra.absolute(), "w") as fExtra:

        # Save all opened files into on object for easier use
        save_files = saving.organize_save_files(
            fURL, file_names.html, fPrice, fCoverage, fSpecial, fPTC, fATC, fExtra
        )

        # Setup debugging
        debug_data = debugging.get_debug_status(config)


        # Checking the robots.txt file for permission to crawl
        if debug_data.scrape_url:
            can_crawl = extraction.get_permission(user_agent)
        else:
            # Program set to debug - use pre-set data
            can_crawl = True

        # If crawling is permitted, run the program
        if can_crawl:
            log.info("Permission granted to crawl site")
            log.info("Starting URL extraction")

            # Set the start and end for loop
            if debug_data.scrape_url or debug_data.scrape_data:
                start = int(sys.argv[2])
                end = int(sys.argv[3])
            else:
                # Program set to debug - use pre-set data
                url_list = debug_data.url_list
                start = debug_data.start
                end = debug_data.end


            # Cycle through the range of URLs
            for i in range(start, end + 1):
                if debug_data.upload_data:
                    database.remove_data(db, i)

                # TEST FOR ACTIVE URL
                if debug_data.scrape_url:
                    # Apply delay before crawling URL
                    time.sleep(crawl_delay)

                    urlData = extraction.scrape_url(i, session)
                else:
                    # Program set to debug - use pre-set data
                    urlData = url_list[i]


                # SCRAPE DATA FROM ACTIVE URLS
                if urlData.status == "active":
                    if debug_data.scrape_data:
                        # Apply delay before accessing page
                        time.sleep(crawl_delay)

                        content = extraction.collect_content(
                            urlData, session, parse_data
                        )
                    else:
                        # Program set to debug - use pre-saved data
                        content = extraction.debug_data(
                            urlData, debug_data.html_loc, parse_data, log
                        )
                else:
                    content = None

                if content:
                    if debug_data.upload_data:
                        database.upload_data(content, db)

                    # UPLOAD SUBS INFORMATION TO DATABASE
                    if debug_data.upload_subs:
                        database.upload_sub(content, pend)

                    # SAVE BACKUP COPY OF DATA
                    saving.save_data(content, save_files)

    log.info("ALBERTA BLUE CROSS DRUG BENEFIT LIST EXTRACTION COMPLETE")
