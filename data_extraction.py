class PageContent(object):
    def __init__(self, url, html, din, ptc, bsrf, genericName, dateListed, 
                 dateDiscontinued, unitPrice, lca, unitIssue, 
                 interchangeable, manufacturer, atc, schedule, coverage, 
                 clients, coverageCriteria, specialAuth):
        self.url = url
        self.html = html
        self.din = din
        self.ptc = ptc
        self.brandName = bsrf.brand
        self.strength = bsrf.strength
        self.route = bsrf.route
        self.dosageForm = bsrf.dosageForm
        self.genericName = genericName
        self.dateListed = dateListed
        self.dateDiscontinued = dateDiscontinued
        self.unitPrice = unitPrice
        self.lca = lca
        self.unitIssue = unitIssue
        self.interchangeable = interchangeable
        self.manufacturer = manufacturer
        self.atc = atc
        self.schedule = schedule
        self.coverage = coverage
        self.clients = clients
        self.criteria = coverageCriteria
        self.specialAuth = specialAuth
        
class PTC(object):
    def __init__(self, ptcList):
        self.num1 = ptcList[0]
        self.text1 = ptcList[1]
        self.num2 = ptcList[2]
        self.text2 = ptcList[3]
        self.num3 = ptcList[4]
        self.text3 = ptcList[5]
        self.num4 = ptcList[6]
        self.text4 = ptcList[7]

class BSRF(object):
    def __init__(self, brand, strength, route, form):
        self.brand = brand
        self.strength = strength
        self.route = route
        self.form = form

class LCA(object):
    def __init__(self, value, text):
        self.value = value
        self.text = text

class ATC(object):
    def __init__(self, atcList):
        self.code1 = atcList[0]
        self.text1 = atcList[1]
        self.code2 = atcList[2]
        self.text2 = atcList[3]
        self.code3 = atcList[4]
        self.text3 = atcList[5]
        self.code4 = atcList[6]
        self.text4 = atcList[7]
        self.code5 = atcList[8]
        self.text5 = atcList[9]

class Clients(object):
    def __init__(self, list):
        self.g1 = list[0]
        self.g66 = list[1]
        self.g66a = list[2]
        self.g19823 = list[3]
        self.g19824 = list[4]
        self.g20400 = list[5]
        self.g20403 = list[6]
        self.g20514 = list[7]
        self.g22128 = list[8]
        self.g23609 = list[9]

class CoverageCriteria(object):
    def __init__(self, criteria, criteriaSA, criteriaP):
        self.criteria = criteria
        self.special = criteriaSA
        self.palliative = criteriaP

class SpecialAuthorization(object):
    def __init__(self, text, link):
        self.text = text
        self.link = link

def collect_parse_data(cursor):
    # Collect BSRF exceptions
    # Collect PTC exceptions
    # Collect ATC descriptions

    return parseData

def download_page(session, url):
    response = session.get(url)
    status = response.status_code

    if status == 200:
        return response.text()
    else:
        raise IOError("%s returned status code %d" % (url, status))

def extract_page_content(page, parseData, log):
    def truncate_content(page):
        """Extracts relevant HTML and returns a BeautifulSoup object"""

        html = BeautifulSoup(page, "html.parser")
        trunc = html.findAll("div", {"class": "columnLeftFull"})

        return trunc
    
    def convert_date(dateString):
        # If date is present, will be in form of dd-mmm-yyyy
        try:
            # Convert to date object
            date = datetime.strptime(dateString, "%d-%b-%Y")

            # Format for MySQL (yyyy-mm-dd)
            date = date.strftime("%y-%m-%d")
        except ValueError:
            # Expected behaviour for most situations without a date
            date = None
        except:
            log.warn("Error trying to parse date for %s" % url)
            date = None

        return date
    
    def extract_din(html):
        """Extracts the DIN"""
        # Get the main HTML element
        din = html.p.string

        # Extract the DIN
        # TO CONFIRM: is the DIN/PIN always 8 digits?
        # If so, would it be better to regex extract?
        din = din.replace("DIN/PIN Detail - ", "")

        return din

    def extract_ptc(html, exceptions, log):
        """Extracts the PTC numbers and descriptions"""
        def parse_ptc(ptcString):
            """Separates out each number and formats descriptions
            
                String is formatted with each number and description 
                on a single line. Sometimes a number will not have a
                description. The raw string is formatted into a list
                where each number is followed by the description, or 
                None in cases where there is no description. The list 
                is then padded to 8 entries (the maximum amount).
            """

            # Removes blank list entries
            rawList = []

            for line in ptcString.split("\n"):
                line = line.strip()

                if line:
                    rawList.append(line)

            # Identfies numbers vs. text to propery arrange list
            numPrev = False

            newList = []

            for line in rawList:
                # Check if this entry is a number
                # All codes have at least 4 digits
                match = re.match(r"\d{4}", line)

                # Entry is number
                if match:
                    # Check if the previous line was a number
                    if numPrev:
                        # Previous entry was number, therefore it did 
                        # not have a text description
                        ptcList.append(None)
                        ptcList.append(line)
                    else:
                        # Previous line was text, can just add number
                        ptcList.append(line)
                        numPrev = True
                
                # Entry is text        
                else:
                    exceptionFound = False

                    for exception in exceptions:
                        if exception.original == line:
                            line = exception.correction
                            exceptionFound = True
                            break

                    if exceptionFound == False:
                        # Convert remainder of text to title case
                        line = line.title()

                    ptcList.append(line)
                    numPrev = False

            # Pad list to 8 items
            while i < 8 - len(ptcList):
                ptcList.append(None)

            return PTC(ptcList)
    
        ptcString = html.find_all('tr', class_="idblTable")[0]\
                        .td.div.p.get_text().strip()

        return parse_ptc(ptcString)

    def extract_brand_strength_route_form(html):
        """Extracts the brand name, strenght, route, and dosage form"""
        
        def parse_brand_name(text):
            '''Properly formats the brand name'''

            # TO DO: MOVE ALL THIS INTO FULL BRAND NAMES AND INTO MYSQL
            #        WILL SWITCH TO MATCHING ENTIRE STRINGS AND LOADING
            #        IT ALL INTO A SET. WILL NEED TO SPEED TEST THIS

            # Convert to title text
            text = text.title()

            # Removes extra space characters
            text = re.sub(r"\s{2,}", " ", text)

            # Targetted replacements			
            # 0
            text = re.sub(r"'S\b", "'s", text)

            # A
            text = re.sub(r"\bAc\b", "AC", text)
            text = re.sub(r"\bAdv\b", "ADV", text)
            text = re.sub(r"\bAerochamber\b", "AeroChamber", text)
            text = re.sub(r"\bAf\b", "AF", text)
            text = re.sub(r"\bAsa\b", "ASA", text)

            # B
            text = re.sub(r"\bBenzaclin\b", "BenzaClin", text)
            text = re.sub(r"\bBid\b", "BID", text)
            text = re.sub(r"\bBp\b", "BP", text)

            # C
            text = re.sub(r"\bCd\b", "CD", text)
            text = re.sub(r"\bChildrens\b", "Children's", text)
            text = re.sub(r"\bCfc\b", "CFC", text)
            text = re.sub(r"\bCr\b", "CR", text)
            text = re.sub(r"\bCtp\b", "CTP", text)

            # D
            text = re.sub(r"\bDdavp\b", "DDAVP", text)
            text = re.sub(r"\bDexiron\b", "DexIron", text)
            text = re.sub(r"\bDf\b", "DF", text)
            text = re.sub(r"\bDhe\b", "DHE", text)
            text = re.sub(r"\bDr\b", "DR", text)
            text = re.sub(r"\bDs\b", "DS", text)
            text = re.sub(r"\bDuotrav\b", "DuoTrav", text)

            # E
            text = re.sub(r"\bEc\b", "EC", text)
            text = re.sub(r"\bEcs\b", "ECS", text)
            text = re.sub(r"\bEnfacare\b", "EnfaCare", text)
            text = re.sub(r"\bEpipen\b", "EpiPen", text)
            text = re.sub(r"\bEr\b", "ER", text)
            text = re.sub(r"\bEs\b", "ES", text)
            text = re.sub(r"\bEz\b", "EZ", text)

            # F
            text = re.sub(r"\bFastab\b", "FasTab", text)
            text = re.sub(r"\bFc\b", "FC", text)
            text = re.sub(r"\bFct\b", "FCT", text)
            text = re.sub(r"\bFemhrt\b", "FemHRT", text)
            text = re.sub(r"\bFlextouch\b", "FlexTouch", text)

            # G
            text = re.sub(r"\bGe\b", "GE", text)
            text = re.sub(r"\bGlucagen\b", "GlucaGen", text)
            text = re.sub(r"\bGluconorm\b", "GlucoNorm", text)
            text = re.sub(r"\bGoquick\b", "GoQuick", text)

            # H
            text = re.sub(r"\bHbv\b", "HBV", text)
            text = re.sub(r"\bHc\b", "HC", text)
            text = re.sub(r"\bHcl\b", "HCl", text)
            text = re.sub(r"\bHct\b", "HCT", text)
            text = re.sub(r"\bHctz\b", "HCTZ", text)
            text = re.sub(r"\bHfa\b", "HFA", text)
            text = re.sub(r"\bHn\b", "HN", text)
            text = re.sub(r"\bHp\b", "HP", text)
            text = re.sub(r"\bHumapen\b", "HumaPen", text)
            text = re.sub(r"\bHypokit\b", "HypoKit", text)

            # I
            text = re.sub(r"\bIbd\b", "IBD", text)
            text = re.sub(r"\bIi\b", "II", text)
            text = re.sub(r"\bIr\b", "IR", text)
            text = re.sub(r"\bIv\b", "IV", text)

            # J

            # K
            text = re.sub(r"\bKwikpen\b", "KwikPen", text)

            # L
            text = re.sub(r"\bLa\b", "LA", text)

            # M
            text = re.sub(r"\bMct\b", "MCT", text)
            text = re.sub(r"\bMetoprol\b", "Metoprolol", text)
            text = re.sub(r"\bMetrocream\b", "MetroCream", text)
            text = re.sub(r"\bMetrogel\b", "MetroGel", text)
            text = re.sub(r"\bMetrolotion\b", "MetroLotion", text)
            text = re.sub(r"\bMinestrin\b", "MinEstrin", text)
            text = re.sub(r"\bMiniquick\b", "MiniQuick", text)
            text = re.sub(r"\bMr\b", "MR", text)
            text = re.sub(r"\bMs\b", "MS", text)
            text = re.sub(r"\bMt\b", "MT", text)
            text = re.sub(r"\bMs4\b", "MS4", text)
            text = re.sub(r"\bMt12\b", "MT12", text)
            text = re.sub(r"\bMt20\b", "MT20", text)
            text = re.sub(r"\bMtx\b", "MTX", text)

            # N
            text = re.sub(r"\bNeosure\b", "NeoSure", text)
            text = re.sub(r"\bNorlevo\b", "NorLevo", text)
            text = re.sub(r"\bNovasource\b", "NovaSource", text)
            text = re.sub(r"\bNovorapid\b", "NovoRapid", text)
            text = re.sub(r"\bNph\b", "NPH", text)
            text = re.sub(r"\bNs\b", "NS", text)
            text = re.sub(r"\bNutrihep\b", "NutriHep", text)

            # O
            text = re.sub(r"\bOdt\b", "ODT", text)
            text = re.sub(r"\bOptichamber\b", "OptiChamber", text)
            text = re.sub(r"\bOxyneo\b", "OxyNeo", text)

            # P
            text = re.sub(r"\bPediasure\b", "PediaSure", text)
            text = re.sub(r"\bPq\b", "PQ", text)

            # Q

            # R
            text = re.sub(r"\bRbv\b", "RBV", text)
            text = re.sub(r"\bRc\b", "RC", text)
            text = re.sub(r"\bRdt\b", "RDT", text)
            text = re.sub(r"\bRpd\b", "RPD", text)

            # S
            text = re.sub(r"\bScandishake\b", "ScandiShake", text)
            text = re.sub(r"\bSdz\b", "SDZ", text)
            text = re.sub(r"\bSod Succin\.", "Sodium Succinate", text)
            text = re.sub(r"\bSolostar\b", "SoloSTAR", text)
            text = re.sub(r"\bSr\b", "SR", text)

            # T
            text = re.sub(r"\bThickenup\b", "ThickenUp", text)
            text = re.sub(r"\bTobradex\b", "TobraDex", text)
            text = re.sub(r"\bTs\b", "TS", text)

            # U
            text = re.sub(r"\bUdv\b", "UDV", text)
            text = re.sub(r"\bUsp\b", "USP", text)

            # V
            text = re.sub(r"\bVhn\b", "VHN", text)
            text = re.sub(r"\bVhp\b", "VHP", text)
            text = re.sub(r"\bVk\b", "VK", text)
            text = re.sub(r"\bVr\b", "VR", text)

            # W

            # X
            text = re.sub(r"\bXc\b", "XC", text)
            text = re.sub(r"\bXl\b", "XL", text)
            text = re.sub(r"\bXr\b", "XR", text)
            text = re.sub(r"\bXrt\b", "XRT", text)

            # Y

            # Z

            #String Replacements	text = text.replace("", "")
            # THIS NEEDS TO BE MOVED INTO AN EXCEPTION INSTEAD OF HERE
            text = text.replace("Sod.(Unpreserved)", "Sodium (Unpreserved)")

            return text

        def parse_strength(text):
            '''Manually corrects errors not fixed by .lower().'''
            
            # Converts the strength to lower case
            text = text.lower()

            # Removes any extra spaces
            text = re.sub(r"\s{2,}", " ", text)

            # Remove any spaces around slashes
            text = re.sub(r"\s/\s", "/", text)

            # Remove any spaces between numbers and %
            text = re.sub(r"\s%", "%", text)

            # Targetted corrections
            text = re.sub(r"\benm\b", "enema", text)
            text = re.sub(r"\biu\b", "IU", text)
            text = re.sub(r"\bmeq\b", "mEq", text)
            text = re.sub(r"\bml\b", "mL", text)
            text = re.sub(r"\bpth\b", "patch", text)
            text = re.sub(r"\bsyr\b", "syringe", text)

            return text
        
        def parse_route(text):
            '''Properly formats the route'''

            # Convert route to lower case
            text = text.lower()

            return text

        def parse_dosage_form(text):
            '''Properly formats the dosage form'''

            # Convert route to lower case
            text = text.lower()

            return text
        
        def split_brand_strength_route_form(text):
            """Extracts brand name, strength, route, dosage form from string
	            Args:
	                text: the extracted text from the html
		
	            Returns:
	                output: a BSRF object
			
	            Raises:
	                None.
            """
            
            # Checks if the text is an exception case
            exceptMatch = False

            for exception in bsrfExceptionList:
                if text == exception[0]:
                    brandName = exception[1]
                    strength = exception[2]
                    route = exception[3]
                    dosageForm = exception[4]

                    exceptMatch = True

                    break

            if exceptMatch:
                # ECL-METFORMIN 500 MG    ORAL   TABLET
                    
                # Splits text multiple strings depending on the format used

                # Formats vary with number of white space between sections
                # TO DO: Check if this search can be sped up with 
                #        different regex patterns
                match3 = r"\b\s{3}\b"
                match4 = r"\b\s{4}\b"

                # Format: B S   R    F
                if re.search(match4, text) and re.search(match3, text):
                
                    text = text.split("   ")
                
                    brandStrength = text[0].strip()
                    route = text[1].strip()
                    dosageForm = text[2].strip()

                # Format: B S    F
                elif re.search(match4, text):
                
                    text = text.split("    ")
                    
                    brandStrength = text[0].strip()
                    route = None
                    dosageForm = text[1].strip()

                # Format: B S   F
                elif re.search(match3, text):
                    text = text.split("   ")
                    brandStrength = text[0].strip()
                    route = None
                    dosageForm = text[1].strip()

                # Format: B S
                else:
                    # B S
                    brandStrength = text
                    route = None
                    dosageForm = None
                
                # Splits the brandStrength at the first number 
                # encountered with text behind it (assumed to 
                # be a unit)
                search = re.search(r"\b\d.+$", text)

                if search:
                    split = search.start()

                    brandName = text[:split].strip()
                    strength = text[split:].strip()
                else:
                    brandName = text
                    strength = None

                # Apply final corrections to extracted information
                brandName = parse_brand_name(output[0])
                strength = parse_strength(output[1])
                route = parse_route(output[2])
                dosageForm = parse_dosage_form(output[3])
            
            output = BSRF(brandName, strength, route, dosageForm)

            return output

        bsrf = html.find_all('tr', class_="idblTable")[1].td.div.string.strip()
        
        return split_brand_strength_route_form(bsrf)

    def extract_generic_name(html):
        """Extracts the generic name"""
        def parse_generic(text):
            """Correct formatting of generic name to be lowercase"""
            """ CONVERT TO A STRAIGHT REPLACEMENT 
            # Regex Replacements			text = re.sub(r"", "", text)
            # 0

            # A
            text = re.sub(r"\ba\b", "A", text)
            text = re.sub(r"\basa\b", "ASA", text)

            # B
            text = re.sub(r"\bb\b", "B", text)
            text = re.sub(r"\bb2\b", "B2", text)
            text = re.sub(r"\bbotulinumtoxina\b", "botulinumtoxinA", text)

            # C
            text = re.sub(r"\bc\b", "C", text)
            text = re.sub(r"\bcitrate,acid\b", "citrate, acid", text)
            text = re.sub(r"\bcl\b", "Cl", text)

            # D
            text = re.sub(r"\bd\b", "D", text)
            text = re.sub(r"\bd3\b", "D3", text)
            text = re.sub(r"\bdessicated\b", "desiccated", text)

            # E
            text = re.sub(r"\be\b", "E", text)

            # H
            text = re.sub(r"\bhbr\b", "HBr", text)
            text = re.sub(r"\bhcl\b", "HCl", text)

            # K
            text = re.sub(r"\bk\b", "K", text)
            text = re.sub(r"\bkd\b", "kD", text)

            # O
            text = re.sub(r"\bonabotulinumtoxina\b", "onabotulinumtoxinA", text)

            # R
            text = re.sub(r"\brdna\b", "RDNA", text)
            text = re.sub(r"\br-dna\b", "RDNA", text)

            # V
            text = re.sub(r"\bvol\b", "volumes", text)
            """
            # NEED TO ACTUALLY CODE THIS
            exceptionList = []
                    
            for item in exceptionList:
                if item.original == text:
                    generic = item.correction
                    exception = True
                    break

            if exception == False:
                # Remove parenthesis on each side of text
                generic = text[1:len(text) - 1]

                # Convert to lower case
                generic = generic.lower()

                # Removes extra space characters
                generic = re.sub(r"\s{2,}", " ", generic)

                # Remove spaces around slashes
                generic = re.sub(r"/\s", "/", generic)

            return generic
            
        generic = html.find_all('tr', class_="idblTable")[2]\
                      .td.div.string.strip()

        return parse_generic(generic)

    def extract_date_listed(html):
        """"""
        dateText = html.find_all('tr', class_="idblTable")[3]\
                       .find_all('td')[1].string.strip()
        
        dateListed = convert_date(dateText)

        return dateListed

    def extract_date_discontinued(html):
        """"""
        dateText  = html.find_all('tr', class_="idblTable")[4]\
                        .find_all('td')[1].string.strip()
        
        dateDiscontinued = convert_date(dateText)
        
        return dateDiscontinued

    def extract_unit_price(html):
        """Extracts the unit price"""
        priceText = html.find_all('tr', class_="idblTable")[5]\
                        .find_all('td')[1].string.strip()

        if priceText == "N/A":
            unitPrice = None
        else:
            unitPrice = priceText

        return priceText

    def extract_lca(html):
        """Extract LCA price and any accompanying text"""
        lcaString = html.find_all('tr', class_="idblTable")[6]\
                        .find_all('td')[1].div.get_text().strip()

        # If the string has a space, it will have LCA text
        if " " in lcaString:
            if "N/A" in lcaString:
                # Note there is a weird case in the old code where
                # a line with a space and N/A, but I could not find
                # such an example; this is for theory only
                lca = None
                lcaText = lcaString[4:]
            else:
                # LCA with text - split at first space to extract
                index = lcaString.find(" ")

                lca = lcaString[0:index]
                lcaText = lcaString[index + 1:]
        # No LCA text present
        else:
            lcaText = None

            # Check if there is any price data
            if "N/A" in lcaString:
                lca = None
            else:
                lca = lcaString

        return LCA(lca, lcaText)

    def extract_unit_issue(html):
        """Extracts the unit of issue"""
        unitText =  html.find_all('tr', class_="idblTable")[7]\
                        .find_all('td')[1].string.strip()

        # Unit of Issue
        unitIssue = unit_issue.lower()

        return unitIssue

    def extract_interchangeable(html):
        """"""
        interchangeable = html.find_all('tr', class_="idblTable")[8]\
                              .find_all('td')[1].get_text()
          
        if "YES" in interchangeable:
            interchangeable = 1
        else:
            interchangeable = 0

    def extract_manufacturer(html):
        """"""
        manufacturer = html.find_all('tr', class_="idblTable")[9]\
                           .find_all('td')[1].a.string.strip()

        def parse_manufactuer(text):
            '''Manually corrects errors that are not fixed by .title()'''
            text = text.title()

            # Removes extra space characters
            text = re.sub(r"\s{2,}", " ", text)

            # Regex Replacements			text = re.sub(r"", "", text)
            # 0

            # A
            text = re.sub(r"\bAa\b", "AA", text)
            text = re.sub(r"\bAb\b", "AB", text)
            text = re.sub(r"\bAbbvieb\b", "AbbVie", text)
            text = re.sub(r"\bAstrazeneca\b", "AstraZeneca", text)

            # B
            text = re.sub(r"\bBgp\b", "BGP", text)
            text = re.sub(r"\bBiomarin\b", "BioMarin", text)

            # E
            text = re.sub(r"\bErfa\b", "ERFA", text)
            text = re.sub(r"\bEmd\b", "EMD", text)

            # F
            text = re.sub(r"\bFze\b", "FZE", text)

            # G
            text = re.sub(r"\bGenmed\b", "GenMed", text)
            text = re.sub(r"\bGlaxosmithkline\b", "GlaxoSmithKline", text)
            text = re.sub(r"\bGmbh\b", "GmbH", text)

            # I
            text = re.sub(r"\bInc(\.|\b)", "Inc.", text)
            text = re.sub(r"\bIncorporated\b", "Inc.", text)

            # L
            text = re.sub(r"\bLeo\b", "LEO", text)
            text = re.sub(r"\bLtd(\.|\b)", "Ltd.", text)
            text = re.sub(r"\bLimited\b", "Ltd.", text)

            # M
            text = re.sub(r"\bMcneil\b", "McNeil", text)

            # N
            text = re.sub(r"\bNj\b", "NJ", text)

            # S
            text = re.sub(r"\bSterimax\b", "SteriMax", text)

            # T
            text = re.sub(r"\bTaropharma\b", "TaroPharma", text)

            # U
            text = re.sub(r"\bUcb\b", "UCB", text)
            text = re.sub(r"\bUk\b", "UK", text)
            text = re.sub(r"\bUlc\b", "ULC", text)

            return text

    def extract_atc(html, descriptions, log):
        """Extracts the ATC codes and assigns description"""
        
        def match_atc(code, descriptions):
            """Matches an ATC code to the description"""
            description = None

            for entry in descriptions:
                if entry.code == code:
                    description = entry.description
                    break

            return description

        def parse_atc(text):
            '''Splits text into a list containing ATC codes and titles.'''
            atcList  = []

            # The regex matches to extract specific content
            searchList = [
                # Level 1: Anatomical Main Group
                "([a-zA-Z]).*$",
		
                # Level 2: Therapeutic Subgroup
                "([a-zA-Z]\d\d).*$",

                # Level 3: Pharmacological Subgroup
                "([a-zA-Z]\d\d[a-zA-Z]).*$",

                # Level 4: Chemical Subgroup
                "([a-zA-Z]\d\d[a-zA-Z][a-zA-Z]).*$",

                # Level 5: Chemical Substance
                "([a-zA-Z]\d\d[a-zA-Z][a-zA-Z]\d\d)*$"
            ]

            for search in searchList:
                match = re.match(search, text)
                
                if match:
                    code = match.group(1)
                    description = match_atc(code)
                else:
                    code = None
                    description = None

                atcList.append(code)
                atcList.append(description)

            return atcList 

        atc = html.find_all('tr', class_="idblTable")[10]\
                  .find_all('td')[1].string.strip()

        atcList = parse_atc(atc)

        return ATC(atcList)

    def extract_schedule(html):
        """Extracts the provincial drug schedule"""
        schedule = html.find_all('tr', class_="idblTable")[11]\
                       .find_all('td')[1].string.strip()

        return schedule

    def extract_coverage(html):
        """Extract the coverage status"""
        coverage = html.find_all('tr', class_="idblTable")[12]\
                       .find_all('td')[1].string.strip()

        coverage = coverage.title()

        return coverage

    def extract_clients(html):
        """Extracts clients and converts to 1/0 representation"""

        clients = html.find_all('tr', class_="idblTable")[13]\
                      .find_all('td')[1].get_text().strip()

        # List of strings to match against
        stringList = ["(Group 1)", "(Group 66)", "(Group 66A", 
                      "Income Support", "(AISH)", "(Group 19824", 
                      "(Group 20400", "(Group 20403", "(Group 20514", 
                      "(Group 22128", "(Group 23609"]
        
        # If string is found in clients text, return 1, otherwise 0
        clientList = []

        for name in stringList:
            if name in clients:
                clientList.append(1)
            else:
                clientList.append(0)

        return Clients(clientList)

    def extract_coverage_criteria(html):
        """Extracts any coverage criteria data"""
        criteriaText = html.find_all('tr', class_="idblTable")[14]\
                           .find_all('td')[1].get_text()
        
        # Default values incase desired info is not found
        criteria = 0
        criteriaSA = None
        criteriaP = None

        if "coverage" in criteriaText:
            criteria = 1

            # Extracts the link element
            criteriaSA = html.find_all('tr', class_="idblTable")[14]\
                             .find_all('td')[1].p\
                             .find_all('a')[0]['onclick']

            # Extracts just the URL for the special auth criteria
            criteriaSA = ("https://idbl.ab.bluecross.ca/idbl/%s" %
                          re.search(r"\('(.+\d)','", criteriaSA).group(1))
            

        if "program" in criteriaText:
            criteria = 1

            # Palliative care link is always the same
            criteriaP = ("http://www.health.alberta.ca/services/"
                            "drugs-palliative-care.html")

        return CoverageCriteria(criteria, criteriaSA, criteriaP)

    def extract_special_auth():
        """Extract any special authorization links"""

        specialElem = html.find_all('tr', class_="idblTable")[15]\
                          .find_all('td')[1]
        
        specialAuth = []
      
        if "N/A" not in specialElem.get_text():
            for a in special_auth_temp.find_all('a'):
                # Grab the text for the special auth link
                text = a.string.strip()

                # Grab and format the pdf link
                link = a['onclick']
                link = ("https://idbl.ab.bluecross.ca%s" 
                        % re.search(r"\('(.+\.pdf)','", link).group(1))

                specialAuth.append(SpecialAuthorization(text, link))

        return specialAuth
        

    # Truncate extra content to improve extraction
    html = truncate_content(page)

    din = extract_din(html)
    ptc = extract_ptc(html, parseData.ptc, log)
    bsrf = extract_brand_strength_route_form(html)
    genericName = extract_generic_name(html)
    dateListed = extract_date_listed(html)
    dateDiscontinued = extract_date_discontinued(html)
    unitPrice = extract_unit_price(html)
    lca = extract_lca(html)
    unitIssue = extract_unit_issue(html)
    interchangeable = extract_interchangeable(html)
    manufacturer = extract_manufacturer(html)
    atc = extract_atc(html, parseData.atc, log)
    schedule = extract_schedule(html)
    coverage = extract_coverage(html)
    clients = extract_clients(html)
    coverageCriteria = extract_coverage_criteria(html)
    specialAuth = extract_special_auth(html)

    # Generate the final object
    pageContent = PageContent(
        url, page, din, ptc, brandName, strength, route, dosageForm, 
        genericName, dateListed, dateDiscontinued, unitPrice, lca, 
        unitIssue, interchangeable, manufacturer, atc, schedule, coverage, 
        clients, coverageCriteria, specialAuth)

    return pageContent

def collect_content(url, session, crawlDelay, parseData, log):
    """Takes a list of URLs and extracts drug pricing information
        args:
            url:        url to extract data from
            session:    requests session object connected to the site
            delay:      time to pause between each request
            cursor:     PyMySQL cursor to query database
            log:        a logging object to send logs to

        returns:
            content:    the PageContent object with all extracted data

        raises:
            none.
    """
    
    from bs4 import BeautifulSoup
    from datetime import datetime
    import time
    import re
    
    # Apply delay before starting
    time.sleep(delay)

    # Download the page content
    try:
        page = download_page(session, url)
    except Exception as e:
        log.warn("Unable to download page content: %e"
                    % (url, e))
        page = None
        pageContent = None

    # Extract relevant information out from the page content
    if page:
        try:
            pageContent = extract_page_content(url, page, parseData, log)
        except Exception as e:
            log.warn("Unable to extract %s page content: %s" 
                        % (url, e))
            pageContent = None

    return pageContent