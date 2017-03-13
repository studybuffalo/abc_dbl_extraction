def check_url(session, url, scriptHeader):
    """Checks the provided URL for an active status code"""
    try:
        response = session.head(url, headers=scriptHeader, allow_redirects=False)
        code = response.status_code
    except Exception as e:
        log.warn("Unable to retriever header for %s: %s" % (url, e))
        code = 0
    
    if code == 200:
        active.write(url + "\n")
        return url
    elif code != 302:
        error.write(url + "\n")
        return None

def scrape_urls(config, today, crawlDelay):
    """Cycles through product IDs to find active URLs
        args:
            config: config object holding extraction details

        returns:
            urlList:    A list of active URLs from the website

        raises:
            none.
    """
    from unipath import Path
    from urllib import request
    import requests
    import time

    log.info("Permissing granted to crawl site")
    log.info("Starting URL extraction")

    # Session to request HTML headers
    session = requests.Session()
    
	# Variables to generate urls
    base = ("https://idbl.ab.bluecross.ca/idbl/"
            "lookupDinPinDetail.do?productID=")
    start = config.getint("url_extraction", "url_start")
    end = config.getint("url_extraction", "url_end")
    
    # Set where to save the extracted url data
    urlLoc = Path(pubCon.get("misc", "url_location"))

    activeList = urlLoc.child("%s_active.txt" % today).absolute()
    errorList = urlLoc.child("%s_error.txt" % today).absolute()

    # Identify Robot
    userAgent = config.get("robot", "user_agent", raw=True)
    userAgentContact = config.get("robot", "user_email")
    scriptHeader = {"User-Agent": userAgent, "From": userAgentContact}
        
	# Goes through each URL; saves active ones to text file and list
    urlList = []

    with open(activeList, 'w') as active, open(errorList, 'w') as error: 
        for i in range (start, end + 1):
            url = "%s%010d" % (base, i)
            
            tempUrl = check_url(session, url, scriptHeader)
            
            if tempUrl:
                urlList.append(tempUrl)
            
            time.sleep(crawlDelay)
    
    log.info("URL extraction complete")
    
    return urlList