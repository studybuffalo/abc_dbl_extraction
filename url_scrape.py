class URLData(object):
    def __init__(self, url, status):
        self.url = url
        self.status = status

def check_url(url, session, log):
    """Checks the provided URL for an active status code"""
    # Request the header for the provided url
    try:
        response = session.head(url, allow_redirects=False)
        code = response.status_code
    except Exception as e:
        log.warn("Unable to retriever header for %s: %s" % (url, e))
        code = 0
    
    # Check status and create the URL Status object
    if code == 200:
        log.debug("%s active" % url)
        status = URLData(url, "active")

    elif code == 302:
        log.debug("%s inactive" % url)
        status = URLData(url, "inactive")

    else:
        log.warn("Unexpected %d error with %s" % (code, url))
        status = URLData(url, "error")

    return status

def scrape_url(id, session, delay, log):
    """Takes the provided ID # and checks if it returns active URL
        args:
            session:    a requests session to request headers
            delay:      the seconds delay between header requests
            log:        a logging object to send logs to

        returns:
            urlList:    A list of active URLs from the website

        raises:
            none.
    """

    from unipath import Path

	# Base URL to construct final URL from
    base = ("https://idbl.ab.bluecross.ca/idbl/"
            "lookupDinPinDetail.do?productID=")

    # Assembles the url form the base + 10 digit productID
    url = "%s%010d" % (base, id)
            
    data = check_url(url, session, log)
            
    # Return the URL
    return data