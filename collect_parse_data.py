class BSRFSub(object):
    def __init__(self, brandName, strength, route, dosageForm):
        self.brandName = brandName
        self.strength = strength
        self.route = route
        self.dosageForm = dosageForm


class ParseData(object):
    def __init__(self, ptc, bsrf, brand, units, generic, manufacturer, atc):
        self.ptc = ptc
        self.bsrf = bsrf
        self.brand = brand
        self.units = units
        self.generic = generic
        self.manufacturer = manufacturer
        self.atc = atc

class SearchList(object):
    def __init__(self, originalList, corrList):
        self.original = originalList
        self.correction = corrList


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
         "FROM abc_sub_bsrf ORDER BY bsrf")
    results = cursor.execute(s)

    bsrfO = []
    bsrfC = []

    for row in cursor:
        bsrfO.append(row["bsrf"])
        bsrfC.append(BSRFSub(row["brand_name"], row["strength"], 
                             row["route"], row["dosage_form"]))
    
    bsrf = SearchList(bsrfO, bsrfC)


    # Get the Brand Name subs
    s = "SELECT original, correction FROM abc_subs_brand ORDER BY original"
    results = cursor.execute(s)

    brandO = []
    brandC = []

    for row in cursor:
        brandO.append(row["original"])
        brandC.append( row["correction"])

    brand = SearchList(brandO, brandC)


    # Get the Units Subs
    s = "SELECT original, correction FROM abc_subs_unit ORDER BY original"
    results = cursor.execute(s)

    unitsO = []
    unitsC = []

    for row in cursor:
        unitsO.append(row["orignal"])
        unitsC.append(row["correction"])

    units = SearchList(unitsO, unitsC)


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
    s = "SELECT code, description FROM abc_subs_atc ORDER BY code"
    results = cursor.execute(s)

    atcC = []
    atcD = []

    for row in cursor:
        atcC.append(row["code"])
        atcD.append(row["description"])

    atc = SearchList(atcC, atcD)


    return ParseData(ptc, bsrf, brand, units, generic, manufacturer, atc)