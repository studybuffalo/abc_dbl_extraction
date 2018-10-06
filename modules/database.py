# TODO: Determine if get_or_create is needed or if get can be used

from django.db import DataError
import logging


log = logging.getLogger(__name__)

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

def remove_data(db, url):
    """Removes the data for the specified URL"""
    log.debug("URL %s: Removing database entries" % url)
    
    db["atc"].objects.filter(url=url).delete()
    db["coverage"].objects.filter(url=url).delete()
    db["extra"].objects.filter(url=url).delete()
    db["ptc"].objects.filter(url=url).delete()
    db["price"].objects.filter(url=url).delete()
    db["special"].objects.filter(url=url).delete()
 
def upload_data(content, db):
    """Uploads the content to the respective database tables"""
    log.debug("URL %s: Uploading data to database" % content.url)
    
    # save the ATC data to the Django DB
    try:
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
    except DataError as e:
        log.critical('Error uploading ATC data: {}'.format(e))


    # Save the Coverage data to the Django DB
    try:
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
    except DataError as e:
        log.critical('Error uploading Coverage data: {}'.format(e))


    # Save the Extra Information to the django DB
    try:
        extra = db["extra"](
            url=content.url,
            date_listed=content.dateListed.parse,
            date_discontinued=content.dateDiscontinued.parse,
            manufacturer=content.manufacturer.parse,
            schedule=content.schedule.parse,
            interchangeable=content.interchangeable.parse,
        )
        extra.save()
    except DataError as e:
        log.critical('Error uploading Extra data: {}'.format(e))

    
    # Save the price data to the Django DB
    try:
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
    except DataError as e:
        log.critical('Error uploading Price data: {}'.format(e))


    # Save the PTC data to the Django DB
    try:
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
    except DataError as e:
        log.critical('Error uploading PTC data: {}'.format(e))


    # Save any special auth results to the Django DB
    try:
        for spec in content.specialAuth:
            special = db["special"](
                url=content.url,
                title=spec.text,
                link=spec.link,
            )
            special.save()
    except DataError as e:
        log.critical(
            'Error uploading Special Authorization data: {}'.format(e)
        )

    
def upload_sub(content, pend):
    """Uploads any data missing a substitution to database"""
    log.debug("URL %s: Uploading sub data" % content.url)
    
    # TODO: Figure out if a URL field is needed or not 
    # (or if it is tied to a separate table)

    # Upload the BSRF sub data
    if content.bsrf.matched == False:
        try:
            bsrf, _ = pend["bsrf"].objects.get_or_create(
                original=content.bsrf.html
            )
            bsrf.brand_name=content.bsrf.brand
            bsrf.strength=content.bsrf.strength
            bsrf.route=content.bsrf.route
            bsrf.dosage_form=content.bsrf.form
            bsrf.save()
        except DataError as e:
            log.critical(
                'Error uploading BSRF Substitution data: {}'.format(e)
            )


    # Upload the generic sub data
    if content.genericName.matched == False:
        try:
            generic, _ = pend["generic"].objects.get_or_create(
                original=content.genericName.html,
            )
            generic.correction=content.genericName.parse
            generic.save()
        except DataError as e:
            log.critical(
                'Error uploading Generic Substitution data: {}'.format(e)
            )


    # Upload the manufacturer sub data
    if content.manufacturer.matched == False:
        try:
            manufacturer, _ = pend["manufacturer"].objects.get_or_create(
                original=content.manufacturer.html,
            )
            manufacturer.correction=content.manufacturer.parse
            manufacturer.save()
        except DataError as e:
            log.critical(
                'Error uploading Manufacturer Substitution data: {}'.format(e)
            )

    # Upload the PTC sub data
    if content.ptc.matched1 == False and content.ptc.text1:
        try:
            ptc1, _ = pend["ptc"].objects.get_or_create(
                original=content.ptc.html1,
            )
            ptc1.correction=content.ptc.text1
            ptc1.save()
        except DataError as e:
            log.critical(
                'Error uploading PTC1 Substitution data: {}'.format(e)
            )

    if content.ptc.matched2 == False and content.ptc.text2:
        try:
            ptc2, _ = pend["ptc"].objects.get_or_create(
                original=content.ptc.html2,
            )
            ptc2.correction=content.ptc.text2
            ptc2.save()
        except DataError as e:
            log.critical(
                'Error uploading PTC2 Substitution data: {}'.format(e)
            )

    if content.ptc.matched3 == False and content.ptc.text3:
        try:
            ptc3, _ = pend["ptc"].objects.get_or_create(
                original=content.ptc.html3,
            )
            ptc3.correction=content.ptc.text3
            ptc3.save()
        except DataError as e:
            log.critical(
                'Error uploading PTC3 Substitution data: {}'.format(e)
            )

    if content.ptc.matched4 == False and content.ptc.text4:
        try:
            ptc4, _ = pend["ptc"].objects.get_or_create(
                original=content.ptc.html4,
            )
            ptc4.correction=content.ptc.text4
            ptc4.save()
        except DataError as e:
            log.critical(
                'Error uploading PTC4 Substitution data: {}'.format(e)
            )