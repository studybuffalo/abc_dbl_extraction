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

def collect_parse_data(subs):
    """Retrieves all the required parsing data from the database
        args:
            subs: a dictionary of Django substitution models

        returns:
            ParseData:  an object containing all the parse data. All 
                        parse data contains two lists: one for 
                        searching against, and one for applying the 
                        actual substitutions

        raises:
            none.
    """
    # Get the ATC subs
    atcC = []
    atcD = []

    for item in subs["atc"].objects.all().order_by("code"):
        atcC.append(item.code)
        atcD.append(item.description)

    atc = SearchList(atcC, atcD)

    # Get the Brand name, Strength, Route, Form subs
    bsrfO = []
    bsrfC = []

    for item in subs["bsrf"].objects.all().order_by("bsrf"):
        bsrfO.append(item.bsrf)
        bsrfC.append(BSRFSub(
            item.brand_name, item.strength, item.route, item.dosage_form
        ))
    
    bsrf = SearchList(bsrfO, bsrfC)

    # Get the Generic Name subs
    genericO = []
    genericC = []

    for item in subs["generic"].objects.all().order_by("original"):
        genericO.append(item.original)
        genericC.append(item.correction)

    generic = SearchList(genericO, genericC)

    # Get the Manufacturer subs
    manufO = []
    manufC = []

    for item in subs["manufacturer"].objects.all().order_by("original"):
        manufO.append(item.original)
        manufC.append(item.correction)

    manufacturer = SearchList(manufO, manufC)

    # Get the PTC subs
    ptcO = []
    ptcC = []

    for item in subs["ptc"].objects.all().order_by("original"):
        ptcO.append(item.original)
        ptcC.append(item.correction)

    ptc = SearchList(ptcO, ptcC)

    # Get the Units Subs
    
    units = []

    for item in subs["unit"].objects.all().order_by("original"):
        units.append(Units(item.original, item.correction))

    return ParseData(ptc, bsrf, units, generic, manufacturer, atc)

def remove_data(db, url, log):
    """Removes the data for the specified URL"""
    log.debug("URL %s: Removing database entries" % url)
    
    db["atc"].objects.filter(url=url).delete()
    db["coverage"].objects.filter(url=url).delete()
    db["extra"].objects.filter(url=url).delete()
    db["ptc"].objects.filter(url=url).delete()
    db["price"].objects.filter(url=url).delete()
    db["special"].objects.filter(url=url).delete()
 
def upload_data(content, db, log):
    """Uploads the content to the respective database tables"""
    log.debug("URL %s: Uploading data to database" % content.url)

    # save the ATC data to the Django DB
    atc = db["atc"](
        url=content.url,
        atc_1=content.atc.code1,
        atc_1_text=content.atc.text1,
        atc_2=content.atc.code2,
        atc_2_text=content.atc.text2,
        atc_3=content.atc.code3,
        atc_3_text=content.atc.text3,
        atc_4=content.atc.code4,
        atc_4_text=content.atc.text4,
    )
    atc.save()
    # Save the Coverage data to the Django DB
    coverage = db["coverage"](
        url=content.url,
        coverage=content.coverage.parse,
        criteria=content.criteria.criteria,
        criteria_sa=content.criteria.special,
        criteria_p=content.criteria.palliative,
        group_1=content.clients.g1,
        group_66=content.clients.g66,
        group_66a=content.clients.g66a,
        group_19823=content.clients.g19823,
        group_19823a=content.clients.g19823a,
        group_19824=content.clients.g19824,
        group_20400=content.clients.g20400,
        group_20403=content.clients.g20403,
        group_20514=content.clients.g20514,
        group_22128=content.clients.g22128,
        group_23609=content.clients.g23609,
    )
    coverage.save()

    # Save the Extra Information to the django DB
    extra = db["extra"](
        url=content.url,
        date_listed=content.dateListed.parse,
        date_discontinued=content.dateDiscontinued.parse,
        manufacturer=content.manufacturer.parse,
        schedule=content.schedule.parse,
        interchangeable=content.interchangeable.parse,
    )
    extra.save()
    
    # Save the price data to the Django DB
    price = db["price"](
        url=content.url,
        din=content.din.parse,
        brand_name=content.bsrf.brand,
        strength=content.bsrf.strength,
        route=content.bsrf.route,
        dosage_form=content.bsrf.form,
        generic_name=content.genericName.parse,
        unit_price=content.unitPrice.parse,
        lca=content.lca.value,
        lca_text=content.lca.text,
        unit_issue=content.unitIssue.parse,
    )
    price.save()

    # Save the PTC data to the Django DB
    ptc = db["ptc"](
        url=content.url,
        ptc_1=content.ptc.code1,
        ptc_1_text=content.ptc.text1,
        ptc_2=content.ptc.code2,
        ptc_2_text=content.ptc.text2,
        ptc_3=content.ptc.code3,
        ptc_3_text=content.ptc.text3,
        ptc_4=content.ptc.code4,
        ptc_4_text=content.ptc.text4,
    )
    ptc.save()

    # Save any special auth results to the Django DB
    for spec in content.specialAuth:
        special = db["special"](
            url=content.url,
            title=spec.text,
            link=spec.link,
        )
        special.save()
    
def upload_sub(content, pend, log):
    """Uploads any data missing a substitution to database"""
    log.debug("URL %s: Uploading sub data" % content.url)

    # TODO: Replace the INSERT ... UPDATE ON DUPLICATE KEY
    # TODO: Figure out if a URL field is needed or not 
    # (or if it is tied to a separate table)

    # Upload the BSRF sub data
    if content.bsrf.matched == False:
        bsrf = pend["bsrf"](
            original=content.bsrf.html,
            brand_name=content.bsrf.brand,
            strength=content.bsrf.strength,
            route=content.bsrf.route,
            dosage_form=content.bsrf.form,
        )
        bsrf.save()

    # Upload the generic sub data
    if content.genericName.matched == False:
        generic = pend["generic"](
            original=content.genericName.html,
            correction=content.genericName.parse,
        )
        generic.save()

    # Upload the manufacturer sub data
    if content.manufacturer.matched == False:
        manufacturer = pend["manufacturer"](
            original=content.manufacturer.html,
            correction=content.manufacturer.parse,
        )
        generic.save()

    # Upload the PTC sub data
    if content.ptc.matched1 == False and content.ptc.text1:
        ptc1 = pend["ptc"](
            original=content.ptc.html1,
            correction=content.ptc.text1,
        )
        ptc1.save()

    if content.ptc.matched2 == False and content.ptc.text2:
        ptc2 = pend["ptc"](
            original=content.ptc.html2,
            correction=content.ptc.text2,
        )
        ptc2.save()

    if content.ptc.matched3 == False and content.ptc.text3:
        ptc3 = pend["ptc"](
            original=content.ptc.html3,
            correction=content.ptc.text3,
        )
        ptc3.save()

    if content.ptc.matched4 == False and content.ptc.text4:
        ptc14 = pend["ptc"](
            original=content.ptc.html4,
            correction=content.ptc.text4,
        )
        ptc4.save()