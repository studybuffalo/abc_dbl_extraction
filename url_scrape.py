def check_url(session, url, active, error, log):
    """Checks the provided URL for an active status code"""
    # Request the header for the provided url
    try:
        response = session.head(url, allow_redirects=False)
        code = response.status_code
    except Exception as e:
        log.warn("Unable to retriever header for %s: %s" % (url, e))
        code = 0
    
    if code == 200:
        log.debug("%s active" % url)
        active.write(url + "\n")
        return url
    elif code == 302:
        log.debug("%s inactive" % url)
    else:
        log.warn("Unexpected %d error with %s" % (code, url))
        error.write(url + "\n")
        return None

def scrape_urls(config, session, today, delay, log):
    """Cycles through product IDs to find active URLs
        args:
            config:     config object holding extraction details
            session:    a requests session to request headers
            today:      the date to add to the text files
            delay:      the seconds delay between header requests
            log:        a logging object to send logs to

        returns:
            urlList:    A list of active URLs from the website

        raises:
            none.
    """

    from unipath import Path
    import time

    log.info("Permissing granted to crawl site")
    log.info("Starting URL extraction")

	# Variables to generate urls
    base = ("https://idbl.ab.bluecross.ca/idbl/"
            "lookupDinPinDetail.do?productID=")
    start = config.getint("url_extraction", "url_start")
    end = config.getint("url_extraction", "url_end")
    
    # Set where to save the extracted url data
    urlLoc = Path(config.get("url_extraction", "url_location"))

    activeList = urlLoc.child("%s_active.txt" % today).absolute()
    errorList = urlLoc.child("%s_error.txt" % today).absolute()
    
	# Goes through each URL; saves active ones to text file and list
    urlList = []

    with open(activeList, 'w') as active, open(errorList, 'w') as error: 
        for i in range (start, end + 1):
            # Assembles the url form the base + 10 digit productID
            url = "%s%010d" % (base, i)
            
            tempUrl = check_url(session, url, active, error, log)
            
            # Record any valid URLs
            if tempUrl:
                urlList.append(tempUrl)
            
            # Wait for delay to reduce load on server
            time.sleep(delay)
    
    log.info("URL extraction complete")
    
    return urlList