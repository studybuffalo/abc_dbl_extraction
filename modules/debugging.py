class Debug(object):
    def __init__(self, scrapeUrl, urlList, start, end, scrapeData, htmlLoc,
               uploadData, uploadSubs, updateWebsite):
        self.scrapeUrl = scrapeUrl
        self.urlList = urlList
        self.start = start
        self.end = end
        self.scrapeData = scrapeData
        self.htmlLoc = htmlLoc
        self.uploadData = uploadData
        self.uploadSubs = uploadSubs
        self.updateWebsite = updateWebsite


def get_debug_status(conf, log):
    """Collects all required data to enable program debugging modes"""
    from modules import extraction

    # Check if the URLs will be scrapped
    try:
        scrapeUrl = conf.getboolean("debug", "scrape_urls")
    except Exception as e:
        log.warn("Unable to determine URL debugging status: %s" % e)
        scrapeUrl = True

    if scrapeUrl:
        log.debug("URL SCRAPING ENABLED")
        urlList = None
        start = None
        end = None
    else:
        log.debug("DEBUG MODE - SKIPPING URL SCRAPING")

        urlList = extraction.debug_url(Path(conf.get("debug", "url_loc")))
        start = 0
        end = len(urlList) - 1
        

    # Check if pages will be scraped
    try:
        scrapeData = conf.getboolean("debug", "scrape_data")
    except Exception as e:
        log.warn("Unable to determine data scraping debugging status: %s" % e)
        scrapeData = True

    if scrapeData:
        log.debug("WEBSITE SCRAPING ENABLED")
        htmlLoc = None
    else:
        log.debug("DEBUG MODE - SKIPPING WEBSITE SCRAPING")
        htmlLoc = Path(conf.get("debug", "data_loc"))

        # Replaces any urlList data with the html content
        urlList = extraction.debug_url_data(htmlLoc)
        start = 0
        end = len(urlList) - 1
    

    # Check if data will be uploaded to database    
    try:
        uploadData = conf.getboolean("debug", "upload_data")
    except Exception as e:
        log.warn("Unable to determine upload debugging status: %s" % e)
        uploadData = True
    
    if uploadData:
        log.debug("DATA UPLOAD ENABLED")
    else:
        log.debug("DEBUG MODE - SKIPPING DATABASE UPLOADS")


    # Check if sub data will be uploaded to database
    try:
        uploadSub = conf.getboolean("debug", "upload_sub")
    except Exception as e:
        log.warn("Unable to determine substitute upload debugging status: %s"
                 % e)
        uploadSub = True

    if uploadSub:
        log.debug("SUB UPLOAD ENABLED")
    else:
        log.debug("DEBUG MODE - SKIPPING SUB UPLOADS")

    # Check if details.php will be updated
    try:
        updateWebsite = conf.getboolean("debug", "update_website")
    except Exception as e:
        log.warn("Unable to determine website update debugging status: %s" % e)
        updateWebsite = True

    if updateWebsite:
        log.debug("UPDATING 'details.php' ENABLED")
    else:
        log.debug("DEBUG MODE - SKIPPING 'details.php' UPDATE")

    # Compile all debug data and return object
    debugData = Debug(scrapeUrl, urlList, start, end, scrapeData, htmlLoc, 
                      uploadData, uploadSub, updateWebsite)

    return debugData