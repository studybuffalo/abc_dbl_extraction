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


def collect_parse_data(cursor):
    # Get the PTC subs
    s = "SELECT original, correction FROM abc_subs_ptc"
    results = cursor.execute(s)

    ptc = []

    for row in cursor:
        ptc.append(Sub(row["original"], row["correction"]))

    # Get the BSRF subs
    s = ("SELECT bsrf, brand_name, strength, route, dosage_form "
         "FROM abc_sub_bsrf")
    results = cursor.execute(s)

    brand = []

    for row in cursor:
        brand.append(BSRFSub(row["bsrf"], row["brand_name"], row["strength"], 
                             row["route"], row["dosage_form"]))

    # Get the Brand Name subs
    s = "SELECT original, correction FROM abc_subs_brand"
    results = cursor.execute(s)

    brand = []

    for row in cursor:
        brand.append(Sub(row["original"], row["correction"]))

    # Get the Units Subs
    s = "SELECT original, correction FROM abc_subs_unit"
    results = cursor.execute(s)

    units = []

    for row in cursor:
        units.append(Sub(row["original"], row["correction"]))

    # Get the Generic Name subs
    s = "SELECT original, correction FROM abc_subs_generic"
    results = cursor.execute(s)

    generic = []

    for row in cursor:
        generic.append(Sub(row["original"], row["correction"]))

    # Get the Manufacturer subs
    s = "SELECT original, correction FROM abc_subs_manufacturer"
    results = cursor.execute(s)

    manufacturer = []

    for row in cursor:
        manufacturer.append(Sub(row["original"], row["correction"]))

    # Get the ATC subs
    s = "SELECT code, description FROM abc_subs_atc"
    results = cursor.execute(s)

    atc = []

    for row in cursor:
        atc.append(ATCDescription(row["code"], row["description"]))

    return ParseData(ptc, bsrf, brand, units, generic, manufacturer, atc)