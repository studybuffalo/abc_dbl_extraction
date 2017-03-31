class DB(object):
    def __init__(self, connection, cursor):
        self.connection = connection
        self.cursor = cursor

class BSRFSub(object):
    def __init__(self, brandName, strength, route, dosageForm):
        self.brandName = brandName
        self.strength = strength
        self.route = route
        self.dosageForm = dosageForm

class Units(object):
    def __init__(self, original, correction):
        self.original = original
        self.correction = correction

class SearchList(object):
    def __init__(self, originalList, corrList):
        self.original = originalList
        self.correction = corrList

class ParseData(object):
    def __init__(self, ptc, bsrf, units, generic, manufacturer, atc):
        self.ptc = ptc
        self.bsrf = bsrf
        self.units = units
        self.generic = generic
        self.manufacturer = manufacturer
        self.atc = atc


def setup_db_connection(conf, log):
    """Sets up MySQL database connections and cursor"""
    import pymysql.cursors

    db = conf.get("mysql", "db")
    host = conf.get("mysql", "host")
    user = conf.get("mysql", "user")
    pw = conf.get("mysql", "password")

    try:
        connection = pymysql.connect(host=host, 
                                     user=user, 
                                     password=pw, 
                                     db=db, 
                                     charset="utf8",
                                     cursorclass=pymysql.cursors.DictCursor)
    except:
        log.exception("Unable to connect to database")
        connection = None

    try:
        cursor = connection.cursor()
    except:
        log.exception("Unable to establish database cursor")
        cursor = None

    db = DB(connection, cursor)

    return db

def collect_parse_data(cursor):
    """Retrieves all the required parsing data from the database
        args:
            cursor: a PyMySQL cursor connected to the proper database

        returns:
            ParseData:  an object containing all the parse data. All 
                        parse data contains two lists: one for 
                        searching against, and one for applying the 
                        actual substitutions

        raises:
            none.
    """

    # Get the PTC subs
    s = "SELECT original, correction FROM abc_subs_ptc ORDER BY original"
    results = cursor.execute(s)

    ptcO = []
    ptcC = []

    for row in cursor:
        ptcO.append(row["original"])
        ptcC.append(row["correction"])

    ptc = SearchList(ptcO, ptcC)


    # Get the BSRF subs
    s = ("SELECT bsrf, brand_name, strength, route, dosage_form "
         "FROM abc_subs_bsrf ORDER BY bsrf")
    results = cursor.execute(s)

    bsrfO = []
    bsrfC = []

    for row in cursor:
        bsrfO.append(row["bsrf"])
        bsrfC.append(BSRFSub(row["brand_name"], row["strength"], 
                             row["route"], row["dosage_form"]))
    
    bsrf = SearchList(bsrfO, bsrfC)


    # Get the Units Subs
    s = "SELECT original, correction FROM abc_subs_unit ORDER BY original"
    results = cursor.execute(s)

    units = []

    for row in cursor:
        units.append(Units(row["original"], row["correction"]))


    # Get the Generic Name subs
    s = "SELECT original, correction FROM abc_subs_generic ORDER BY original"
    results = cursor.execute(s)

    genericO = []
    genericC = []

    for row in cursor:
        genericO.append(row["original"])
        genericC.append(row["correction"])

    generic = SearchList(genericO, genericC)


    # Get the Manufacturer subs
    s = ("SELECT original, correction FROM abc_subs_manufacturer "
         "ORDER BY original")
    results = cursor.execute(s)

    manufO = []
    manufC = []

    for row in cursor:
        manufO.append(row["original"])
        manufC.append(row["correction"])

    manufacturer = SearchList(manufO, manufC)


    # Get the ATC subs
    s = "SELECT code, description FROM abc_atc_descriptions ORDER BY code"
    results = cursor.execute(s)

    atcC = []
    atcD = []

    for row in cursor:
        atcC.append(row["code"])
        atcD.append(row["description"])

    atc = SearchList(atcC, atcD)


    return ParseData(ptc, bsrf, units, generic, manufacturer, atc)

def remove_data(cursor, url, log):
    """Removes the data for the specified URL"""
    log.debug("URL %s: Removing database entries" % url)

    s = "DELETE FROM abc_atc WHERE url = %s"
    cursor.execute(s, url)
    
    s = "DELETE FROM abc_coverage WHERE url = %s"
    cursor.execute(s, url)
    
    s = "DELETE FROM abc_extra_information WHERE url = %s"
    cursor.execute(s, url)
    
    s = "DELETE FROM abc_price WHERE url = %s"
    cursor.execute(s, url)
    
    s = "DELETE FROM abc_ptc WHERE url = %s"
    cursor.execute(s, url)

    s = "DELETE FROM abc_special_authorization WHERE url = %s"
    cursor.execute(s, url)
 
def upload_data(content, cursor, log):
    """Uploads the content to the respective database tables"""
    log.debug("URL %s: Uploading data to database" % content.url)

    # Construct and execute abc_price query
    s = ("INSERT INTO abc_price (url, din, brand_name, strength, "
         "route, dosage_form, generic_name, unit_price, lca, lca_text, "
         "unit_issue) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    price = (content.url, content.din.parse, content.bsrf.brand, 
             content.bsrf.strength, content.bsrf.route, content.bsrf.form, 
             content.genericName.parse, content.unitPrice.parse, 
             content.lca.value, content.lca.text, content.unitIssue.parse)

    cursor.execute(s, price)

    # Construct and execute abc_coverage query
    s = ("INSERT INTO abc_coverage (url, coverage, criteria, criteria_sa, "
         "criteria_p, group_1, group_66, group_66a, group_19823, "
         "group_19823a, group_19824, group_20400, group_20403, group_20514, "
         "group_22128, group_23609) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, "
         "%s, %s, %s, %s, %s, %s, %s, %s)")
    coverage = (content.url, content.coverage.parse, 
                content.criteria.criteria, content.criteria.special, 
                content.criteria.palliative, content.clients.g1, 
                content.clients.g66, content.clients.g66a,
                content.clients.g19823, content.clients.g19823a, 
                content.clients.g19824, content.clients.g20400, 
                content.clients.g20403, content.clients.g20514, 
                content.clients.g22128, content.clients.g23609)
    cursor.execute(s, coverage)

    # Construct and execute abc_special_authorization query 
    # (if there are values)
    s = ("INSERT INTO abc_special_authorization (url, title, link) "
            "VALUES (%s, %s, %s)")
        
    for spec in content.specialAuth:
        special = (content.url, spec.text, spec.link)
        cursor.execute(s, special)

    # Construct and execute abc_ptc query
    s = ("INSERT INTO abc_ptc (url, ptc_1, ptc_1_text, ptc_2, ptc_2_text, "
         "ptc_3, ptc_3_text, ptc_4, ptc_4_text) "
         "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
    ptc = (content.url, content.ptc.code1, content.ptc.text1, 
           content.ptc.code2, content.ptc.text2, 
           content.ptc.code3, content.ptc.text3, 
           content.ptc.code4, content.ptc.text4)
    cursor.execute(s, ptc)

    # Construct and execute abc_atc query
    s = ("INSERT INTO abc_atc (url, atc_1, atc_1_text, atc_2, atc_2_text, "
         "atc_3, atc_3_text, atc_4, atc_4_text, atc_5, atc_5_text) "
         "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    atc = (content.url, content.atc.code1, content.atc.text1, 
           content.atc.code2, content.atc.text2, 
           content.atc.code3, content.atc.text3, 
           content.atc.code4, content.atc.text4, 
           content.atc.code5, content.atc.text5)
    cursor.execute(s, atc)

    # Construct and execute abc_extra_information query
    s = ("INSERT INTO abc_extra_information (url, date_listed, "
         "date_discontinued, manufacturer, schedule, interchangeable) "
         "VALUES (%s, %s, %s, %s, %s, %s)")
    extra = (content.url, content.dateListed.parse, 
             content.dateDiscontinued.parse, content.manufacturer.parse, 
             content.schedule.parse, content.interchangeable.parse)
    cursor.execute(s, extra)

def upload_sub(content, cursor, log):
    """Uploads any data missing a substitution to database"""
    log.debug("URL %s: Uploading sub data" % content.url)

    # Upload the BSRF sub data
    if content.bsrf.matched == False:
        s = ("INSERT INTO abc_pend_bsrf (url, original, brand_name, "
             "strength, route, dosage_form) VALUES (%s, %s, %s, %s, %s, %s) "
             "ON DUPLICATE KEY UPDATE brand_name = %s, strength = %s, "
             "route = %s, dosage_form = %s")
        bsrf = (content.url, content.bsrf.html, content.bsrf.brand,
                content.bsrf.strength, content.bsrf.route, content.bsrf.form, 
                content.bsrf.brand, content.bsrf.strength, content.bsrf.route, 
                content.bsrf.form)

        cursor.execute(s, bsrf)

    # Upload the generic sub data
    if content.genericName.matched == False:
        s = ("INSERT INTO abc_pend_generic (url, original, correction) "
             "VALUES (%s, %s, %s) "
             "ON DUPLICATE KEY UPDATE correction = %s")
        generic = (content.url, content.genericName.html, 
                   content.genericName.parse, content.genericName.parse)

        cursor.execute(s, generic)

    # Upload the manufacturer sub data
    if content.manufacturer.matched == False:
        s = ("INSERT INTO abc_pend_manufacturer (url, original, correction) "
             "VALUES (%s, %s, %s) "
             "ON DUPLICATE KEY UPDATE correction = %s")
        manuf = (content.url, content.manufacturer.html, 
                   content.manufacturer.parse, content.manufacturer.parse)

        cursor.execute(s, manuf)

    # Upload the PTC sub data
    if content.ptc.matched1 == False and content.ptc.text1:
        s = ("INSERT INTO abc_pend_ptc (url, original, correction) "
             "VALUES (%s, %s, %s) "
             "ON DUPLICATE KEY UPDATE correction = %s")
        ptc1 = (content.url, content.ptc.html1, 
                content.ptc.text1, content.ptc.text1)

        cursor.execute(s, ptc1)

    if content.ptc.matched2 == False and content.ptc.text2:
        s = ("INSERT INTO abc_pend_ptc (url, original, correction) "
             "VALUES (%s, %s, %s) "
             "ON DUPLICATE KEY UPDATE correction = %s")
        ptc2 = (content.url, content.ptc.html2, 
                content.ptc.text2, content.ptc.text2)

        cursor.execute(s, ptc2)

    if content.ptc.matched3 == False and content.ptc.text3:
        s = ("INSERT INTO abc_pend_ptc (url, original, correction) "
             "VALUES (%s, %s, %s) "
             "ON DUPLICATE KEY UPDATE correction = %s")
        ptc3 = (content.url, content.ptc.html3, 
                content.ptc.text3, content.ptc.text3)

        cursor.execute(s, ptc3)

    if content.ptc.matched4 == False and content.ptc.text4:
        s = ("INSERT INTO abc_pend_ptc (url, original, correction) "
             "VALUES (%s, %s, %s) "
             "ON DUPLICATE KEY UPDATE correction = %s")
        ptc4 = (content.url, content.ptc.html4, 
                content.ptc.text4, content.ptc.text4)

        cursor.execute(s, ptc4)