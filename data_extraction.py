class PageContent(object):
    def __init__(self, url, html, din, ptc, brandName, strength, route, 
                 dosageForm, genericName, dateListed, dateDiscontinued, 
                 unitPrice, lca, unitIssue, interchangeable, manufacturer, 
                 atc, schedule, coverage, clients, coverageCriteria, 
                 specialAuth):
        self.url = url
        self.html = html
        self.din = din
        self.ptc = ptc
        self.brandName = brandName
        self.strength = strength
        self.route = route
        self.dosageForm = dosageForm
        self.genericName = genericName
        self.dateListed = dateListed
        self.dateDiscontinued = dateDiscontinued
        self.dateDiscontinued = unitPrice
        self.lca = lca
        self.unitIssue = unitIssue
        self.interchangeable = interchangeable
        self.manufacturer = manufacturer
        self.atc = atc
        self.schedule = schedule
        self.coverage = coverage
        self.clients = coverageCriteria
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

def download_page(session, url):
    response = session.get(url)
    status = response.status_code

    if status == 200:
        return response.text()
    else:
        raise IOError("%s returned status code %d" % (url, status))

def extract_page_content(page):
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

    def extract_ptc():
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
                    # NEED TO ACTUALLY CODE THIS
                    exceptionList = []
                    
                    for item in exceptionList:
                        if item.original == line:
                            line = item.correction
                            exception = True
                            break

                    if exception == False:
                        # Convert remainder of text to title case
                        line = line.title()

                    ptcList.append(line)
                    numPrev = False

            # Pad list to 8 items
            while i < 8 - len(ptcList):
                ptcList.append(None)

            return PTC(ptcList)
    
        ptcString = html.find_all('tr', class_="idblTable")[0].td.div.p.get_text().strip()

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

    def extract_generic_name():
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
            
        generic = html.find_all('tr', class_="idblTable")[2].td.div.string.strip()

        return parse_generic(generic)

    def extract_date_listed():
        """"""
        dateText = html.find_all('tr', class_="idblTable")[3].find_all('td')[1].string.strip()
        
        dateListed = convert_date(dateText)

        return dateListed

    def extract_date_discontinued():
        """"""
        dateText  = html.find_all('tr', class_="idblTable")[4].find_all('td')[1].string.strip()
        
        dateDiscontinued = convert_date(dateText)
        
        return dateDiscontinued

    def extract_unit_price():
        """Extracts the unit price"""
        priceText = html.find_all('tr', class_="idblTable")[5].find_all('td')[1].string.strip()

        if priceText == "N/A":
            unitPrice = None
        else:
            unitPrice = priceText

        return priceText

    def extract_lca():
        """Extract LCA price and any accompanying text"""
        lcaString = html.find_all('tr', class_="idblTable")[6].find_all('td')[1].div.get_text().strip()

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

    def extract_unit_issue():
        """Extracts the unit of issue"""
        unitText =  html.find_all('tr', class_="idblTable")[7].find_all('td')[1].string.strip()

        # Unit of Issue
        unitIssue = unit_issue.lower()

        return unitIssue

    def extract_interchangeable():
        """"""
        interchangeable = html.find_all('tr', class_="idblTable")[8].find_all('td')[1].get_text()
          
        if "YES" in interchangeable:
            interchangeable = 1
        else:
            interchangeable = 0

    def extract_manufacturer():
        """"""
        manufacturer = html.find_all('tr', class_="idblTable")[9].find_all('td')[1].a.string.strip()

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

    def extract_atc():
        """"""
        atc = html.find_all('tr', class_="idblTable")[10].find_all('td')[1].string.strip()

        def parse_atc(text):
            '''Splits text into a list containing ATC codes and titles.'''
            output = []
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
                try:
                    code = re.match(search, text).group(1)
                    title = match_atc(code)
                except:
                    code = None
                    title = None
                
                output.append(code)
                output.append(title)

            return output

        def match_atc(code):
            match = False
    
            # List of all ATC codes and titles
            atc_list = [
                ["A", "Alimentary tract and metabolism"],
                ["A01", "Stomatological preparations"],
                ["A01A", "Stomatological preparations"],
                ["A01AA", "Caries prophylactic agents"],
                ["A01AB", "Antiinfectives and antiseptics for local oral treatment"],
                ["A01AC", "Corticosteroids for local oral treatment"],
                ["A01AD", "Other agents for local oral treatment"],
                ["A02", "Drugs for acid related disorders"],
                ["A02A", "Antacids"],
                ["A02AA", "Magnesium compounds"],
                ["A02AB", "Aluminium compounds"],
                ["A02AC", "Calcium compounds"],
                ["A02AD", "Combinations and complexes of aluminium, calcium and magnesium compounds"],
                ["A02AF", "Antacids with antiflatulents"],
                ["A02AG", "Antacids with antispasmodics"],
                ["A02AH", "Antacids with sodium bicarbonate"],
                ["A02AX", "Antacids, other combinations"],
                ["A02B", "Drugs for peptic ulcer and gastro-oesophageal reflux disease (GORD)"],
                ["A02BA", "H2-receptor antagonists"],
                ["A02BB", "Prostaglandins"],
                ["A02BC", "Proton pump inhibitors"],
                ["A02BD", "Combinations for eradication of Helicobacter pylori"],
                ["A02BX", "Other drugs for peptic ulcer and gastro-oesophageal reflux disease (GORD)"],
                ["A02X", "Other drugs for acid related disorders"],
                ["A03", "Drugs for functional gastrointestinal disorders"],
                ["A03A", "Drugs for functional gastrointestinal disorders"],
                ["A03AA", "Synthetic anticholinergics, esters with tertiary amino group"],
                ["A03AB", "Synthetic anticholinergics, quaternary ammonium compounds"],
                ["A03AE", "Serotonin receptor antagonists"],
                ["A03AX", "Other drugs for functional gastrointestinal disorders"],
                ["A03B", "Belladonna and derivatives, plain"],
                ["A03BA", "Belladonna alkaloids, tertiary amines"],
                ["A03BB", "Belladonna alkaloids, semisynthetic, quaternary ammonium compounds"],
                ["A03C", "Antispasmodics in combination with psycholeptics"],
                ["A03CA", "Synthetic anticholinergic agents in combination with psycholeptics"],
                ["A03CB", "Belladonna and derivatives in combination with psycholeptics"],
                ["A03CC", "Other antispasmodics in combination with psycholeptics"],
                ["A03D", "Antispasmodics in combination with analgesics"],
                ["A03DC", "Other antispasmodics in combination with analgesics"],
                ["A03E", "Antispasmodics and anticholinergics in combination with other drugs"],
                ["A03EA", "Antispasmodics, psycholeptics and analgesics in combination"],
                ["A03ED", "Antispasmodics in combination with other drugs"],
                ["A03F", "Propulsives"],
                ["A03FA", "Propulsives"],
                ["A04", "Antiemetics and antinauseants"],
                ["A04A", "Antiemetics and antinauseants"],
                ["A04AA", "Serotonin (5HT3) antagonists"],
                ["A04AD", "Other antiemetics"],
                ["A05", "Bile and liver therapy"],
                ["A05A", "Bile therapy"],
                ["A05AA", "Bile acid preparations"],
                ["A05AB", "Preparations for biliary tract therapy"],
                ["A05AX", "Other drugs for bile therapy"],
                ["A05B", "Liver therapy, lipotropics"],
                ["A05BA", "Liver therapy"],
                ["A05C", "Drugs for bile therapy and lipotropics in combination"],
                ["A06", "Drugs for constipation"],
                ["A06A", "Drugs for constipation"],
                ["A06AA", "Softeners, emollients"],
                ["A06AB", "Contact laxatives"],
                ["A06AC", "Bulk-forming laxatives"],
                ["A06AD", "Osmotically acting laxatives"],
                ["A06AG", "Enemas"],
                ["A06AH", "Peripheral opioid receptor antagonists"],
                ["A06AX", "Other drugs for constipation"],
                ["A07", "Antidiarrheals, intestinal antiinflammatory/antiinfective agents"],
                ["A07A", "Intestinal antiinfectives"],
                ["A07AA", "Antibiotics"],
                ["A07AB", "Sulfonamides"],
                ["A07AC", "Imidazole derivatives"],
                ["A07AX", "Other intestinal antiinfectives"],
                ["A07B", "Intestinal adsorbents"],
                ["A07BA", "Charcoal preparations"],
                ["A07BB", "Bismuth preparations"],
                ["A07BC", "Other intestinal adsorbents"],
                ["A07C", "Electrolytes with carbohydrates"],
                ["A07CA", "Oral rehydration salt formulations"],
                ["A07D", "Antipropulsives"],
                ["A07DA", "Antipropulsives"],
                ["A07E", "Intestinal antiinflammatory agents"],
                ["A07EA", "Corticosteroids acting locally"],
                ["A07EB", "Antiallergic agents, excluding corticosteroids"],
                ["A07EC", "Aminosalicylic acid and similar agents"],
                ["A07F", "Antidiarrheal microorganisms"],
                ["A07FA", "Antidiarrheal microorganisms"],
                ["A07X", "Other antidiarrheals"],
                ["A07XA", "Other antidiarrheals"],
                ["A08", "Antiobesity preparations, excluding diet products"],
                ["A08A", "Antiobesity preparations, excluding diet products"],
                ["A08AA", "Centrally acting antiobesity products"],
                ["A08AB", "Peripherally acting antiobesity products"],
                ["A08AX", "Other antiobesity drugs"],
                ["A09", "Digestives, including enzymes"],
                ["A09A", "Digestives, including enzymes"],
                ["A09AA", "Enzyme preparations"],
                ["A09AB", "Acid preparations"],
                ["A09AC", "Enzyme and acid preparations, combinations"],
                ["A10", "Drugs used in diabetes"],
                ["A10A", "Insulins and analogues"],
                ["A10AB", "Insulins and analogues for injection, fast-acting"],
                ["A10AC", "Insulins and analogues for injection, intermediate-acting"],
                ["A10AD", "Insulins and analogues for injection, intermediate- or long-acting combined with fast-acting"],
                ["A10AE", "Insulins and analogues for injection, long-acting"],
                ["A10AF", "Insulins and analogues for inhalation"],
                ["A10B", "Blood glucose lowering drugs, excluding insulins"],
                ["A10BA", "Biguanides"],
                ["A10BB", "Sulfonylureas"],
                ["A10BC", "Sulfonamides (heterocyclic)"],
                ["A10BD", "Combinations of oral blood glucose lowering drugs"],
                ["A10BF", "Alpha glucosidase inhibitors"],
                ["A10BG", "Thiazolidinediones"],
                ["A10BH", "Dipeptidyl peptidase 4 (DPP-4) inhibitors"],
                ["A10BX", "Other blood glucose lowering drugs, excluding insulins"],
                ["A10X", "Other drugs used in diabetes"],
                ["A10XA", "Aldose reductase inhibitors"],
                ["A11", "Vitamins"],
                ["A11A", "Multivitamins, combinations"],
                ["A11AA", "Multivitamins with minerals"],
                ["A11AB", "Multivitamins, other combinations"],
                ["A11B", "Multivitamins, plain"],
                ["A11BA", "Multivitamins, plain"],
                ["A11C", "Vitamin A and D, including combinations of the two"],
                ["A11CA", "Vitamin A, plain"],
                ["A11CB", "Vitamin A and D in combination"],
                ["A11CC", "Vitamin D and analogues"],
                ["A11D", "Vitamin B1, plain and in combination with vitamin B6 and B12"],
                ["A11DA", "Vitamin B1, plain"],
                ["A11DB", "Vitamin B1 in combination with vitamin B6 and/or vitamin B12"],
                ["A11E", "Vitamin B-complex, including combinations"],
                ["A11EA", "Vitamin B-complex, plain"],
                ["A11EB", "Vitamin B-complex with vitamin C"],
                ["A11EC", "Vitamin B-complex with minerals"],
                ["A11ED", "Vitamin B-complex with anabolic steroids"],
                ["A11EX", "Vitamin B-complex, other combinations"],
                ["A11G", "Ascorbic acid (vitamin C), including combinations"],
                ["A11GA", "Ascorbic acid (vitamin C), plain"],
                ["A11GB", "Ascorbic acid (vitamin C), combinations"],
                ["A11H", "Other plain vitamin preparations"],
                ["A11HA", "Other plain vitamin preparations"],
                ["A11J", "Other vitamin products, combinations"],
                ["A11JA", "Combinations of vitamins"],
                ["A11JB", "Vitamins with minerals"],
                ["A11JC", "Vitamins, other combinations"],
                ["A12", "Mineral supplements"],
                ["A12A", "Calcium"],
                ["A12AA", "Calcium"],
                ["A12AX", "Calcium, combinations with vitamin d and/or other drugs"],
                ["A12B", "Potassium"],
                ["A12BA", "Potassium"],
                ["A12C", "Other mineral supplements"],
                ["A12CA", "Sodium"],
                ["A12CB", "Zinc"],
                ["A12CC", "Magnesium"],
                ["A12CD", "Fluoride"],
                ["A12CE", "Selenium"],
                ["A12CX", "Other mineral products"],
                ["A13", "Tonics"],
                ["A13A", "Tonics"],
                ["A14", "Anabolic agents for systemic use"],
                ["A14B", "Other anabolic agents"],
                ["A15", "Appetite stimulants"],
                ["A16", "Other alimentary tract and metabolism products"],
                ["A16A", "Other alimentary tract and metabolism products"],
                ["A16AA", "Amino acids and derivatives"],
                ["A16AB", "Enzymes"],
                ["A16AX", "Various alimentary tract and metabolism products"],
                ["B", "Blood and blood forming organs"],
                ["B01", "Antithrombotic agents"],
                ["B01A", "Antithrombotic agents"],
                ["B01AA", "Vitamin K antagonists"],
                ["B01AB", "Heparin group"],
                ["B01AC", "Platelet aggregation inhibitors excluding heparin"],
                ["B01AD", "Enzymes"],
                ["B01AE", "Direct thrombin inhibitors"],
                ["B01AF", "Direct factor Xa inhibitors"],
                ["B01AX", "Other antithrombotic agents"],
                ["B02", "Antihemorrhagics"],
                ["B02A", "Antifibrinolytics"],
                ["B02AA", "Amino acids"],
                ["B02AB", "Proteinase inhibitors"],
                ["B02B", "Vitamin K and other hemostatics"],
                ["B02BA", "Vitamin K"],
                ["B02BB", "Fibrinogen"],
                ["B02BC", "Local hemostatics"],
                ["B02BD", "Blood coagulation factors"],
                ["B02BX", "Other systemic hemostatics"],
                ["B03", "Antianemic preparations"],
                ["B03A", "Iron preparations"],
                ["B03AA", "Iron bivalent, oral preparations"],
                ["B03AB", "Iron trivalent, oral preparations"],
                ["B03AC", "Iron, parenteral preparations"],
                ["B03AD", "Iron in combination with folic acid"],
                ["B03AE", "Iron in other combinations"],
                ["B03B", "Vitamin B12 and folic acid"],
                ["B03BA", "Vitamin B12 (cyanocobalamin and analogues)"],
                ["B03BB", "Folic acid and derivatives"],
                ["B03X", "Other antianemic preparations"],
                ["B03XA", "Other antianemic preparations"],
                ["B05", "Blood substitutes and perfusion solutions"],
                ["B05A", "Blood and related products"],
                ["B05AA", "Blood substitutes and plasma protein fractions"],
                ["B05AX", "Other blood products"],
                ["B05B", "I.V. solutions"],
                ["B05BA", "Solutions for parenteral nutrition"],
                ["B05BB", "Solutions affecting the electrolyte balance"],
                ["B05BC", "Solutions producing osmotic diuresis"],
                ["B05C", "Irrigating solutions"],
                ["B05CA", "Antiinfectives"],
                ["B05CB", "Salt solutions"],
                ["B05CX", "Other irrigating solutions"],
                ["B05D", "Peritoneal dialytics"],
                ["B05DA", "Isotonic solutions"],
                ["B05DB", "Hypertonic solutions"],
                ["B05X", "I.V. solution additives"],
                ["B05XA", "Electrolyte solutions"],
                ["B05XB", "Amino acids"],
                ["B05XC", "Vitamins"],
                ["B05XX", "Other I.V. solution additives"],
                ["B05Z", "Hemodialytics and hemofiltrates"],
                ["B05ZA", "Hemodialytics, concentrates"],
                ["B05ZB", "Hemofiltrates"],
                ["B06", "Other hematological agents"],
                ["B06A", "Other hematological agents"],
                ["B06AA", "Enzymes"],
                ["B06AB", "Other hem products"],
                ["B06AC", "Drugs used in hereditary angioedema"],
                ["C", "Cardiovascular system"],
                ["C01", "Cardiac therapy"],
                ["C01A", "Cardiac glycosides"],
                ["C01AA", "Digitalis glycosides"],
                ["C01AB", "Scilla glycosides"],
                ["C01AC", "Strophantus glycosides"],
                ["C01AX", "Other cardiac glycosides"],
                ["C01B", "Antiarrhythmics, class I and III"],
                ["C01BA", "Antiarrhythmics, class Ia"],
                ["C01BB", "Antiarrhythmics, class Ib"],
                ["C01BC", "Antiarrhythmics, class Ic"],
                ["C01BD", "Antiarrhythmics, class III"],
                ["C01BG", "Other antiarrhythmics, class I and III"],
                ["C01C", "Cardiac stimulants excluding cardiac glycosides"],
                ["C01CA", "Adrenergic and dopaminergic agents"],
                ["C01CE", "Phosphodiesterase inhibitors"],
                ["C01CX", "Other cardiac stimulants"],
                ["C01D", "Vasodilators used in cardiac diseases"],
                ["C01DA", "Organic nitrates"],
                ["C01DB", "Quinolone vasodilators"],
                ["C01DX", "Other vasodilators used in cardiac diseases"],
                ["C01E", "Other cardiac preparations"],
                ["C01EA", "Prostaglandins"],
                ["C01EB", "Other cardiac preparations"],
                ["C01EX", "Other cardiac combination products"],
                ["C02", "Antihypertensives"],
                ["C02A", "Antiadrenergic agents, centrally acting"],
                ["C02AA", "Rauwolfia alkaloids"],
                ["C02AB", "Methyldopa"],
                ["C02AC", "Imidazoline receptor agonists"],
                ["C02B", "Antiadrenergic agents, ganglion-blocking"],
                ["C02BA", "Sulfonium derivatives"],
                ["C02BB", "Secondary and tertiary amines"],
                ["C02BC", "Bisquaternary ammonium compounds"],
                ["C02C", "Antiadrenergic agents, peripherally acting"],
                ["C02CA", "Alpha-adrenoreceptor antagonists"],
                ["C02CC", "Guanidine derivatives"],
                ["C02D", "Arteriolar smooth muscle, agents acting on"],
                ["C02DA", "Thiazide derivatives"],
                ["C02DB", "Hydrazinophthalazine derivatives"],
                ["C02DC", "Pyrimidine derivatives"],
                ["C02DD", "Nitroferricyanide derivatives"],
                ["C02DG", "Guanidine derivatives"],
                ["C02K", "Other antihypertensives"],
                ["C02KA", "Alkaloids, excluding rauwolfia"],
                ["C02KB", "Tyrosine hydroxylase inhibitors"],
                ["C02KC", "Mao inhibitors"],
                ["C02KD", "Serotonin antagonists"],
                ["C02KX", "Antihypertensives for pulmonary arterial hypertension"],
                ["C02L", "Antihypertensives and diuretics in combination"],
                ["C02LA", "Rauwolfia alkaloids and diuretics in combination"],
                ["C02LB", "Methyldopa and diuretics in combination"],
                ["C02LC", "Imidazoline receptor agonists in combination with diuretics"],
                ["C02LE", "Alpha-adrenoreceptor antagonists and diuretics"],
                ["C02LF", "Guanidine derivatives and diuretics"],
                ["C02LG", "Hydrazinophthalazine derivatives and diuretics"],
                ["C02LK", "Alkaloids, excluding rauwolfia, in combination with diuretics"],
                ["C02LL", "MAO inhibitors and diuretics"],
                ["C02LN", "Serotonin antagonists and diuretics"],
                ["C02LX", "Other antihypertensives and diuretics"],
                ["C02N", "Combinations of antihypertensives in ATC group C02"],
                ["C03", "Diuretics"],
                ["C03A", "Low-ceiling diuretics, thiazides"],
                ["C03AA", "Thiazides, plain"],
                ["C03AB", "Thiazides and potassium in combination"],
                ["C03AH", "Thiazides, combinations with psycholeptics and/or analgesics"],
                ["C03AX", "Thiazides, combinations with other drugs"],
                ["C03B", "Low-ceiling diuretics, excluding thiazides"],
                ["C03BA", "Sulfonamides, plain"],
                ["C03BB", "Sulfonamides and potassium in combination"],
                ["C03BC", "Mercurial diuretics"],
                ["C03BD", "Xanthine derivatives"],
                ["C03BK", "Sulfonamides, combinations with other drugs"],
                ["C03BX", "Other low-ceiling diuretics"],
                ["C03C", "High-ceiling diuretics"],
                ["C03CA", "Sulfonamides, plain"],
                ["C03CB", "Sulfonamides and potassium in combination"],
                ["C03CC", "Aryloxyacetic acid derivatives"],
                ["C03CD", "Pyrazolone derivatives"],
                ["C03CX", "Other high-ceiling diuretics"],
                ["C03D", "Potassium-sparing agents"],
                ["C03DA", "Aldosterone antagonists"],
                ["C03DB", "Other potassium-sparing agents"],
                ["C03E", "Diuretics and potassium-sparing agents in combination"],
                ["C03EA", "Low-ceiling diuretics and potassium-sparing agents"],
                ["C03EB", "High-ceiling diuretics and potassium-sparing agents"],
                ["C03X", "Other diuretics"],
                ["C03XA", "Vasopressin antagonists"],
                ["C04", "Peripheral vasodilators"],
                ["C04A", "Peripheral vasodilators"],
                ["C04AA", "2-amino-1-phenylethanol derivatives"],
                ["C04AB", "Imidazoline derivatives"],
                ["C04AC", "Nicotinic acid and derivatives"],
                ["C04AD", "Purine derivatives"],
                ["C04AE", "Ergot alkaloids"],
                ["C04AF", "Enzymes"],
                ["C04AX", "Other peripheral vasodilators"],
                ["C05", "Vasoprotectives"],
                ["C05A", "Agents for treatment of hemorrhoids and anal fissures for topical use"],
                ["C05AA", "Corticosteroids"],
                ["C05AB", "Antibiotics"],
                ["C05AD", "Local anesthetics"],
                ["C05AE", "Muscle relaxants"],
                ["C05AX", "Other agents for treatment of hemorrhoids and anal fissures for topical use"],
                ["C05B", "Antivaricose therapy"],
                ["C05BA", "Heparins or heparinoids for topical use"],
                ["C05BB", "Sclerosing agents for local injection"],
                ["C05BX", "Other sclerosing agents"],
                ["C05C", "Capillary stabilizing agents"],
                ["C05CA", "Bioflavonoids"],
                ["C05CX", "Other capillary stabilizing agents"],
                ["C07", "Beta blocking agents"],
                ["C07A", "Beta blocking agents"],
                ["C07AA", "Beta blocking agents, non-selective"],
                ["C07AB", "Beta blocking agents, selective"],
                ["C07AG", "Alpha and beta blocking agents"],
                ["C07B", "Beta blocking agents and thiazides"],
                ["C07BA", "Beta blocking agents, non-selective, and thiazides"],
                ["C07BB", "Beta blocking agents, selective, and thiazides"],
                ["C07BG", "Alpha and beta blocking agents and thiazides"],
                ["C07C", "Beta blocking agents and other diuretics"],
                ["C07CA", "Beta blocking agents, non-selective, and other diuretics"],
                ["C07CB", "Beta blocking agents, selective, and other diuretics"],
                ["C07CG", "Alpha and beta blocking agents and other diuretics"],
                ["C07D", "Beta blocking agents, thiazides and other diuretics"],
                ["C07DA", "Beta blocking agents, non-selective, thiazides and other diuretics"],
                ["C07DB", "Beta blocking agents, selective, thiazides and other diuretics"],
                ["C07E", "Beta blocking agents and vasodilators"],
                ["C07EA", "Beta blocking agents, non-selective, and vasodilators"],
                ["C07EB", "Beta blocking agents, selective, and vasodilators"],
                ["C07F", "Beta blocking agents and other antihypertensives"],
                ["C07FA", "Beta blocking agents, non-selective, and other antihypertensives"],
                ["C07FB", "Beta blocking agents, selective, and other antihypertensives"],
                ["C08", "Calcium channel blockers"],
                ["C08C", "Selective calcium channel blockers with mainly vascular effects"],
                ["C08CA", "Dihydropyridine derivatives"],
                ["C08CX", "Other selective calcium channel blockers with mainly vascular effects"],
                ["C08D", "Selective calcium channel blockers with direct cardiac effects"],
                ["C08DA", "Phenylalkylamine derivatives"],
                ["C08DB", "Benzothiazepine derivatives"],
                ["C08E", "Non-selective calcium channel blockers"],
                ["C08EA", "Phenylalkylamine derivatives"],
                ["C08EX", "Other non-selective calcium channel blockers"],
                ["C08G", "Calcium channel blockers and diuretics"],
                ["C08GA", "Calcium channel blockers and diuretics"],
                ["C09", "Agents acting on the renin-angiotensin system"],
                ["C09A", "ACE inhibitors, plain"],
                ["C09AA", "ACE inhibitors, plain"],
                ["C09B", "ACE inhibitors, combinations"],
                ["C09BA", "ACE inhibitors and diuretics"],
                ["C09BB", "ACE inhibitors and calcium channel blockers"],
                ["C09BX", "ACE inhibitors, other combinations"],
                ["C09C", "Angiotensin II antagonists, plain"],
                ["C09CA", "Angiotensin II antagonists, plain"],
                ["C09D", "Angiotensin II antagonists, combinations"],
                ["C09DA", "Angiotensin II antagonists and diuretics"],
                ["C09DB", "Angiotensin II antagonists and calcium channel blockers"],
                ["C09DX", "Angiotensin II antagonists, other combinations"],
                ["C09X", "Other agents acting on the renin-angiotensin system"],
                ["C09XA", "Renin-inhibitors"],
                ["C10", "Lipid modifying agents"],
                ["C10A", "Lipid modifying agents, plain"],
                ["C10AA", "HMG CoA reductase inhibitors"],
                ["C10AB", "Fibrates"],
                ["C10AC", "Bile acid sequestrants"],
                ["C10AD", "Nicotinic acid and derivatives"],
                ["C10AX", "Other lipid modifying agents"],
                ["C10B", "Lipid modifying agents, combinations"],
                ["C10BA", "HMG CoA reductase inhibitors in combination with other lipid modifying agents"],
                ["C10BX", "HMG CoA reductase inhibitors, other combinations"],
                ["D", "Dermatologicals"],
                ["D01", "Antifungals for dermatological use"],
                ["D01A", "Antifungals for topical use"],
                ["D01AA", "Antibiotics"],
                ["D01AC", "Imidazole and triazole derivatives"],
                ["D01AE", "Other antifungals for topical use"],
                ["D01B", "Antifungals for systemic use"],
                ["D01BA", "Antifungals for systemic use"],
                ["D02", "Emollients and protectives"],
                ["D02A", "Emollients and protectives"],
                ["D02AA", "Silicone products"],
                ["D02AB", "Zinc products"],
                ["D02AC", "Soft paraffin and fat products"],
                ["D02AD", "Liquid plasters"],
                ["D02AE", "Carbamide products"],
                ["D02AF", "Salicylic acid preparations"],
                ["D02AX", "Other emollients and protectives"],
                ["D02B", "Protectives against uv-radiation"],
                ["D02BA", "Protectives against uv-radiation for topical use"],
                ["D02BB", "Protectives against uv-radiation for systemic use"],
                ["D03", "Preparations for treatment of wounds and ulcers"],
                ["D03A", "Cicatrizants"],
                ["D03AA", "Cod-liver oil ointments"],
                ["D03AX", "Other cicatrizants"],
                ["D03B", "Enzymes"],
                ["D03BA", "Proteolytic enzymes"],
                ["D04", "Antipruritics, including antihistamines, anesthetics, etc."],
                ["D04A", "Antipruritics, including antihistamines, anesthetics, etc."],
                ["D04AA", "Antihistamines for topical use"],
                ["D04AB", "Anesthetics for topical use"],
                ["D04AX", "Other antipruritics"],
                ["D05", "Antipsoriatics"],
                ["D05A", "Antipsoriatics for topical use"],
                ["D05AA", "Tars"],
                ["D05AC", "Antracen derivatives"],
                ["D05AD", "Psoralens for topical use"],
                ["D05AX", "Other antipsoriatics for topical use"],
                ["D05B", "Antipsoriatics for systemic use"],
                ["D05BA", "Psoralens for systemic use"],
                ["D05BB", "Retinoids for treatment of psoriasis"],
                ["D05BX", "Other antipsoriatics for systemic use"],
                ["D06", "Antibiotics and chemotherapeutics for dermatological use"],
                ["D06A", "Antibiotics for topical use"],
                ["D06AA", "Tetracycline and derivatives"],
                ["D06AX", "Other antibiotics for topical use"],
                ["D06B", "Chemotherapeutics for topical use"],
                ["D06BA", "Sulfonamides"],
                ["D06BB", "Antivirals"],
                ["D06BX", "Other chemotherapeutics"],
                ["D06C", "Antibiotics and chemotherapeutics, combinations"],
                ["D07", "Corticosteroids, dermatological preparations"],
                ["D07A", "Corticosteroids, plain"],
                ["D07AA", "Corticosteroids, weak (group I)"],
                ["D07AB", "Corticosteroids, moderately potent (group II)"],
                ["D07AC", "Corticosteroids, potent (group III)"],
                ["D07AD", "Corticosteroids, very potent (group IV)"],
                ["D07B", "Corticosteroids, combinations with antiseptics"],
                ["D07BA", "Corticosteroids, weak, combinations with antiseptics"],
                ["D07BB", "Corticosteroids, moderately potent, combinations with antiseptics"],
                ["D07BC", "Corticosteroids, potent, combinations with antiseptics"],
                ["D07BD", "Corticosteroids, very potent, combinations with antiseptics"],
                ["D07C", "Corticosteroids, combinations with antibiotics"],
                ["D07CA", "Corticosteroids, weak, combinations with antibiotics"],
                ["D07CB", "Corticosteroids, moderately potent, combinations with antibiotics"],
                ["D07CC", "Corticosteroids, potent, combinations with antibiotics"],
                ["D07CD", "Corticosteroids, very potent, combinations with antibiotics"],
                ["D07X", "Corticosteroids, other combinations"],
                ["D07XA", "Corticosteroids, weak, other combinations"],
                ["D07XB", "Corticosteroids, moderately potent, other combinations"],
                ["D07XC", "Corticosteroids, potent, other combinations"],
                ["D07XD", "Corticosteroids, very potent, other combinations"],
                ["D08", "Antiseptics and disinfectants"],
                ["D08A", "Antiseptics and disinfectants"],
                ["D08AA", "Acridine derivatives"],
                ["D08AB", "Aluminium agents"],
                ["D08AC", "Biguanides and amidines"],
                ["D08AD", "Boric acid products"],
                ["D08AE", "Phenol and derivatives"],
                ["D08AF", "Nitrofuran derivatives"],
                ["D08AG", "Iodine products"],
                ["D08AH", "Quinoline derivatives"],
                ["D08AJ", "Quaternary ammonium compounds"],
                ["D08AK", "Mercurial products"],
                ["D08AL", "Silver compounds"],
                ["D08AX", "Other antiseptics and disinfectants"],
                ["D09", "Medicated dressings"],
                ["D09A", "Medicated dressings"],
                ["D09AA", "Medicated dressings with antiinfectives"],
                ["D09AB", "Zinc bandages"],
                ["D09AX", "Soft paraffin dressings"],
                ["D10", "Anti-acne preparations"],
                ["D10A", "Anti-acne preparations for topical use"],
                ["D10AA", "Corticosteroids, combinations for treatment of acne"],
                ["D10AB", "Preparations containing sulfur"],
                ["D10AD", "Retinoids for topical use in acne"],
                ["D10AE", "Peroxides"],
                ["D10AF", "Antiinfectives for treatment of acne"],
                ["D10AX", "Other anti-acne preparations for topical use"],
                ["D10B", "Anti-acne preparations for systemic use"],
                ["D10BA", "Retinoids for treatment of acne"],
                ["D10BX", "Other anti-acne preparations for systemic use"],
                ["D11", "Other dermatological preparations"],
                ["D11A", "Other dermatological preparations"],
                ["D11AA", "Antihidrotics"],
                ["D11AC", "Medicated shampoos"],
                ["D11AE", "Androgens for topical use"],
                ["D11AF", "Wart and anti-corn preparations"],
                ["D11AH", "Agents for dermatitis, excluding corticosteroids"],
                ["D11AX", "Other dermatologicals"],
                ["G", "Genito urinary system and sex hormones"],
                ["G01", "Gynecological antiinfectives and antiseptics"],
                ["G01A", "Antiinfectives and antiseptics, excluding combinations with corticosteroids"],
                ["G01AA", "Antibiotics"],
                ["G01AB", "Arsenic compounds"],
                ["G01AC", "Quinoline derivatives"],
                ["G01AD", "Organic acids"],
                ["G01AE", "Sulfonamides"],
                ["G01AF", "Imidazole derivatives"],
                ["G01AG", "Triazole derivatives"],
                ["G01AX", "Other antiinfectives and antiseptics"],
                ["G01B", "Antiinfectives/antiseptics in combination with corticosteroids"],
                ["G01BA", "Antibiotics and corticosteroids"],
                ["G01BC", "Quinoline derivatives and corticosteroids"],
                ["G01BD", "Antiseptics and corticosteroids"],
                ["G01BE", "Sulfonamides and corticosteroids"],
                ["G01BF", "Imidazole derivatives and corticosteroids"],
                ["G02", "Other gynecologicals"],
                ["G02A", "Uterotonics"],
                ["G02AB", "Ergot alkaloids"],
                ["G02AC", "Ergot alkaloids and oxytocin including analogues, in combination"],
                ["G02AD", "Prostaglandins"],
                ["G02AX", "Other uterotonics"],
                ["G02B", "Contraceptives for topical use"],
                ["G02BA", "Intrauterine contraceptives"],
                ["G02BB", "Intravaginal contraceptives"],
                ["G02C", "Other gynecologicals"],
                ["G02CA", "Sympathomimetics, labour repressants"],
                ["G02CB", "Prolactine inhibitors"],
                ["G02CC", "Antiinflammatory products for vaginal administration"],
                ["G02CX", "Other gynecologicals"],
                ["G03", "Sex hormones and modulators of the genital system"],
                ["G03A", "Hormonal contraceptives for systemic use"],
                ["G03AA", "Progestogens and estrogens, fixed combinations"],
                ["G03AB", "Progestogens and estrogens, sequential preparations"],
                ["G03AC", "Progestogens"],
                ["G03AD", "Emergency contraceptives"],
                ["G03B", "Androgens"],
                ["G03BA", "3-oxoandrosten (4) derivatives"],
                ["G03BB", "5-androstanon (3) derivatives"],
                ["G03C", "Estrogens"],
                ["G03CA", "Natural and semisynthetic estrogens, plain"],
                ["G03CB", "Synthetic estrogens, plain"],
                ["G03CC", "Estrogens, combinations with other drugs"],
                ["G03CX", "Other estrogens"],
                ["G03D", "Progestogens"],
                ["G03DA", "Pregnen (4) derivatives"],
                ["G03DB", "Pregnadien derivatives"],
                ["G03DC", "Estren derivatives"],
                ["G03E", "Androgens and female sex hormones in combination"],
                ["G03EA", "Androgens and estrogens"],
                ["G03EB", "Androgen, progestogen and estrogen in combination"],
                ["G03EK", "Androgens and female sex hormones in combination with other drugs"],
                ["G03F", "Progestogens and estrogens in combination"],
                ["G03FA", "Progestogens and estrogens, fixed combinations"],
                ["G03FB", "Progestogens and estrogens, sequential preparations"],
                ["G03G", "Gonadotropins and other ovulation stimulants"],
                ["G03GA", "Gonadotropins"],
                ["G03GB", "Ovulation stimulants, synthetic"],
                ["G03H", "Antiandrogens"],
                ["G03HA", "Antiandrogens, plain"],
                ["G03HB", "Antiandrogens and estrogens"],
                ["G03X", "Other sex hormones and modulators of the genital system"],
                ["G03XA", "Antigonadotropins and similar agents"],
                ["G03XB", "Progesterone receptor modulators"],
                ["G03XC", "Selective estrogen receptor modulators"],
                ["G04", "Urologicals"],
                ["G04B", "Urologicals"],
                ["G04BA", "Acidifiers"],
                ["G04BC", "Urinary concrement solvents"],
                ["G04BD", "Drugs for urinary frequency and incontinence"],
                ["G04BE", "Drugs used in erectile dysfunction"],
                ["G04BX", "Other urologicals"],
                ["G04C", "Drugs used in benign prostatic hypertrophy"],
                ["G04CA", "Alpha-adrenoreceptor antagonists"],
                ["G04CB", "Testosterone-5-alpha reductase inhibitors"],
                ["G04CX", "Other drugs used in benign prostatic hypertrophy"],
                ["H", "Systemic hormonal preparations, excluding sex hormones and insulins"],
                ["H01", "Pituitary and hypothalamic hormones and analogues"],
                ["H01A", "Anterior pituitary lobe hormones and analogues"],
                ["H01AA", "ACTH"],
                ["H01AB", "Thyrotropin"],
                ["H01AC", "Somatropin and somatropin agonists"],
                ["H01AX", "Other anterior pituitary lobe hormones and analogues"],
                ["H01B", "Posterior pituitary lobe hormones"],
                ["H01BA", "Vasopressin and analogues"],
                ["H01BB", "Oxytocin and analogues"],
                ["H01C", "Hypothalamic hormones"],
                ["H01CA", "Gonadotropin-releasing hormones"],
                ["H01CB", "Somatostatin and analogues"],
                ["H01CC", "Anti-gonadotropin-releasing hormones"],
                ["H02", "Corticosteroids for systemic use"],
                ["H02A", "Corticosteroids for systemic use, plain"],
                ["H02AA", "Mineralocorticoids"],
                ["H02AB", "Glucocorticoids"],
                ["H02B", "Corticosteroids for systemic use, combinations"],
                ["H02BX", "Corticosteroids for systemic use, combinations"],
                ["H02C", "Antiadrenal preparations"],
                ["H02CA", "Anticorticosteroids"],
                ["H03", "Thyroid therapy"],
                ["H03A", "Thyroid preparations"],
                ["H03AA", "Thyroid hormones"],
                ["H03B", "Antithyroid preparations"],
                ["H03BA", "Thiouracils"],
                ["H03BB", "Sulfur-containing imidazole derivatives"],
                ["H03BC", "Perchlorates"],
                ["H03BX", "Other antithyroid preparations"],
                ["H03C", "Iodine therapy"],
                ["H03CA", "Iodine therapy"],
                ["H04", "Pancreatic hormones"],
                ["H04A", "Glycogenolytic hormones"],
                ["H04AA", "Glycogenolytic hormones"],
                ["H05", "Calcium homeostasis"],
                ["H05A", "Parathyroid hormones and analogues"],
                ["H05AA", "Parathyroid hormones and analogues"],
                ["H05B", "Anti-parathyroid agents"],
                ["H05BA", "Calcitonin preparations"],
                ["H05BX", "Other anti-parathyroid agents"],
                ["J", "Antiiinfectives for systemic use"],
                ["J01", "Antibacterials for systemic use"],
                ["J01A", "Tetracyclines"],
                ["J01AA", "Tetracyclines"],
                ["J01B", "Amphenicols"],
                ["J01BA", "Amphenicols"],
                ["J01C", "Beta-lactam antibacterials, penicillins"],
                ["J01CA", "Penicillins with extended spectrum"],
                ["J01CE", "Beta-lactamase sensitive penicillins"],
                ["J01CF", "Beta-lactamase resistant penicillins"],
                ["J01CG", "Beta-lactamase inhibitors"],
                ["J01CR", "Combinations of penicillins, including beta-lactamase inhibitors"],
                ["J01D", "Other beta-lactam antibacterials"],
                ["J01DB", "First-generation cephalosporins"],
                ["J01DC", "Second-generation cephalosporins"],
                ["J01DD", "Third-generation cephalosporins"],
                ["J01DE", "Fourth-generation cephalosporins"],
                ["J01DF", "Monobactams"],
                ["J01DH", "Carbapenems"],
                ["J01DI", "Other cephalosporins and penems"],
                ["J01E", "Sulfonamides and trimethoprim"],
                ["J01EA", "Trimethoprim and derivatives"],
                ["J01EB", "Short-acting sulfonamides"],
                ["J01EC", "Intermediate-acting sulfonamides"],
                ["J01ED", "Long-acting sulfonamides"],
                ["J01EE", "Combinations of sulfonamides and trimethoprim, including derivatives"],
                ["J01F", "Macrolides, lincosamides and streptogramins"],
                ["J01FA", "Macrolides"],
                ["J01FF", "Lincosamides"],
                ["J01FG", "Streptogramins"],
                ["J01G", "Aminoglycoside antibacterials"],
                ["J01GA", "Streptomycins"],
                ["J01GB", "Other aminoglycosides"],
                ["J01M", "Quinolone antibacterials"],
                ["J01MA", "Fluoroquinolones"],
                ["J01MB", "Other quinolones"],
                ["J01R", "Combinations of antibacterials"],
                ["J01RA", "Combinations of antibacterials"],
                ["J01X", "Other antibacterials"],
                ["J01XA", "Glycopeptide antibacterials"],
                ["J01XB", "Polymyxins"],
                ["J01XC", "Steroid antibacterials"],
                ["J01XD", "Imidazole derivatives"],
                ["J01XE", "Nitrofuran derivatives"],
                ["J01XX", "Other antibacterials"],
                ["J02", "Antimycotics for systemic use"],
                ["J02A", "Antimycotics for systemic use"],
                ["J02AA", "Antibiotics"],
                ["J02AB", "Imidazole derivatives"],
                ["J02AC", "Triazole derivatives"],
                ["J02AX", "Other antimycotics for systemic use"],
                ["J04", "Antimycobacterials"],
                ["J04A", "Drugs for treatment of tuberculosis"],
                ["J04AA", "Aminosalicylic acid and derivatives"],
                ["J04AB", "Antibiotics"],
                ["J04AC", "Hydrazides"],
                ["J04AD", "Thiocarbamide derivatives"],
                ["J04AK", "Other drugs for treatment of tuberculosis"],
                ["J04AM", "Combinations of drugs for treatment of tuberculosis"],
                ["J04B", "Drugs for treatment of lepra"],
                ["J04BA", "Drugs for treatment of lepra"],
                ["J05", "Antivirals for systemic use"],
                ["J05A", "Direct acting antivirals"],
                ["J05AA", "Thiosemicarbazones"],
                ["J05AB", "Nucleosides and nucleotides excluding reverse transcriptase inhibitors"],
                ["J05AC", "Cyclic amines"],
                ["J05AD", "Phosphonic acid derivatives"],
                ["J05AE", "Protease inhibitors"],
                ["J05AF", "Nucleoside and nucleotide reverse transcriptase inhibitors"],
                ["J05AG", "Non-nucleoside reverse transcriptase inhibitors"],
                ["J05AH", "Neuraminidase inhibitors"],
                ["J05AR", "Antivirals for treatment of hiv infections, combinations"],
                ["J05AX", "Other antivirals"],
                ["J06", "Immune sera and immunoglobulins"],
                ["J06A", "Immune sera"],
                ["J06AA", "Immune sera"],
                ["J06B", "Immunoglobulins"],
                ["J06BA", "Immunoglobulins, normal human"],
                ["J06BB", "Specific immunoglobulins"],
                ["J06BC", "Other immunoglobulins"],
                ["J07", "Vaccines"],
                ["J07A", "Bacterial vaccines"],
                ["J07AC", "Anthrax vaccines"],
                ["J07AD", "Brucellosis vaccines"],
                ["J07AE", "Cholera vaccines"],
                ["J07AF", "Diphtheria vaccines"],
                ["J07AG", "Hemophilus influenzae b vaccines"],
                ["J07AH", "Meningococcal vaccines"],
                ["J07AJ", "Pertussis vaccines"],
                ["J07AK", "Plague vaccines"],
                ["J07AL", "Pneumococcal vaccines"],
                ["J07AM", "Tetanus vaccines"],
                ["J07AN", "Tuberculosis vaccines"],
                ["J07AP", "Typhoid vaccines"],
                ["J07AR", "Typhus (exanthematicus) vaccines"],
                ["J07AX", "Other bacterial vaccines"],
                ["J07B", "Viral vaccines"],
                ["J07BA", "Encephalitis vaccines"],
                ["J07BB", "Influenza vaccines"],
                ["J07BC", "Hepatitis vaccines"],
                ["J07BD", "Measles vaccines"],
                ["J07BE", "Mumps vaccines"],
                ["J07BF", "Poliomyelitis vaccines"],
                ["J07BG", "Rabies vaccines"],
                ["J07BH", "Rota virus diarrhea vaccines"],
                ["J07BJ", "Rubella vaccines"],
                ["J07BK", "Varicella zoster vaccines"],
                ["J07BL", "Yellow fever vaccines"],
                ["J07BM", "Papillomavirus vaccines"],
                ["J07BX", "Other viral vaccines"],
                ["J07C", "Bacterial and viral vaccines, combined"],
                ["J07CA", "Bacterial and viral vaccines, combined"],
                ["J07X", "Other vaccines"],
                ["L", "Antineoplastic agents and immunomodulating agents"],
                ["L01", "Antineoplastic agents"],
                ["L01A", "Alkylating agents"],
                ["L01AA", "Nitrogen mustard analogues"],
                ["L01AB", "Alkyl sulfonates"],
                ["L01AC", "Ethylene imines"],
                ["L01AD", "Nitrosoureas"],
                ["L01AG", "Epoxides"],
                ["L01AX", "Other alkylating agents"],
                ["L01B", "Antimetabolites"],
                ["L01BA", "Folic acid analogues"],
                ["L01BB", "Purine analogues"],
                ["L01BC", "Pyrimidine analogues"],
                ["L01C", "Plant alkaloids and other natural products"],
                ["L01CA", "Vinca alkaloids and analogues"],
                ["L01CB", "Podophyllotoxin derivatives"],
                ["L01CC", "Colchicine derivatives"],
                ["L01CD", "Taxanes"],
                ["L01CX", "Other plant alkaloids and natural products"],
                ["L01D", "Cytotoxic antibiotics and related substances"],
                ["L01DA", "Actinomycines"],
                ["L01DB", "Anthracyclines and related substances"],
                ["L01DC", "Other cytotoxic antibiotics"],
                ["L01X", "Other antineoplastic agents"],
                ["L01XA", "Platinum compounds"],
                ["L01XB", "Methylhydrazines"],
                ["L01XC", "Monoclonal antibodies"],
                ["L01XD", "Sensitizers used in photodynamic/radiation therapy"],
                ["L01XE", "Protein kinase inhibitors"],
                ["L01XX", "Other antineoplastic agents"],
                ["L01XY", "Combinations of antineoplastic agents"],
                ["L02", "Endocrine therapy"],
                ["L02A", "Hormones and related agents"],
                ["L02AA", "Estrogens"],
                ["L02AB", "Progestogens"],
                ["L02AE", "Gonadotropin releasing hormone analogues"],
                ["L02AX", "Other hormones"],
                ["L02B", "Hormone antagonists and related agents"],
                ["L02BA", "Anti-estrogens"],
                ["L02BB", "Anti-androgens"],
                ["L02BG", "Aromatase inhibitors"],
                ["L02BX", "Other hormone antagonists and related agents"],
                ["L03", "Immunostimulants"],
                ["L03A", "Immunostimulants"],
                ["L03AA", "Colony stimulating factors"],
                ["L03AB", "Interferons"],
                ["L03AC", "Interleukins"],
                ["L03AX", "Other immunostimulants"],
                ["L04", "Immunosuppressants"],
                ["L04A", "Immunosuppressants"],
                ["L04AA", "Selective immunosuppressants"],
                ["L04AB", "Tumor necrosis factor alpha (TNF-Alpha) inhibitors"],
                ["L04AC", "Interleukin inhibitors"],
                ["L04AD", "Calcineurin inhibitors"],
                ["L04AX", "Other immunosuppressants"],
                ["M", "Musculo-skeletal system"],
                ["M01", "Antiinflammatory and antirheumatic products"],
                ["M01A", "Antiinflammatory and antirheumatic products, non-steroids"],
                ["M01AA", "Butylpyrazolidines"],
                ["M01AB", "Acetic acid derivatives and related substances"],
                ["M01AC", "Oxicams"],
                ["M01AE", "Propionic acid derivatives"],
                ["M01AG", "Fenamates"],
                ["M01AH", "Coxibs"],
                ["M01AX", "Other antiinflammatory and antirheumatic agents, non-steroids"],
                ["M01B", "Antiinflammatory/antirheumatic agents in combination"],
                ["M01BA", "Antiinflammatory/antirheumatic agents in combination with corticosteroids"],
                ["M01BX", "Other antiinflammatory/antirheumatic agents in combination with other drugs"],
                ["M01C", "Specific antirheumatic agents"],
                ["M01CA", "Quinolines"],
                ["M01CB", "Gold preparations"],
                ["M01CC", "Penicillamine and similar agents"],
                ["M01CX", "Other specific antirheumatic agents"],
                ["M02", "Topical products for joint and muscular pain"],
                ["M02A", "Topical products for joint and muscular pain"],
                ["M02AA", "Antiinflammatory preparations, non-steroids for topical use"],
                ["M02AB", "Capsaicin and similar agents"],
                ["M02AC", "Preparations with salicylic acid derivatives"],
                ["M02AX", "Other topical products for joint and muscular pain"],
                ["M03", "Muscle relaxants"],
                ["M03A", "Muscle relaxants, peripherally acting agents"],
                ["M03AA", "Curare alkaloids"],
                ["M03AB", "Choline derivatives"],
                ["M03AC", "Other quaternary ammonium compounds"],
                ["M03AX", "Other muscle relaxants, peripherally acting agents"],
                ["M03B", "Muscle relaxants, centrally acting agents"],
                ["M03BA", "Carbamic acid esters"],
                ["M03BB", "Oxazol, thiazine, and triazine derivatives"],
                ["M03BC", "Ethers, chemically close to antihistamines"],
                ["M03BX", "Other centrally acting agents"],
                ["M03C", "Muscle relaxants, directly acting agents"],
                ["M03CA", "Dantrolene and derivatives"],
                ["M04", "Antigout preparations"],
                ["M04A", "Antigout preparations"],
                ["M04AA", "Preparations inhibiting uric acid production"],
                ["M04AB", "Preparations increasing uric acid excretion"],
                ["M04AC", "Preparations with no effect on uric acid metabolism"],
                ["M04AX", "Other antigout preparations"],
                ["M05", "Drugs for treatment of bone diseases"],
                ["M05B", "Drugs affecting bone structure and mineralization"],
                ["M05BA", "Bisphosphonates"],
                ["M05BB", "Bisphosphonates, combinations"],
                ["M05BC", "Bone morphogenetic proteins"],
                ["M05BX", "Other drugs affecting bone structure and mineralization"],
                ["M09", "Other drugs for disorders of the musculoskeletal system"],
                ["M09A", "Other drugs for disorders of the musculoskeletal system"],
                ["M09AA", "Quinine and derivatives"],
                ["M09AB", "Enzymes"],
                ["M09AX", "Other drugs for disorders of the musculo-skeletal system"],
                ["N", "Nervous system"],
                ["N01", "Anesthetics"],
                ["N01A", "Anesthetics, general"],
                ["N01AA", "Ethers"],
                ["N01AB", "Halogenated hydrocarbons"],
                ["N01AF", "Barbiturates, plain"],
                ["N01AG", "Barbiturates in combination with other drugs"],
                ["N01AH", "Opioid anesthetics"],
                ["N01AX", "Other general anesthetics"],
                ["N01B", "Anesthetics, local"],
                ["N01BA", "Esters of aminobenzoic acid"],
                ["N01BB", "Amides"],
                ["N01BC", "Esters of benzoic acid"],
                ["N01BX", "Other local anesthetics"],
                ["N02", "Analgesics"],
                ["N02A", "Opioids"],
                ["N02AA", "Natural opium alkaloids"],
                ["N02AB", "Phenylpiperidine derivatives"],
                ["N02AC", "Diphenylpropylamine derivatives"],
                ["N02AD", "Benzomorphan derivatives"],
                ["N02AE", "Oripavine derivatives"],
                ["N02AF", "Morphinan derivatives"],
                ["N02AG", "Opioids in combination with antispasmodics"],
                ["N02AX", "Other opioids"],
                ["N02B", "Other analgesics and antipyretics"],
                ["N02BA", "Salicylic acid and derivatives"],
                ["N02BB", "Pyrazolones"],
                ["N02BE", "Anilides"],
                ["N02BG", "Other analgesics and antipyretics"],
                ["N02C", "Antimigraine preparations"],
                ["N02CA", "Ergot alkaloids"],
                ["N02CB", "Corticosteroid derivatives"],
                ["N02CC", "Selective serotonin (5HT1) agonists"],
                ["N02CX", "Other antimigraine preparations"],
                ["N03", "Antiepileptics"],
                ["N03A", "Antiepileptics"],
                ["N03AA", "Barbiturates and derivatives"],
                ["N03AB", "Hydantoin derivatives"],
                ["N03AC", "Oxazolidine derivatives"],
                ["N03AD", "Succinimide derivatives"],
                ["N03AE", "Benzodiazepine derivatives"],
                ["N03AF", "Carboxamide derivatives"],
                ["N03AG", "Fatty acid derivatives"],
                ["N03AX", "Other antiepileptics"],
                ["N04", "Anti-parkinson drugs"],
                ["N04A", "Anticholinergic agents"],
                ["N04AA", "Tertiary amines"],
                ["N04AB", "Ethers chemically close to antihistamines"],
                ["N04AC", "Ethers of tropine or tropine derivatives"],
                ["N04B", "Dopaminergic agents"],
                ["N04BA", "Dopa and dopa derivatives"],
                ["N04BB", "Adamantane derivatives"],
                ["N04BC", "Dopamine agonists"],
                ["N04BD", "Monoamine oxidase B inhibitors"],
                ["N04BX", "Other dopaminergic agents"],
                ["N05", "Psycholeptics"],
                ["N05A", "Antipsychotics"],
                ["N05AA", "Phenothiazines with aliphatic side-chain"],
                ["N05AB", "Phenothiazines with piperazine structure"],
                ["N05AC", "Phenothiazines with piperidine structure"],
                ["N05AD", "Butyrophenone derivatives"],
                ["N05AE", "Indole derivatives"],
                ["N05AF", "Thioxanthene derivatives"],
                ["N05AG", "Diphenylbutylpiperidine derivatives"],
                ["N05AH", "Diazepines, oxazepines, thiazepines and oxepines"],
                ["N05AK", "Other nervous system drugs"],	# Changed in 2008 from N05AK to N07XX
                ["N05AL", "Benzamides"],
                ["N05AN", "Lithium"],
                ["N05AX", "Other antipsychotics"],
                ["N05B", "Anxiolytics"],
                ["N05BA", "Benzodiazepine derivatives"],
                ["N05BB", "Diphenylmethane derivatives"],
                ["N05BC", "Carbamates"],
                ["N05BD", "Dibenzo-bicyclo-octadiene derivatives"],
                ["N05BE", "Azaspirodecanedione derivatives"],
                ["N05BX", "Other anxiolytics"],
                ["N05C", "Hypnotics and sedatives"],
                ["N05CA", "Barbiturates, plain"],
                ["N05CB", "Barbiturates, combinations"],
                ["N05CC", "Aldehydes and derivatives"],
                ["N05CD", "Benzodiazepine derivatives"],
                ["N05CE", "Piperidinedione derivatives"],
                ["N05CF", "Benzodiazepine related drugs"],
                ["N05CH", "Melatonin receptor agonists"],
                ["N05CM", "Other hypnotics and sedatives"],
                ["N05CX", "Hypnotics and sedatives in combination, excluding barbiturates"],
                ["N06", "Psychoanaleptics"],
                ["N06A", "Antidepressants"],
                ["N06AA", "Non-selective monoamine reuptake inhibitors"],
                ["N06AB", "Selective serotonin reuptake inhibitors"],
                ["N06AF", "Monoamine oxidase inhibitors, non-selective"],
                ["N06AG", "Monoamine oxidase A inhibitors"],
                ["N06AX", "Other antidepressants"],
                ["N06B", "Psychostimulants, agents used for ADHD and nootropics"],
                ["N06BA", "Centrally acting sympathomimetics"],
                ["N06BC", "Xanthine derivatives"],
                ["N06BX", "Other psychostimulants and nootropics"],
                ["N06C", "Psycholeptics and psychoanaleptics in combination"],
                ["N06CA", "Antidepressants in combination with psycholeptics"],
                ["N06CB", "Psychostimulants in combination with psycholeptics"],
                ["N06D", "Anti-dementia drugs"],
                ["N06DA", "Anticholinesterases"],
                ["N06DX", "Other anti-dementia drugs"],
                ["N07", "Other nervous system drugs"],
                ["N07A", "Parasympathomimetics"],
                ["N07AA", "Anticholinesterases"],
                ["N07AB", "Choline esters"],
                ["N07AX", "Other parasympathomimetics"],
                ["N07B", "Drugs used in addictive disorders"],
                ["N07BA", "Drugs used in nicotine dependence"],
                ["N07BB", "Drugs used in alcohol dependence"],
                ["N07BC", "Drugs used in opioid dependence"],
                ["N07C", "Antivertigo preparations"],
                ["N07CA", "Antivertigo preparations"],
                ["N07X", "Other nervous system drugs"],
                ["N07XA", "Gangliosides and ganglioside derivatives"],
                ["N07XX", "Other nervous system drugs"],
                ["P", "Antiparasitic products, insecticides and repellents"],
                ["P01", "Antiprotozoals"],
                ["P01A", "Agents against amoebiasis and other protozoal diseases"],
                ["P01AA", "Hydroxyquinoline derivatives"],
                ["P01AB", "Nitroimidazole derivatives"],
                ["P01AC", "Dichloroacetamide derivatives"],
                ["P01AR", "Arsenic compounds"],
                ["P01AX", "Other agents against amoebiasis and other protozoal diseases"],
                ["P01B", "Antimalarials"],
                ["P01BA", "Aminoquinolines"],
                ["P01BB", "Biguanides"],
                ["P01BC", "Methanolquinolines"],
                ["P01BD", "Diaminopyrimidines"],
                ["P01BE", "Artemisinin and derivatives, plain"],
                ["P01BF", "Artemisinin and derivatives, combinations"],
                ["P01BX", "Other antimalarials"],
                ["P01C", "Agents against leishmaniasis and trypanosomiasis"],
                ["P01CA", "Nitroimidazole derivatives"],
                ["P01CB", "Antimony compounds"],
                ["P01CC", "Nitrofuran derivatives"],
                ["P01CD", "Arsenic compounds"],
                ["P01CX", "Other agents against leishmaniasis and trypanosomiasis"],
                ["P02", "Anthelmintics"],
                ["P02B", "Antitrematodals"],
                ["P02BA", "Quinoline derivatives and related substances"],
                ["P02BB", "Organophosphorous compounds"],
                ["P02BX", "Other antitrematodal agents"],
                ["P02C", "Antinematodal agents"],
                ["P02CA", "Benzimidazole derivatives"],
                ["P02CB", "Piperazine and derivatives"],
                ["P02CC", "Tetrahydropyrimidine derivatives"],
                ["P02CE", "Imidazothiazole derivatives"],
                ["P02CF", "Avermectines"],
                ["P02CX", "Other antinematodals"],
                ["P02D", "Anticestodals"],
                ["P02DA", "Salicylic acid derivatives"],
                ["P02DX", "Other anticestodals"],
                ["P03", "Ectoparasiticides, including scabicides, insecticides and repellents"],
                ["P03A", "Ectoparasiticides, including scabicides"],
                ["P03AA", "Sulfur containing products"],
                ["P03AB", "Chlorine containing products"],
                ["P03AC", "Pyrethrines, including synthetic compounds"],
                ["P03AX", "Other ectoparasiticides, including scabicides"],
                ["P03B", "Insecticides and repellents"],
                ["P03BA", "Pyrethrines"],
                ["P03BX", "Other insecticides and repellents"],
                ["R", "Respiratory system"],
                ["R01", "Nasal preparations"],
                ["R01A", "Decongestants and other nasal preparations for topical use"],
                ["R01AA", "Sympathomimetics, plain"],
                ["R01AB", "Sympathomimetics, combinations excluding corticosteroids"],
                ["R01AC", "Antiallergic agents, excluding corticosteroids"],
                ["R01AD", "Corticosteroids"],
                ["R01AX", "Other nasal preparations"],
                ["R01B", "Nasal decongestants for systemic use"],
                ["R01BA", "Sympathomimetics"],
                ["R02", "Throat preparations"],
                ["R02A", "Throat preparations"],
                ["R02AA", "Antiseptics"],
                ["R02AB", "Antibiotics"],
                ["R02AD", "Anesthetics, local"],
                ["R02AX", "Other throat preparations"],
                ["R03", "Drugs for obstructive airway diseases"],
                ["R03A", "Adrenergics, inhalants"],
                ["R03AA", "Alpha- and beta-adrenoreceptor agonists"],
                ["R03AB", "Non-selective beta-adrenoreceptor agonists"],
                ["R03AC", "Selective beta-2-adrenoreceptor agonists"],
                ["R03AH", "Combinations of adrenergics"],
                ["R03AK", "Adrenergics in combination with corticosteroids or other drugs, excluding"],
                ["R03AL", "Adrenergics in combination with anticholinergics"],
                ["R03B", "Other drugs for obstructive airway diseases, inhalants"],
                ["R03BA", "Glucocorticoids"],
                ["R03BB", "Anticholinergics"],
                ["R03BC", "Antiallergic agents, excluding corticosteroids"],
                ["R03BX", "Other drugs for obstructive airway diseases, inhalants"],
                ["R03C", "Adrenergics for systemic use"],
                ["R03CA", "Alpha- and beta-adrenoreceptor agonists"],
                ["R03CB", "Non-selective beta-adrenoreceptor agonists"],
                ["R03CC", "Selective beta-2-adrenoreceptor agonists"],
                ["R03CK", "Adrenergics and other drugs for obstructive airway diseases"],
                ["R03D", "Other systemic drugs for obstructive airway"],
                ["R03DA", "Xanthines"],
                ["R03DB", "Xanthines and adrenergics"],
                ["R03DC", "Leukotriene receptor antagonists"],
                ["R03DX", "Other systemic drugs for obstructive airway diseases"],
                ["R05", "Cough and cold preparations"],
                ["R05C", "Expectorants, excluding combinations with cough suppressants"],
                ["R05CA", "Expectorants"],
                ["R05CB", "Mucolytics"],
                ["R05D", "Cough suppressants, excluding combinations with expectorants"],
                ["R05DA", "Opium alkaloids and derivatives"],
                ["R05DB", "Other cough suppressants"],
                ["R05F", "Cough suppressants and expectorants, combinations"],
                ["R05FA", "Opium derivatives and expectorants"],
                ["R05FB", "Other cough suppressants and expectorants"],
                ["R05X", "Other cold preparations"],
                ["R06", "Antihistamines for systemic use"],
                ["R06A", "Antihistamines for systemic use"],
                ["R06AA", "Aminoalkyl ethers"],
                ["R06AB", "Substituted alkylamines"],
                ["R06AC", "Substituted ethylene diamines"],
                ["R06AD", "Phenothiazine derivatives"],
                ["R06AE", "Piperazine derivatives"],
                ["R06AK", "Combinations of antihistamines"],
                ["R06AX", "Other antihistamines for systemic use"],
                ["R07", "Other respiratory system products"],
                ["R07A", "Other respiratory system products"],
                ["R07AA", "Lung surfactants"],
                ["R07AB", "Respiratory stimulants"],
                ["R07AX", "Other respiratory system products"],
                ["S", "Sensory organs"],
                ["S01", "Ophthalmologicals"],
                ["S01A", "Antiinfectives"],
                ["S01AA", "Antibiotics"],
                ["S01AB", "Sulfonamides"],
                ["S01AD", "Antivirals"],
                ["S01AE", "Fluoroquinolones"],
                ["S01AX", "Other antiinfectives"],
                ["S01B", "Antiinflammatory agents"],
                ["S01BA", "Corticosteroids, plain"],
                ["S01BB", "Corticosteroids and mydriatics in combination"],
                ["S01BC", "Antiinflammatory agents, non-steroids"],
                ["S01C", "Antiinflammatory agents and antiinfectives in combination"],
                ["S01CA", "Corticosteroids and antiinfectives in combination"],
                ["S01CB", "Corticosteroids/antiinfectives/mydriatics in combination"],
                ["S01CC", "Antiinflammatory agents, non-steroids and antiinfectives in"],
                ["S01E", "Antiglaucoma preparations and miotics"],
                ["S01EA", "Sympathomimetics in glaucoma therapy"],
                ["S01EB", "Parasympathomimetics"],
                ["S01EC", "Carbonic anhydrase inhibitors"],
                ["S01ED", "Beta blocking agents"],
                ["S01EE", "Prostaglandin analogues"],
                ["S01EX", "Other antiglaucoma preparations"],
                ["S01F", "Mydriatics and cycloplegics"],
                ["S01FA", "Anticholinergics"],
                ["S01FB", "Sympathomimetics excluding antiglaucoma preparations"],
                ["S01G", "Decongestants and antiallergics"],
                ["S01GA", "Sympathomimetics used as decongestants"],
                ["S01GX", "Other antiallergics"],
                ["S01H", "Local anesthetics"],
                ["S01HA", "Local anesthetics"],
                ["S01J", "Diagnostic agents"],
                ["S01JA", "Colouring agents"],
                ["S01JX", "Other ophthalmological diagnostic agents"],
                ["S01K", "Surgical aids"],
                ["S01KA", "Viscoelastic substances"],
                ["S01KX", "Other surgical aids"],
                ["S01L", "Ocular vascular disorder agents"],
                ["S01LA", "Antineovascularisation agents"],
                ["S01X", "Other ophthalmologicals"],
                ["S01XA", "Other ophthalmologicals"],
                ["S02", "Otologicals"],
                ["S02A", "Antiinfectives"],
                ["S02AA", "Antiinfectives"],
                ["S02B", "Corticosteroids"],
                ["S02BA", "Corticosteroids"],
                ["S02C", "Corticosteroids and antiinfectives in combination"],
                ["S02CA", "Corticosteroids and antiinfectives in combination"],
                ["S02D", "Other otologicals"],
                ["S02DA", "Analgesics and anesthetics"],
                ["S02DC", "Indifferent preparations"],
                ["S03", "Ophthalmological and otological preparations"],
                ["S03A", "Antiinfectives"],
                ["S03AA", "Antiinfectives"],
                ["S03B", "Corticosteroids"],
                ["S03BA", "Corticosteroids"],
                ["S03C", "Corticosteroids and antiinfectives in combination"],
                ["S03CA", "Corticosteroids and antiinfectives in combination"],
                ["S03D", "Other ophthalmological and otological preparations"],
                ["V", "Various"],
                ["V01", "Allergens"],
                ["V01A", "Allergens"],
                ["V01AA", "Allergen extracts"],
                ["V03", "All other therapeutic products"],
                ["V03A", "All other therapeutic products"],
                ["V03AB", "Antidotes"],
                ["V03AC", "Iron chelating agents"],
                ["V03AE", "Drugs for treatment of hyperkalemia and hyperphosphatemia"],
                ["V03AF", "Detoxifying agents for antineoplastic treatment"],
                ["V03AG", "Drugs for treatment of hypercalcemia"],
                ["V03AH", "Drugs for treatment of hypoglycemia"],
                ["V03AK", "Tissue adhesives"],
                ["V03AM", "Drugs for embolisation"],
                ["V03AN", "Medical gases"],
                ["V03AX", "Other therapeutic products"],
                ["V03AZ", "Nerve depressants"],
                ["V04", "Diagnostic agents"],
                ["V04B", "Urine tests"],
                ["V04C", "Other diagnostic agents"],
                ["V04CA", "Tests for diabetes"],
                ["V04CB", "Tests for fat absorption"],
                ["V04CC", "Tests for bile duct patency"],
                ["V04CD", "Tests for pituitary function"],
                ["V04CE", "Tests for liver functional capacity"],
                ["V04CF", "Tuberculosis diagnostics"],
                ["V04CG", "Tests for gastric secretion"],
                ["V04CH", "Tests for renal function and ureteral injuries"],
                ["V04CJ", "Tests for thyreoidea function"],
                ["V04CK", "Tests for pancreatic function"],
                ["V04CL", "Tests for allergic diseases"],
                ["V04CM", "Tests for fertility disturbances"],
                ["V04CX", "Other diagnostic agents"],
                ["V06", "General nutrients"],
                ["V06A", "Diet formulations for treatment of obesity"],
                ["V06AA", "Low-energy diets"],
                ["V06B", "Protein supplements"],
                ["V06C", "Infant formulas"],
                ["V06CA", "Nutrients without phenylalanine"],
                ["V06D", "Other nutrients"],
                ["V06DA", "Carbohydrates/proteins/minerals/vitamins, combinations"],
                ["V06DB", "Fat/carbohydrates/proteins/minerals/vitamins, combinations"],
                ["V06DC", "Carbohydrates"],
                ["V06DD", "Amino acids, including combinations with polypeptides"],
                ["V06DE", "Amino acids/carbohydrates/minerals/vitamins, combinations"],
                ["V06DF", "Milk substitutes"],
                ["V06DX", "Other combinations of nutrients"],
                ["V07", "All other non-therapeutic products"],
                ["V07A", "All other non-therapeutic products"],
                ["V07AA", "Plasters"],
                ["V07AB", "Solvents and diluting agents, including irrigating solutions"],
                ["V07AC", "Blood transfusion, auxiliary products"],
                ["V07AD", "Blood tests, auxiliary products"],
                ["V07AN", "Incontinence equipment"],
                ["V07AR", "Sensitivity tests, discs and tablets"],
                ["V07AS", "Stomi equipment"],
                ["V07AT", "Cosmetics"],
                ["V07AV", "Technical disinfectants"],
                ["V07AX", "Washing agents etc."],
                ["V07AY", "Other non-therapeutic auxiliary products"],
                ["V07AZ", "Chemicals and reagents for analysis"],
                ["V08", "Contrast media"],
                ["V08A", "X-ray contrast media, iodinated"],
                ["V08AA", "Watersoluble, nephrotropic, high osmolar X-ray contrast media"],
                ["V08AB", "Watersoluble, nephrotropic, low osmolar X-ray contrast media"],
                ["V08AC", "Watersoluble, hepatotropic X-ray contrast media"],
                ["V08AD", "Non-watersoluble X-ray contrast media"],
                ["V08B", "X-ray contrast media, non-iodinated"],
                ["V08BA", "Barium sulfate containing X-ray contrast media"],
                ["V08C", "Magnetic resonance imaging contrast media"],
                ["V08CA", "Paramagnetic contrast media"],
                ["V08CB", "Superparamagnetic contrast media"],
                ["V08CX", "Other magnetic resonance imaging contrast media"],
                ["V08D", "Ultrasound contrast media"],
                ["V08DA", "Ultrasound contrast media"],
                ["V09", "Diagnostic radiopharmaceuticals"],
                ["V09A", "Central nervous system"],
                ["V09AA", "Technetium (99m-Tc) compounds"],
                ["V09AB", "Iodine (123I) compounds"],
                ["V09AX", "Other central nervous system diagnostic radiopharmaceuticals"],
                ["V09B", "Skeleton"],
                ["V09BA", "Technetium (99m-Tc) compounds"],
                ["V09C", "Renal system"],
                ["V09CA", "Technetium (99m-Tc) compounds"],
                ["V09CX", "Other renal system diagnostic radiopharmaceuticals"],
                ["V09D", "Hepatic and reticulo endothelial system"],
                ["V09DA", "Technetium (99m-Tc) compounds"],
                ["V09E", "Respiratory system"],
                ["V10", "Therapeutic radiopharmaceuticals"],
                ["V20", "Surgical dressings"]
            ]
            
            for entry in atc_list:
                if entry[0] == code:
                    output = entry[1]
                    match = True
                    break

            if match == False:
                output = ""

            return output

    def extract_schedule():
        """"""
        schedule = html.find_all('tr', class_="idblTable")[11].find_all('td')[1].string.strip()

    def extract_coverage():
        """"""
        coverage = html.find_all('tr', class_="idblTable")[12].find_all('td')[1].string.strip()

        coverage = coverage.title()

    def extract_clients():
        """"""
        clients = html.find_all('tr', class_="idblTable")[13].find_all('td')[1].get_text().strip()

        # Clients
        client_list = ["(Group 1)", "(Group 66)", "(Group 66A", 
                       "Income Support", "(AISH)", "(Group 19824", 
                       "(Group 20400", "(Group 20403", "(Group 20514", 
                       "(Group 22128", "(Group 23609"]
        clients = []

        for name in client_list:
            if name in clients_temp:
                clients.append(1)
            else:
                clients.append(0)

    def extract_coverage_criteria():
        """"""
        coverage_criteria = html.find_all('tr', class_="idblTable")[14].find_all('td')[1].get_text()
        
        if "Click" in coverage_criteria:
            if "coverage" in coverage_criteria and "program" in coverage_criteria:
                coverage_criteria_sa = html.find_all('tr', class_="idblTable")[14].find_all('td')[1].p.find_all('a')[0]['onclick']
                coverage_criteria_p = "http://www.health.alberta.ca/services/drugs-palliative-care.html"
            elif "coverage" in coverage_criteria:
                coverage_criteria_sa = html.find_all('tr', class_="idblTable")[14].find_all('td')[1].p.find_all('a')[0]['onclick']
                coverage_criteria_p = None
            elif "program" in coverage_criteria:
                coverage_criteria_sa = None
                coverage_criteria_p = "http://www.health.alberta.ca/services/drugs-palliative-care.html"
            
            coverage_criteria = 1
        else:
            coverage_criteria = 0
            coverage_criteria_sa = None
            coverage_criteria_p = None

        # Coverage Criteria, SA, P
        if coverage_criteria == 1:
            if coverage_criteria_sa != None:
                coverage_criteria_sa = "https://idbl.ab.bluecross.ca/idbl/" + re.search(r"\('(.+\d)','", coverage_criteria_sa).group(1)

    def extract_special_auth():
        """"""
        special_auth_temp = html.find_all('tr', class_="idblTable")[15].find_all('td')[1]
        
        special_auth = []
        special_auth_link = []
      
        if "N/A" in special_auth_temp.get_text():
            special_auth = ["N/A"]
            special_auth_link = ["N/A"]
        else:
            for a in special_auth_temp.find_all('a'):
                special_auth.append(a.string.strip())
                special_auth_link.append(a['onclick'])

        # Special Authorization & Links
        if "N/A" not in special_auth[0]:
            for i in range(0, len(special_auth)):
                special_auth[i] = special_auth[i]
                special_auth_link[i] = "https://idbl.ab.bluecross.ca" + re.search(r"\('(.+\.pdf)','", special_auth_link[i]).group(1)
                temp_list.append([url, special_auth[i], special_auth_link[i]])
        else:
            temp_list.append([url, None, None])
        

        html = truncate_content(page)

    # Truncate extra content to improve extraction
    html = truncate_content(page)

    # Extract the DIN
    din = extract_din(html)

    # Extract the PTC
    ptc = extract_ptc(html)

    # Extract the brand name, strength, route, and dosage form
    bsrf = extract_brand_strength_route_form(html)
    brandName = bsrf.brand
    strength = bsrf.strength
    route = bsrf.route
    dosageForm = bsrf.form

    genericName = extract_generic_name(html)
    dateListed = extract_date_listed(html)
    dateDiscontinued = extract_date_discontinued(html)
    unitPrice = extract_unit_price(html)
    lca = extract_lca(html)
    unitIssue = extract_unit_issue(html)
    interchangeable = extract_interchangeable(html)
    manufacturer = extract_manufacturer(html)
    atc = extract_atc(html)
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

def collect_content(url, session, crawlDelay):
    """Takes a list of URLs and extracts drug pricing information
        args:
            url:        url to extract data from
            session:    requests session object connected to the site
            delay:      time to pause between each request

        returns:
            content:    a lost of object containing the pricing data

        raises:
            none.
    """
    
    from bs4 import BeautifulSoup
    from datetime import datetime
    import time
    import re
    
    # Apply delay before starting
    time.sleep(delay)

    try:
        page = download_page(session, url)
    except Exception as e:
        log.warn("Unable to download page content: %e"
                    % (url, e))
        page = None
        pageContent = None

    if page:
        try:
            pageContent = extract_page_content(url, page)
        except Exception as e:
            log.warn("Unable to extract %s page content: %s" 
                        % (url, e))
            pageContent = None

    return pageContent