class FileNames(object):
    def __init__(self, url, html, price, coverage, 
                 specialAuth, ptc, atc, extra):
        self.url = url
        self.html = html
        self.price = price
        self.coverage = coverage
        self.specialAuth = specialAuth
        self.ptc = ptc
        self.atc = atc
        self.extra = extra

class SaveFiles(object):
    def __init__(self, url, html, price, coverage, special, ptc, 
                 atc, extra):
        self.url = url
        self.html = html
        self.price = price
        self.coverage = coverage
        self.special = special
        self.ptc = ptc
        self.atc = atc
        self.extra = extra

def get_today():
    import datetime

    today = datetime.date.today()
    year = today.year
    month = "%02d" % today.month
    day = "%02d" % today.day
    
    today = "%s-%s-%s" % (year, month, day)
    
    return today

def collect_file_paths(con):
    from unipath import Path

    """Collects extraction file paths and creates needed directories"""
    # Get Current today
    today = get_today()

    # Assemble URL filepath
    url = Path(con.get("locations", "url")).child(today, "url.txt")
    url.parent.mkdir(parents=True)

    # Assemble HTML file path
    html = Path(con.get("locations", "html")).child(today, "html")
    html.mkdir(parents=True)

    # Assemble price file path
    price = Path(con.get("locations", "price")).child(today, "price.csv")
    price.parent.mkdir(parents=True)

    # Assemble coverage file path
    cov = Path(con.get("locations", "coverage")).child(today, "coverage.csv")
    cov.parent.mkdir(parents=True)

    # Assemble special authorization file path
    special = Path(con.get("locations", "special")).child(today, "special.csv")
    special.parent.mkdir(parents=True)

    # Assemble PTC file path
    ptc = Path(con.get("locations", "ptc")).child(today, "ptc.csv")
    ptc.parent.mkdir(parents=True)

    # Assemble ATC file path
    atc = Path(con.get("locations", "atc")).child(today, "atc.csv")
    atc.parent.mkdir(parents=True)

    # Assemble extra information file path
    extra = Path(con.get("locations", "extra")).child(today, "extra.csv")
    extra.parent.mkdir(parents=True)

    return FileNames(url, html, price, cov, special, ptc, atc, extra)

def create_csv_writer(path):
    import csv

    writer = csv.writer(path, 
                        quoting=csv.QUOTE_NONNUMERIC, 
                        lineterminator="\n")

    return writer

def organize_save_files(url, html, price, coverage, special, ptc, atc, extra):
    # Create appropriate CSV writers
    cPrice = create_csv_writer(price)
    cCoverage = create_csv_writer(coverage)
    cSpecial = create_csv_writer(special)
    cPTC = create_csv_writer(ptc)
    cATC = create_csv_writer(atc)
    cExtra = create_csv_writer(extra)

    saveFiles = SaveFiles(url, html, cPrice, cCoverage, cSpecial, cPTC, 
                          cATC, cExtra)

    return saveFiles

def save_data(content, save, log):
    """Saves the information in content to respective files"""
    log.debug("URL %s: Saving data to file" % content.url)

    # Save URL data
    try:
        save.url.write("%s\n" % content.url)
    except Exception as e:
        log.warn("Unable to write %s to url.txt: %s" % (content.url, e))

    # Save the price data
    price = [content.url, content.din.parse, content.bsrf.brand, 
             content.bsrf.strength, content.bsrf.route, content.bsrf.form, 
             content.genericName.parse, content.unitPrice.parse, 
             content.lca.value, content.lca.text, content.unitIssue.parse]

    try:
        save.price.writerow(price)
    except Exception as e:
        log.warn("Unable to write %s to price.csv: %s" % (content.url, e))

    # Save the coverage data
    coverage = [content.url, content.coverage.parse, 
                content.criteria.criteria, content.criteria.special, 
                content.criteria.palliative, content.clients.g1, 
                content.clients.g66, content.clients.g66a,
                content.clients.g19823, content.clients.g19823a, 
                content.clients.g19824, content.clients.g20400, 
                content.clients.g20403, content.clients.g20514, 
                content.clients.g22128, content.clients.g23609]
    
    try:
        save.coverage.writerow(coverage)
    except Exception as e:
        log.warn("Unable to write %s to coverage.csv: %s" % 
                      (content.url, e))

    # Save the special authorization data
    special = []
    
    for item in content.specialAuth:
        special.append([content.url, item.text, item.link])

    try:
        save.special.writerows(special)
    except Exception as e:
        log.warn("Unable to write %s to special.csv: %s" 
                      % (content.url, e))

    # Save the PTC data
    ptc = [content.url, content.ptc.code1, content.ptc.text1, 
           content.ptc.code2, content.ptc.text2, 
           content.ptc.code3, content.ptc.text3, 
           content.ptc.code4, content.ptc.text4]

    try:
        save.ptc.writerow(ptc)
    except Exception as e:
        log.warn("Unable to write %s to ptc.csv: %s" % (content.url, e))

    # Save the ATC data
    atc = [content.url, content.atc.code1, content.atc.text1, 
           content.atc.code2, content.atc.text2, 
           content.atc.code3, content.atc.text3, 
           content.atc.code4, content.atc.text4, 
           content.atc.code5, content.atc.text5]

    try:
        save.atc.writerow(atc)
    except Exception as e:
        log.warn("Unable to write %s to atc.csv: %s" % (content.url, e))

    # Save the extra information data
    extra = [content.url, content.dateListed.parse, 
             content.dateDiscontinued.parse, content.manufacturer.parse, 
             content.schedule.parse, content.interchangeable.parse]

    try:
        save.extra.writerow(extra)
    except Exception as e:
        log.warn("Unable to write %s to extra.csv: %s" % (content.url, e))

    # Save a copy of the HTML page
    htmlPath = save.html.child("%s.html" % content.url).absolute()

    try:
        with open(htmlPath, "w") as fHTML:
            fHTML.write(content.html)
    except Exception as e:
        log.critical("Unable to save HTML for %s: %s" % (content.url, e))