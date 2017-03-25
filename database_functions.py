def return_connection(conf):
    """Connects to a MySQL DB with the provided details"""
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
                                     charsest="utf8",
                                     cursorclass=pymysql.cursors.DictCursor)
    except:
        log.exception("Unable to connect to database")
        connection = None

    return connection

def return_cursor(conn):
    """Creates a cursor for the DB connection"""
    try:
        cursor = conn.cursor()
    except:
        log.exception("Unable to establish database cursor")
        cursor = None

    return cursor

def remove_data(cursor, url):
    """Removes the data for the specified URL"""
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

    s = "DELETE FROM abc_special_authorizaiton WHERE url = %s"
    cursor.execute(s, url)


def upload_data(content, cursor):
    """Uploads the content to the respective database tables"""
    # Construct and execute abc_price query
    s = ("INSERT INTO abc_price (url, din, brand_name, strength, "
         "route, dosage_form, generic_name, unit_price, lca, lca_text, "
         "unit_issue) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    price = (content.url, content.din, content.brandName, content.strength,
             content.route, content.dosageForm, content.genericName, content.unitPrice,
             content.lca, content.lcaText, content.unitIssue)

    cursor.excecute(s, price)

    # Construct and execute abc_coverage query
    s = ("INSERT INTO abc_coverage (url, coverage, criteria, criteria_sa, "
         "criteria_p, group_1, group_66, group_66a, group_19823, "
         "group_19823a, group_19824, group_20400, group_20403, group_20514, "
         "group_22128, group_23609) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, "
         "%s, %s, %s, %s, %s, %s, %s, %s)")
    coverage = ()
    cursor.execute(s, coverage)

    # Construct and execute abc_special_authorization query
    s = ("INSERT INTO abc_special_authorization (url, title, link) "
         "VALUES (%s, %s, %s)")
    special = ()
    cursor.execute(s, special)

    # Construct and execute abc_ptc query
    s = ("INSERT INTO abc_ptc (url, ptc_1, ptc_1_text, ptc_2, ptc_2_text, "
         "ptc_3, ptc_3_text, ptc_4, ptc_4_text) "
         "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)")
    ptc = ()
    cursor.execute(s, special)

    # Construct and execute abc_atc query
    s = ("INSERT INTO abc_atc (url, atc_1, atc_1_text, atc_2, atc_2_text, "
         "atc_3, atc_3_text, atc_4, atc_4_text, atc_5, atc_5_text) "
         "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    atc = ()
    cursor.execute(s, atc)

    # Construct and execute abc_extra_information query
    s = ("INSERT INTO abc_extra_information (url, date_listed, "
         "date_discontinued, manufacturer,schedule, interchangeable) "
         "VALUES (%s, %s, %s, %s, %s, %s)")
    extra = ()
    cursor.execute(s, extra)