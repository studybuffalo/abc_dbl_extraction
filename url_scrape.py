class URLData(object):
    def __init__(self, id, url, status):
        self.id = id
        self.url = url
        self.status = status

def assemble_url(id):
    """Constructs a valid iDBL url based on the drug ID"""
    # Base URL to construct final URL from
    base = ("https://idbl.ab.bluecross.ca/idbl/"
            "lookupDinPinDetail.do?productID=")
        
    # Assembles the url form the base + 10 digit productID
    url = "%s%010d" % (base, id)

    return url

def check_url(id, url, session, log):
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
        log.debug("ACTIVE   - %s" % url)
        status = URLData(id, url, "active")

    elif code == 302:
        log.debug("INACTIVE - %s" % url)
        status = URLData(id, url, "inactive")

    else:
        log.warn("Unexpected %d error with %s" % (code, url))
        status = URLData(id, url, "error")

    return status


def scrape_url(id, session, log):
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

    url = assemble_url(id)
            
    data = check_url(id, url, session, log)
            
    # Return the URL
    return data


def debug_url(fileLoc):
    """Returns data from text file instead of website"""
    with open(fileLoc.absolute(), "r") as file:
        urls = file.read().split("\n")

    urlList = []

    for id in urls:
        if id:
            # Construct the full URL
            id = int(id)
            url = assemble_url(id)

            # Create the URLData object and append it
            urlList.append(URLData(id, url, "active"))
        
    return urlList

def debug_url_data(htmlLoc):
    """Builds a urlList out of the html file names"""
    # Get all the file names in the directory
    files = htmlLoc.listdir(pattern="*.html", names_only=True)

    # Extracts all the ids from the file names
    idList = []

    for file in files:
        idList.append(int(file[:-5]))

    # Sorts the ids numerically
    idList = sorted(idList, key=int)

    # Creates a URL list from the sorted IDs
    urlList = []

    for id in idList:
        url = assemble_url(id)

        # Create the URLData object and append it
        urlList.append(URLData(id, url, "active"))

    return urlList