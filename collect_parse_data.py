class Sub(object):
    def __init__(self, original, correction):
        self.original = original
        self.correction = correction


class BSRFSub(object):
    def __init__(self, bsrf, brandName, strength, route, dosageForm):
        self.bsrf = bsrf
        self.brandName = brandName
        self.strength = strength
        self.route = route
        self.dosageForm = dosageForm


class ATCDescription(object):
    def __init__(self, code, description):
        self.code = code
        self.description = description


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
    def __init__(self, searchList, objectList):
        self.searchList = searchList
        self.objectList = objectList

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
    s = "SELECT original, correction FROM abc_subs_ptc"
    results = cursor.execute(s)

    ptcS = []
    ptcO = []

    for row in cursor:
        ptcS.append(row["original"])
        ptcO.append(Sub(row["original"], row["correction"]))

    
    ptc = SearchList(ptcS, ptcO)


    # Get the BSRF subs
    s = ("SELECT bsrf, brand_name, strength, route, dosage_form "
         "FROM abc_sub_bsrf")
    results = cursor.execute(s)

    bsrfS = []
    bsrfO = []

    for row in cursor:
        bsrfS.append(row["bsrf"])
        bsrfO.append(BSRFSub(row["bsrf"], row["brand_name"], row["strength"], 
                             row["route"], row["dosage_form"]))
    
    bsrf = SearchList(bsrfS, bsrfO)


    # Get the Brand Name subs
    s = "SELECT original, correction FROM abc_subs_brand"
    results = cursor.execute(s)

    brandS = []
    brandO = []

    for row in cursor:
        brandS.append(row["original"])
        brandO.append(Sub(row["original"], row["correction"]))

    brand = SearchList(brandS, brandO)


    # Get the Units Subs
    s = "SELECT original, correction FROM abc_subs_unit"
    results = cursor.execute(s)

    unitsS = []
    unitsO = []

    for row in cursor:
        unitsS.append(row["orignal"])
        unitsO.append(Sub(row["original"], row["correction"]))

    units = SearchList(unitsS, unitsO)


    # Get the Generic Name subs
    s = "SELECT original, correction FROM abc_subs_generic"
    results = cursor.execute(s)

    genericS = []
    genericO = []

    for row in cursor:
        genericS.append(row["original"])
        genericO.append(Sub(row["original"], row["correction"]))

    generic = SearchList(genericS, genericO)


    # Get the Manufacturer subs
    s = "SELECT original, correction FROM abc_subs_manufacturer"
    results = cursor.execute(s)

    manufS = []
    manufO = []

    for row in cursor:
        manufS.append(row["original"])
        manufO.append(Sub(row["original"], row["correction"]))

    manufacturer = SearchList(manufS, manufO)


    # Get the ATC subs
    s = "SELECT code, description FROM abc_subs_atc"
    results = cursor.execute(s)

    atcS = []
    atcO = []

    for row in cursor:
        atcS.append(row["code"])
        atcO.append(ATCDescription(row["code"], row["description"]))

    atc = SearchList(atcS, atcO)


    return ParseData(ptc, bsrf, brand, units, generic, manufacturer, atc)