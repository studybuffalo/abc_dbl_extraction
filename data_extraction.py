class PageContent(object):
    def __init__(self, din):
        self.din = din
        
def download_page(session, url):
    response = session.get(url)
    status = response.status_code

    if status == 200:
        return response.text()
    else:
        raise IOError("%s returned status code %d" % (url, status))

def extract_page_content(page):
    def truncate_content(page):
        """Extracts relevant HTML and returns a BeautifulSoup object

            This was determined with trial and error; the start and 
            end parts appear to be unique strings that reasonably
            extract the relevant HTML sections from the page.
        """
        start = page.find("columnLeftFull")
        end = page.find("A drug classification system")

        page = html[start:end]

        html = BeautifulSoup(page, 'html.parser')

        return html
        
    def extract_din(html):
        """Extracts the DIN"""
        # Get the main HTML element
        din = html.p.string

        # Remove exccess content
        din = din.replace("DIN/PIN Detail - ", "")

        return din

    def extract_ptc():
        """"""
        ptc = html.find_all('tr', class_="idblTable")[0].td.div.p.get_text().strip()

        def parse_ptc(text):
            '''Splits text into a list containing PTC codes and titles.'''
            pre_list = text.split("\n")
            post_list = []
            output = []
            number_last = False

            # Removes blank list entries
            for line in pre_list:
                line = line.strip()

            if line != "":
                post_list.append(line)

            # Properly organizes & formats list
            for line in post_list:
                search = re.search(r"\d{4,}", line)

                if search != None:
                    # Entry is a number
                    if number_last == False:
                        output.append(line)
                        number_last = True
                    else:
                        # Last entry was a number; append none for the 
                        # text field
                        output.append(None)
                        output.append(line)
                else:
                    # Entry is text - formats it properly
                    line = line.title()

                    line = re.sub(r"\b5-Ht3\b", "5-HT3", line)
                    line = re.sub(r"\bComt\b", "COMT", line)
                    line = re.sub(r"\bCox-2\b", "COX-2", line)
                    line = re.sub(r"\bDpp-4\b", "DPP-4", line)
                    line = re.sub(r"\bEent\b", "EENT", line)
                    line = re.sub(r"\bIi\b", "II", line)
                    line = re.sub(r"\bIii\b", "III", line)
                    line = re.sub(r"\bIv\b", "IV", line)
                    line = re.sub(r"\bSglt2\b", "SGLT2", line)

                    output.append(line)
                    number_last = False

            # Appends None to output for a total of 8 items
            end = 8 - len(output)

            for _ in range(end):
                output.append(None)

            return output
    
    def extract_brand_strength_route_form():
        """Extracts the brand name, strenght, route, and dosage form"""
        bsrf = html.find_all('tr', class_="idblTable")[1].td.div.string.strip()

        def split_brand_name(text):
            """Extracts brand name, strength, route, dosage form from string
            
	            Takes the brand_name_temp string and extracts the brand name,
	            string, route, and dosage from. If necessary, performs 
	            processing on entries with formatting abnormalities. Finally,
	            passes each item for further processing with the parse 
	            functions.
		
	            Args:
	            text: the brand_name_temp string
		
	            Returns:
	            Returns list with the brand_name, strength, route, and 
	            dosage form.
			
	            Raises:
	            None.
            """
            output = ["", "", "", ""]
            
            # Splits text multiple strings depending on the format used
            if re.search(r"[\w%]\s{4}\w", text) != None:
                if re.search(r"[\w%]\s{3}\w", text) != None:
                    text = text.split("   ")
                    
                    output[0] = text[0].strip()
                    output[2] = text[1].strip()
                    output[3] = text[2].strip()
                else:
                    text = text.split("    ")
                    
                    output[0] = text[0].strip()
                    output[3] = text[1].strip()
            elif re.search(r"[\w%]\s{3}\w", text) != None:
                text = text.split("   ")
                
                output[0] = text[0].strip()
                output[3] = text[1].strip()
            else:
                output[0] = text.strip()
            
            # List that identifies entries that may have abnormalities
            prelim_exception_list = [
                "0.9% SODIUM", "ACCURETIC", "ACET ", "ACTEMRA", "ADVAIR", 
                "ALDACTAZIDE", "ALYSENA", "ANDRODERM", "ANDROGEL", 
                "APO-FENTANYL", "APRI", "ARANESP", "ARIXTRA", "ASACOL", 
                "AVALIDE", "AVIANE", "AVONEX", "BETASERON", "BETNESOL", 
                "BOOST", "BOTOX", "BREVICON", "BUTRANS", "CANESTEN", 
                "CLIMARA", "CLINDAMYCIN", "COMPD", "COMPOUND", "CORTENEMA", 
                "COTAZYM", "CREON", "DEMULEN", "DEXT", "DURAGESIC", 
                "ENTOCORT", "EPREX", "EPREX", "ESME", "ESTALIS", "ESTRADOT", 
                "EURO-K", "EVRA", "EXELON", "EXTAVIA", "FEMHRT", 
                "FIORINAL-C", "FLEET ENEMA", "FONDAPARINUX", "FRAGMIN",
                "FRAXIPARINE", "FREYA", "GYNAZOLE", "HABITROL", "HUMALOG",
                "HUMULIN", "HYDROMORPHONE HP", "INNOHEP", "INVEGA SUSTENNA",
                "JAMP-K", "LACTATED", "LINESSA", "LOESTRIN", "LOVENOX", 
                "LUTERA", "MARVELON", "MINESTRIN", "MINITRAN", "MIRVALA", 
                "MORPHINE HP", "NICODERM", "NITRO-DUR", "NOVOLIN GE", 
                "OESCLIM", "ORTHO", "OVIMA", "PANCREASE", "PEPTAMEN",
                "PMS-IPRATROPIUM", "PORTIA", "RATIO-TECNAL-C", "REBIF",
                "RECLIPSEN", "RESOURCE", "SAIZEN", "SALOFALK", 
                "ESTRADIOL DERM", "SELECT", "SIMILAC", "SINEMET", 
                "SOMATULINE", "STELARA", "SUMATRIPTAN", "SYMBICORT", 
                "TENORETIC", "TESTIM", "TEVA-CEPHALEXIN", 
                "TRANSDERMAL NICOTINE", "TRANSDERM-NITRO", "TRICIRA",
                "TRI-CYCLEN", "TRINIPATCH", "TYLENOL NO.", "VIOKASE", 
                "VITAL PEPTIDE", "VIVONEX", "ZAMINE", "ZARAH", "ZENHALE"]
            
            match = False
            
            # Any text containing a prelim_exception are further accessed for
            # formatting abnormalities requiring manual correction before 
            # automatic processing
            for prelim_exception in prelim_exception_list:
                if prelim_exception in output[0]:
                    # List of entries that will be manually formatted
                    # 0 = search string, 1 = brand name, 2 = strength,
                    # 3 = route, 4 = dosage form
                    correction_list = [
                        ["0.9% SODIUM CHLORIDE", "Sodium Chloride 0.9% (NS)", "0.9%", "injection", "solution"],
                        ["3.3% DEXT/ 0.3% NACL (2/3-1/3)", "Dextrose 3.3%/Sodium Chloride 0.3% (2/3-1/3)", "3.3%/0.3%", "injection", "solution"],
                        ["3.3% DEXT/0.3% NACL/20 MEQ KCL", "Dextrose 3.3%/Sodium Chloride 0.3%/Potassium Chloride 20 mEq", "3.3%/0.3%/20 mEq", "injection", "solution"],
                        ["3.3% DEXT/0.3% NACL/40 MEQ KCL", "Dextrose 3.3%/Sodium Chloride 0.3%/Potassium Chloride 40 mEq", "3.3%/0.3%/40 mEq", "injection", "solution"],
                        ["5% DEXTROSE (D5W)", "Dextrose 5% (D5W)", "5%", "injection", "solution"],
                        ["5% DEXTROSE/ 0.15% KCL 20 MEQ", "Dextrose 5%/Sodium Chloride 0.15%/Potassium Chloride 20 mEq", "5%/0.15%/20 mEq", "injection", "solution"],				
                        ["5% DEXTROSE/ 0.3% KCL 40 MEQ", "Dextrose 5%/Sodium Chloride 0.3%/Potassium Chloride 40 mEq", "5%/0.3%/40 mEq", "injection", "solution"],				
                        ["ACCURETIC 10/12.5", "Accuretic 10/12.5", "10 mg * 12.5 mg", "oral", "tablet"],
                        ["ACCURETIC 20/12.5", "Accuretic 20/12.5", "20 mg * 12.5 mg", "oral", "tablet"],
                        ["ACCURETIC 20/25", "Accuretic 20/25", "20 mg * 25 mg", "oral", "tablet"],
                        ["ACET 120", "Acet 120", "120 mg", "rectal", "suppository"],
                        ["ACET 325", "Acet 325", "325 mg", "rectal", "suppository"],
                        ["ACET 650", "Acet 650", "650 mg", "rectal", "suppository"],
                        ["ACTEMRA (10 Ml)", "Actemra", " 200 mg/10 mL vial", "injection", "solution"],
                        ["ACTEMRA (20 Ml)", "Actemra", "400 mg/20 mL vial", "injection", "solution"],
                        ["ACTEMRA (4 Ml)", "Actemra", "80 mg /4 mL vial", "injection", "solution"],
                        ["ADVAIR 100 DISKUS", "Advair 100 Diskus", "50 mcg/dose * 100 mcg/dose", "inhalation", "metered inhalation powder"],
                        ["ADVAIR 250 DISKUS", "Advair 250 Diskus", "50 mcg/dose * 250 mcg/dose", "inhalation", "metered inhalation powder"],
                        ["ADVAIR 500 DISKUS", "Advair 500 Diskus", "50 mcg/dose * 500 mcg/dose", "inhalation", "metered inhalation powder"],
                        ["ADVAIR 125", "Advair 125", "25 mcg/dose * 125 mcg/dose", "inhalation", "metered dose aerosol"],
                        ["ADVAIR 250", "Advair 250", "25 mcg/dose * 250 mcg/dose", "inhalation", "metered dose aerosol"],
                        ["ALDACTAZIDE 25", "Aldactazide 25", "25 mg * 25 mg", "oral", "tablet"],
                        ["ALDACTAZIDE 50", "Aldactazide 50", "50 mg * 50 mg", "oral", "tablet"],
                        ["ALYSENA 21", "Alysena 21", "100 mcg * 20 mcg", "oral", "tablet"],
                        ["ALYSENA 28", "Alysena 28", "100 mcg * 20 mcg", "oral", "tablet"],
                        ["ANDRODERM (2.5 MG/DAY)", "Androderm", "12.2 mg (2.5 mg/day)", "transdermal", "patch"],
                        ["ANDRODERM (5 MG/DAY)", "Androderm", "24.3 mg (5 mg/day)", "transdrmal", "patch"],
                        ["ANDROGEL (2.5 G/ PACKET)", "Androgel", "1% (2.5 g/packet)", "topical", "gel"],
                        ["ANDROGEL (5 G/ PACKET)", "Androgel", "1% (2.5 g/packet)", "topical", "gel"],
                        ["APO-FENTANYL 25", "APO-Fentanyl 25", "25 mcg/hr", "transdermal", "patch"],
                        ["APO-FENTANYL 50", "APO-Fentanyl 50", "50 mcg/hr", "transdermal", "patch"],
                        ["APO-FENTANYL 75", "APO-Fentanyl 75", "75 mcg/hr", "transdermal", "patch"],
                        ["APO-FENTANYL 100", "APO-Fentanyl 100", "100 mcg/hr", "transdermal", "patch"],
                        ["APRI 21", "Apri 21", "0.15 mg * 0.03 mg", "oral", "tablet"],
                        ["APRI 28", "Apri 28", "0.15 mg * 0.03 mg", "oral", "tablet"],
                        ["ARANESP (0.3 ML SYRINGE) 30 MCG / SYR", "Aranesp", "30 mcg/0.3 mL syringe", "injection", "syringe"],
                        ["ARANESP (0.3 ML SYRINGE) 60 MCG / SYR", "Aranesp", "60 mcg/0.3 mL syringe", "injection", "syringe"],
                        ["ARANESP (0.3 ML SYRINGE) 150 MCG / SYR", "Aranesp", "150 mcg/0.3 mL sryinge", "injection", "syringe"],
                        ["ARANESP (0.3/ 0.4/ 0.5 ML SYR) 100 MCG / ML", "Aranesp", "30 mcg/0.3 mL syringe, 40 mcg/0.4 mL syringe, 50 mcg/0.5 mL syringe", "injection", "syringe"],
                        ["ARANESP (0.3/ 0.4/ 0.6/ 1.0 ML SYR) 500 MCG / ML", "Aranesp", "150 mcg/0.3 mL syringe, 200 mcg/0.4 mL syringe, 300 mcg/0.6 mL syringe, 500 mcg/1 mL sryinge", "injection", "syringe"],
                        ["ARANESP (0.3/ 0.4/ 0.5/ 0.65 ML SYR) 200 MCG / ML", "Aranesp", "60 mcg/0.3 mL syringe, 80 mcg/0.4 mL sryinge, 100 mcg/0.5 mL sryinge, 130 mcg/0.65 mL syringe", "injection", "syringe"],
                        ["ARANESP (0.4 ML SYRINGE) 10 MCG / SYR", "Aranesp", "10 mcg/0.4 mL sryinge", "injection", "syringe"],
                        ["ARANESP (0.4 ML SYRINGE) 40 MCG / SYR", "Aranesp", "40 mcg/0.4 mL syringe", "injection", "syringe"],
                        ["ARANESP (0.4 ML SYRINGE) 80 MCG / SYR", "Aranesp", "80 mcg/0.4 mL sryinge", "injection", "syringe"],
                        ["ARANESP (0.4 ML SYRINGE) 200 MCG / SYR", "Aranesp", "200 mcg/0.4 mL syringe", "injection", "syringe"],
                        ["ARANESP (0.5 ML SYRINGE) 20 MCG / SYR", "Aranesp", "20 mcg/0.5 mL sryinge", "injection", "syringe"],
                        ["ARANESP (0.5 ML SYRINGE) 50 MCG / SYR", "Aranesp", "50 mcg/0.5 mL syringe", "injection", "syringe"],
                        ["ARANESP (0.5 ML SYRINGE) 100 MCG / SYR", "Aranesp", "100 mcg/0.5 mL syringe", "injection", "syringe"],
                        ["ARANESP (0.6 ML SYRINGE) 300 MCG / SYR", "Aranesp", "300 mcg/0.6 mL syringe", "injection", "syringe"],
                        ["ARANESP (0.65 ML SYRINGE) 130 MCG / SYR", "Aranesp", "130 mcg/0.65 mL syringe", "injection", "syringe"],
                        ["ARANESP (1.0 ML SYR) 500 MCG / SYR", "Aranesp", "500 mcg/1 mL syringe", "injection", "syringe"],
                        ["ARIXTRA (0.5 ML SYRINGE)", "Arixtra", "2.5 mg/0.5 mL syringe", "injection", "syringe"],
                        ["ARIXTRA (0.6 ML SYRINGE)", "Arixtra", "7.5 mg/0.6 mL syringe", "injection", "syringe"],
                        ["ASACOL 800", "Asacol", "800 mg", "oral", "enteric-coated tablet"],
                        ["AVALIDE 150/12.5", "Avalide 150/12.5", " 150 mg * 12.5 mg", "oral", "tablet"],
                        ["AVALIDE 300/12.5", "Avalide 300/12.5", "300 mg * 12.5 mg", "oral", "tablet"],
                        ["AVIANE 21", "Aviane 21", "100 mcg * 20 mcg", "oral", "tablet"],
                        ["AVIANE 28", "Aviane 28", "100 mcg * 20 mcg", "oral", "tablet"],
                        ["AVONEX PS/PEN", "Avonex PS/Pen", "30 mcg (6 MIU)/0.5 mL syringe", "injection", "syringe"],
                        ["BETASERON", "Betaseron", "9.6 MIU (0.3 MG)/vial", "injection", "vial"],
                        ["BETNESOL", "Betnesol", "5 mg/100 mL enema", "rectal", "enema"],
                        ["BOOST 1.5 PLUS CALORIES", "Boost 1.5 Plus Calories", "", "oral", "liquid"],
                        ["BOTOX", "Botox", "50/100/200 units/vial", "injection", "suspension"],
                        ["BREVICON 0.5/35 (21 DAY)", "Brevicon 0.5/35 (21 Day)", "0.5 mg * 0.035 mg", "oral", "tablet"],
                        ["BREVICON 0.5/35 (28 DAY)", "Brevicon 0.5/25 (28 Day)", "0.5 mg * 0.035 mg", "oral", "tablet"],
                        ["BREVICON 1/35 (21 DAY)", "Brevicon 1/35 (21 Day)", "1 mg * 0.035 mg", "oral", "tablet"],
                        ["BREVICON 1/35 (28 DAY)", "Brevicon 1/35 (28 Day)", "1 mg * 0.035 mg", "oral", "tablet"],
                        ["BUTRANS 5", "Butrans 5", "5 mcg/hr", "transdermal", "patch"],
                        ["BUTRANS 10 10 MCG/HR", "Butrans 10", "10 mcg/hr", "transdermal", "patch"],
                        ["BUTRANS 20 20 MCG/HR", "Butrans 20", "20 mcg/hr", "transdermal", "patch"],
                        ["CANESTEN 3 2 %", "Canesten 3", "2%", "vaginal", "cream"],
                        ["CANESTEN 6 1 %", "Canesten 6", "1%", "vaginal", "cream"],
                        ["CANESTEN 1 CREAM COMBI-PAK", "Canesten 1 Cream Combi-Pak", "1% * 10%", "topical/vaginal", "cream/cream"],
                        ["CANESTEN 1 10 %", "Canesten 1", "10%", "vaginal", "cream"],
                        ["CANESTEN 1 COMFORTAB COMBI-PAK", "Canesten 1 Comfortab Combi-Pak", "500 mg * 1%", "vaginal/topical", "tablet/topical"],
                        ["CANESTEN 3 COMFORTAB COMBI-PAK", "Canesten 3 Comfortab Combi-Pak", "200 mg * 1%", "vaginal/topical", "tablet/cream"],
                        ["CLIMARA 25", "Climara 25", "25 mcg/day (2 mg/patch)", "tansdermal", "patch"],
                        ["CLIMARA 50", "Climara 50", "50 mcg/day (3.9 mg/patch)", "transdermal", "patch"],
                        ["CLIMARA 75", "Climara 75", "75 mcg/day (5.7 mg/patch)", "transdermal", "patch"],
                        ["CLIMARA 100", "Climara 100", "100 mcg/day (7.8 mg/patch)", "transdermal", "patch"],
                        ["CLINDAMYCIN (60 & 120 ML)", "Clindamycin", "150 mg/mL (60 mL & 120 mL bottle)", "injection", "vial"],
                        ["COMPD- NSAID", "Compound - NSAID/Analgesic/Muscle Relaxant (Excluding Diclofenac)", "", "topical", "cream, ointment"],
                        ["COMPD-CHLORHEX", "Compound - Chlorhexidine (Not 0.12%)", "", "oral topical", "solution"],
                        ["COMPD-NSAID", "Compound - NSAID/Analgesic/Muscle Relaxant (Excluding Diclofenac)", "", "topical", "cream, ointment"],
                        ["COMPOUND - RETINOIC ACID", "Compound - Retinoic Acid", "", "topical", "cream, ointment"],
                        ["COMPOUND HORMONES", "Compound - Hormones (Estrogen, Progesterone, Testosterone)", "", "", ""],
                        ["COMPOUND NARCOTIC", "Compound - Narcotic Mixtures", "", "injection, oral", ""],
                        ["COMPOUND- SALICYLIC", "Compound - Salicylic Acid", "", "topical", "cream, ointment"],
                        ["COMPOUND-ANTI-INFECTIVE", "Compound - Anti-Infective", "", "topical", "cream, ointment"],
                        ["COMPOUND-CORTICOSTEROIDS", "Compound - Corticosteroids", "", "topical", "cream, ointment"],
                        ["COMPOUND-DICLOFENAC", "Compound - Diclofenac", "", "topical", "cream, ointment"],
                        ["CORTENEMA", "Cortenema", "100 mg/60 mL enema", "rectal", "enema"],
                        ["COTAZYM ECS 8", "Cotazyme ECS 8", "8,000 unit * 30,000 unit * 30,000 unit", "oral", "capsule (enteric-coated pellet)"],
                        ["COTAZYM ECS 20", "Cotazyme ECS 20", "20,000 unit * 55,000 unit * 55,000 unit", "oral", "capsule (enteric-coated pellet)"],
                        ["CREON 25 MINIMICROSPHERES", "Creon 25 Minimicrospheres", "25,000 unit * 74,000 unit * 62,500 unit", "oral", "capsule (enteric-coated pellet)"],
                        ["CREON 10 MINIMICROSPHERES", "Creon 10 Minimicrospheres", "10,000 unit * 33,200 unit * 37,500 unit", "oral", "capsule (enteric-coated pellet)"],
                        ["DEMULEN 30 (21 DAY)", "Demulen 30 (21 Day)", "2 mg * 30 mcg", "oral", "tablet"],
                        ["DEMULEN 30 (28 DAY)", "Demulen 30 (28 Day)", "2 mg * 30 mcg", "oral", "tablet"],
                        ["DURAGESIC MAT 12", "Duragesic MAT 12", "12 mcg/hr", "transdermal", "patch"],
                        ["DURAGESIC MAT 25", "Duragesic MAT 25", " 25 mcg/hr", "transdermal", "patch"],
                        ["DURAGESIC MAT 50", "Duragesic MAT 50", "50 mcg/hr", "transdermal", "patch"],
                        ["DURAGESIC MAT 75", "Duragesic MAT 75", "75 mcg/hr", "transdermal", "patch"],
                        ["DURAGESIC MAT 100", "Duragesic MAT 100", "100 mcg/hr", "transdermal", "patch"],
                        ["ENTOCORT (115 ML)", "Enterocort", "2.3 mg/115 mL enema", "rectal", "enema"],
                        ["EPREX (0.5 ML SYRINGE) 1,000 UNIT / SYR", "Eprex", "1000 units/0.5 mL syringe", "injection", "syringe"],
                        ["EPREX (0.5 ML SYRINGE) 2,000 UNIT / SYR", "Eprex", "2000 units/0.5 mL syringe", "injection", "syringe"],
                        ["EPREX (0.3 ML SYRINGE) 3,000 UNIT / SYR", "Eprex", "3000 units/0.3 mL syringe", "injection", "syringe"],
                        ["EPREX (0.4 ML SYRINGE) 4,000 UNIT / SYR", "Eprex", "4000 units/0.4 mL syringe", "injection", "syringe"],
                        ["EPREX (0.5 ML SYRINGE) 5,000 UNIT / SYR", "Eprex", "5000 units/0.5 mL syringe", "injection", "syringe"],
                        ["EPREX (0.6 ML SYRINGE) 6,000 UNIT / SYR", "Eprex", "6000 units/0.6 mL syringe", "injection", "syringe"],
                        ["EPREX (0.8 ML SYRINGE) 8,000 UNIT / SYR", "Eprex", "8000 units/0.8 mL syringe", "injection", "syringe"],
                        ["EPREX (1 ML SYRINGE) 10,000 UNIT / SYR", "Eprex", "10000 units/1 mL syringe", "injection", "syringe"],
                        ["EPREX (0.5 ML SYRINGE) 20,000 UNIT / SYR", "Eprex", "20000 units/0.5 mL syringe", "injection", "syringe"],
                        ["ESME 21", "Esme 21", "100 mcg * 20 mcg", "oral", "tablet"],
                        ["ESME 28", "Esme 28", "100 mcg * 20 mcg", "oral", "tablet"],
                        ["ESTALIS (2.7*.62 MG/PTH)", "Estalis", "140 mcg/day * 50 mcg/day (2.7 mg/patch * 0.63 mg/patch)", "transdermal", "patch"],
                        ["ESTALIS (4.8*.51 MG/PTH)", "Estalis", " 50 mcg/day * 50 mcg/day (4.8 mg/patch * 0.51 mg/patch", "transdermal", "patch"],
                        ["ESTRADOT 25", "Estradot 25", "25 mcg/day (0.39 mg/patch)", "transdermal", "patch"],
                        ["ESTRADOT 37.5", "Estradot 37.5", "37.5 mcg/day (0.585 mg/patch)", "transdermal", "patch"],
                        ["ESTRADOT 50", "Estradot 50", "50 mcg/day (0.78 mg/patch)", "transdermal", "patch"],
                        ["ESTRADOT 75", "Estradot 75", "75 mcg/day (1.17 mg/patch)", "transdermal", "patch"],
                        ["ESTRADOT 100", "Estradot 100", "100 mcg/day (1.56 mg/patch)", "transdermal", "patch"],
                        ["EURO-K 20", "Euro-K 20", "20 mEq", "oral", "sustained-release tablet"],
                        ["EVRA", "Evra", "150 mcg/day * 20 mcg/day (6 mg/patch * 0.6 mg/patch)", "transdermal", "patch"],
                        ["EXELON PATCH 5", "Exelon Patch 5", "4.6 mg/day", "transdermal", "patch"],
                        ["EXTAVIA", "Extavia", "9.6 MIU (0.3 mg)/vial", "injection", "vial"],
                        ["FEMHRT 1/5", "FemHRT 1/5", "1 mg * 5 mcg", "oral", "tablet"],
                        ["FIORINAL-C 1/4", "Fiorinal-C 1/4", "50 mg * 15 mg * 330 mg * 40 mg", "oral", "capsule"],
                        ["FIORINAL-C 1/2", "Fiorinal-C 1/2", "50 mg * 30 mg * 330 mg * 40 mg", "oral", "capsule"],
                        ["FLEET ENEMA PEDIATRIC (65 ML)", "Fleet Enema Pediatric", "10.4 g/65 mL enema * 3.9 g/65 mL enema", "rectal", "enema"],
                        ["FONDAPARINUX SODIUM (0.5 ML SYRINGE)", "Fondaparinux Sodium", "2.5 mg/0.5 mL syringe", "injection", "syringe"],
                        ["FONDAPARINUX SODIUM (0.6 ML SYRINGE)", "Fondaparinux Sodium", "7.5 mg/0.6 mL syringe", "injection", "syringe"],
                        ["FRAGMIN (0.2 ML SYRINGE) 2,500 IU / SYR", "Fragmin", "2500 IU/0.2 mL syringe", "injection", "syringe"],
                        ["FRAGMIN (0.2 ML SYRINGE) 5,000 IU / SYR", "Fragmin", "5000 IU/0.2 mL syringe", "injection", "syringe"],
                        ["FRAGMIN (0.28 ML SYRINGE) 3,500 IU / SYR", "Fragmin", "3500 IU/0.28 mL syringe", "injection", "syringe"],
                        ["FRAGMIN (0.3 ML SYRINGE) 7,500 IU / SYR", "Fragmin", "7500 IU/0.3 mL syringe", "injection", "syringe"],
                        ["FRAGMIN (0.4 ML SYRINGE) 10,000 IU / SYR", "Fragmin", "10000 IU/0.4 mL syringe", "injection", "syringe"],
                        ["FRAGMIN (0.5 ML SYRINGE) 12,500 IU / SYR", "Fragmin", "12500 IU/0.5 mL syringe", "injection", "syringe"],
                        ["FRAGMIN (0.6 ML SYRINGE) 15,000 IU / SYR", "Fragmin", "15000 IU/0.6 mL syringe", "injection", "syringe"],
                        ["FRAGMIN (0.72 ML SYRINGE) 18,000 IU / SYR", "Fragmin", "18000 IU/0.72 mL syringe", "injection", "syringe"],
                        ["FRAXIPARINE (.3-1ML SYR)", "Fraxiparine", "9500 IU/mL (0.3-1 mL syringes)", "injection", "syringe"],
                        ["FRAXIPARINE FORTE (.6-1ML SYR)", "Fraxiparine Forte", "19000 IU/mL (0.6-1 mL syringes)", "injection", "syringe"],
                        ["FREYA 21", "Freya 21", "0.15 mg * 0.03 mg", "oral", "tablet"],
                        ["FREYA 28", "Freya 28", "0.15 mg * 0.03 mg", "oral", "tablet"],
                        ["GYNAZOLE 1 2 %", "Gynazole 1", "2%", "vaginal", "cream"],
                        ["HABITROL 7 MG/DAY 7 MG/DAY", "Habitrol 7 mg/day", "7 mg/day", "transdermal", "patch"],
                        ["HABITROL 14 MG/DAY 14 MG/DAY", "Habitrol 14 mg/day", "14 mg/day", "transdermal", "patch"],
                        ["HABITROL 21 MG/DAY 21 MG/DAY", "Habitrol 21 mg/day", "21 mg/day", "transdermal", "patch"],
                        ["HUMALOG MIX 25 CARTRIDGE", "Humalog Mix 25 Cartridge", "25% * 75%", "injection", "suspension"],
                        ["HUMALOG MIX 50 CARTRIDGE", "Humalog Mix 50 Cartridge", "50% * 50%", "injection", "suspension"],
                        ["HUMALOG MIX 25 KWIKPEN", "Humalog Mix 25 KwikPen", "25% * 75%", "injection", "suspension"],
                        ["HUMALOG MIX 50 KWIKPEN", "HUmalog Mix 50 KwikPen", "50% * 50%", "injection", "suspension"],
                        ["HUMULIN 30/70", "Humulin 30/70", "30 unit/mL * 70 unit/mL", "injection", "suspension"],
                        ["HUMULIN 30/70 CARTRIDGE", "Humulin 30/70 Cartridge", "30 unit/mL * 70 unit/mL", "injection", "suspension"],
                        ["HYDROMORPHONE HP 50", "Hydromorphone HP 50", "50 mg/mL", "injection", "solution"],
                        ["HYDROMORPHONE HP 20", "Hydromorphone HP 20", "20 mg/mL", "injectionz", "solution"],
                        ["INNOHEP (0.25 ML SYRINGE)", "Innohep", "2500 IU/0.25 mL syringe", "injection", "syringe"],
                        ["INNOHEP (0.35 ML SYRINGE)", "Innohep", "3500 IU/0.35 mL syringe", "injection", "syringe"],
                        ["INNOHEP (0.4 ML SYRINGE)", "Innohep", "8000 IU/0.4 mL syringe", "injection", "syringe"],
                        ["INNOHEP (0.45 ML SYRINGE)", "Innohep", "4500 IU/0.45 mL syringe", "injection", "syringe"],
                        ["INNOHEP (0.5 ML SYRINGE)", "Innohep", "10000 IU/0.5 mL syringe", "injection", "syringe"],
                        ["INNOHEP (0.6 ML SYRINGE)", "Innohep", "12000 IU/0.6 mL syringe", "injection", "syringe"],
                        ["INNOHEP (0.7 ML SYRINGE)", "Innohep", "14000 IU/0.7 mL syringe", "injection", "syringe"],
                        ["INNOHEP (0.8 ML SYRINGE)", "Innohep", "16000 IU/0.8 mL syringe", "injection", "syringe"],
                        ["INNOHEP (0.9 ML SYRINGE)", "Innohep", "18000 IU/0.9 mL syringe", "injection", "syringe"],
                        ["INVEGA SUSTENNA (0.5 ML SYR)", "Invega Sustenna", "50 mg/0.5 mL syringe", "injection", "syringe"],
                        ["INVEGA SUSTENNA (0.75 ML SYR)", "Invega Sustenna", "75 mg/0.75 mL syringe", "injection", "syringe"],
                        ["INVEGA SUSTENNA (1 ML SYR)", "Invega Sustenna", "100 mg/1 mL syringe", "injection", "syringe"],
                        ["INVEGA SUSTENNA (1.5 ML SYR)", "Invega Sustenna", "150 mg/1.5 mL syringe", "injection", "syringe"],
                        ["JAMP-K 8", "JAMP-K 8", "8 mEq", "oral", "sustained-release tablet"],
                        ["JAMP-K 20", "JAMP-K 20", "20 mEq", "oral", "suspension-release tablet"],
                        ["LACTATED RINGER'S", "Lactated Ringer's", "", "injection", "solution"],
                        ["LINESSA 21", "Linessa 21", "0.1 mg * 0.025 mg * 0.125 mg * 0.025 mg * 0.15 mg * 0.025 mg", "oral", "tablet"],
                        ["LINESSA 28", "Linessa 28", "0.1 mg * 0.025 mg * 0.125 mg * 0.025 mg * 0.15 mg * 0.025 mg", "oral", "tablet"],
                        ["LOESTRIN 1.5/30 (21 DAY)", "Loestrin 1.5/30 (21 Day)", "1.5 mg * 0.03 mg", "oral", "tablet"],
                        ["LOESTRIN 1.5/30 (28 DAY)", "Loestrin 1.5/30 (28 Day)", "1.5 mg * 0.03 mg", "oral", "tablet"],
                        ["LOVENOX (0.3 ML SYRINGE) 30 MG / SYR", "Lovenox", "30 mg/0.3 mL syringe", "injection", "syringe"],
                        ["LOVENOX (0.4 ML SYRINGE) 40 MG / SYR", "Lovenox", "40 mg/0.4 mL syringe", "injection", "syringe"],
                        ["LOVENOX (0.6 ML SYRINGE) 60 MG / SYR", "Lovenox", "60 mg/0.6 mL syringe", "injection", "syringe"],
                        ["LOVENOX (0.8 ML SYRINGE) 120 MG / SYR", "Lovenox", "120 mg/0.8 mL syringe", "injection", "syringe"],
                        ["LOVENOX (0.8 ML SYRINGE) 80 MG / SYR", "Lovenox", "80 mg/0.8 mL syringe", "injection", "syringe"],
                        ["LOVENOX (1 ML SYRINGE) 100 MG / SYR", "Lovenox", "100 mg/1 mL syringe", "injection", "syringe"],
                        ["LOVENOX HP (1 ML SYRINGE) 150 MG / SYR", "Lovenox HP", "150 mg/1 mL syringe", "injection", "syringe"],
                        ["LUTERA 21", "Lutera 21", "100 mcg * 20 mcg", "oral", "tablet"],
                        ["LUTERA 28", "Lutera 28", "100 mcg * 20 mcg", "oral", "tablet"],
                        ["MARVELON (21 DAY)", "Marvelon (21 Day)", "0.15 mg * 0.03 mg", "oral", "tablet"],
                        ["MARVELON (28 DAY)", "Marvelon (28 Day)", "0.15 mg * 0.03 mg", "oral", "tablet"],
                        ["MINESTRIN 1/20 (21 DAY)", "MinEstrin 1/20 (21 Day)", "1 mg * 20 mcg", "oral", "tablet"],
                        ["MINESTRIN 1/20 (28 DAY)", "MinEstrin 1/20 (28 Day)", "1 mg * 20 mcg", "oral", "tablet"],
                        ["MINITRAN 0.4", "Minitran 0.4", "0.4 mg/hr", "transdermal", "patch"],
                        ["MINITRAN 0.6", "Minitran 0.6", "0.6 mg/hr", "transdermal", "patch"],
                        ["MINITRAN 0.2", "Minitran 0.2", "0.2 mg/hr", "transdermal", "patch"],
                        ["MIRVALA 21", "Mirvala 21", "0.15 mg * 0.03 mg", "oral", "tablet"],
                        ["MIRVALA 28", "Mirvala 28", "0.15 mg * 0.03 mg", "oral", "tablet"],
                        ["MISCELLANEOUS INJECTABLE COMPOUND", "Compound - Miscellaneous Injectable", "", "injection", "solution"],
                        ["MISCELLANEOUS ORAL COMPOUND", "Compound - Miscellaneous Oral", "", "oral", "solution, suspension"],
                        ["MISCELLANEOUS TOPICAL COMPOUND", "Compound - Miscellaneous Topical", "", "topical", "cream, ointment"],
                        ["MORPHINE HP 50", "Morphine HP 50", "50 mg/mL", "injection", "solution"],
                        ["NICODERM 7 MG/DAY", "Nicoderm 7 mg/Day", "7 mg/day", "transdermal", "patch"],
                        ["NICODERM 14 MG/DAY", "Nicoderm 14 mg/Day", "14 mg/day", "transdermal", "patch"],
                        ["NICODERM 21 MG/DAY", "Nicoderm 21 mg/Day", "21 mg/day", "transdermal", "patch"],
                        ["NITRO-DUR 0.4", "Nitro-Dur 0.4", "0.4 mg/day", "transdermal", "patch"],
                        ["NITRO-DUR 0.2", "Nitro-Dur 0.6", "0.8 mg/day", "transdermal", "patch"],
                        ["NITRO-DUR 0.6", "Nitro-Dur 0.8", "0.6 mg/day", "transdermal", "patch"],
                        ["NITRO-DUR 0.8", "Nitro-Dur 0.8", "0.8 mg/day", "transdermal", "patch"],
                        ["NOVOLIN GE 30/70 30 UNIT", "Novolin GE 30/70", "30 unit/mL * 70 unit/mL", "injection", "suspension"],
                        ["NOVOLIN GE 40/60 CARTRIDGE", "Novolin GE 40/60 Cartridge", "40 unit / ml * 60 unit / ml", "injection", "suspension"],
                        ["NOVOLIN GE 50/50 CARTRIDGE", "Novolin GE 50/50 Cartridge", "50 unit / ml * 50 unit / ml", "injection", "suspension"],
                        ["NOVOLIN GE 30/70 CARTRIDGE", "Novolin GE 30/70 Cartridge", "30 unit / ml * 70 unit / ml", "injection", "suspension"],
                        ["OESCLIM 25", "Oesclim 25", "25 mcg/day (5 mg/patch)", "transdermal", "patch"],
                        ["OESCLIM 50", "Oesclim 50", "50 mcg/day (10 mg/patch)", "transdermal", "patch"],
                        ["ORTHO 0.5/35 (21 DAY)", "Ortho 0.5/35 (21 Day)", "0.5 mg * 0.035 mg", "oral", "tablet"],
                        ["ORTHO 0.5/35 (28 DAY)", "Ortho 0.5/35 (28 Day)", "0.5 mg * 0.035 mg", "oral", "tablet"],
                        ["ORTHO 1/35 (28 DAY)", "Ortho 1/35 (28 Day)", "1 mg * 0.035 mg", "oral", "tablet"],
                        ["ORTHO 1/35 (21 DAY)", "Ortho 1/35 (21 Day)", "1 mg * 0.035 mg", "oral", "tablet"],
                        ["ORTHO 7/7/7 (21 DAY)", "Ortho 7/7/7 (21 Day)", "0.5 mg * 0.035 mg * 0.75 mg * 0.035 mg * 1 mg * 0.035 mg", "oral", "tablet"],
                        ["ORTHO 7/7/7 (28 DAY)", "Ortho 7/7/7 (28 Day)", "0.5 mg * 0.035 mg * 0.75 mg * 0.035 mg * 1 mg * 0.035 mg", "oral", "tablet"],
                        ["OVIMA 21", "Ovima 21", "150 mcg * 30 mcg", "oral", "tablet"],
                        ["OVIMA 28", "Ovima 28", "150 mcg * 30 mcg", "oral", "tablet"],
                        ["PANCREASE MT 16", "Pancrease MT 16", "16,000 unit * 48,000 unit * 48,000 unit", "oral", "capsule (enteric-coated pellet)"],
                        ["PANCREASE MT 10", "Pancrease MT 10", "10,000 unit * 30,000 unit * 30,000 unit", "oral", "capsule (enteric-coated pellet)"],
                        ["PANCREASE MT 4", "Pancrease MT 4", "4,000 unit * 12,000 unit * 12,000 unit", "oral", "capsule (enteric-coated pellet)"],
                        ["PEPTAMEN 1.5", "Peptamen 1.5", "", "oral", "liquid"],
                        ["PEPTAMEN AF 1.2", "Peptamen AF 1.2", "", "oral", "liquid"],
                        ["PEPTAMEN JUNIOR 1.5", "Peptamen Junior 1.5", "", "oral", "liquid"],
                        ["PEPTAMEN JUNIOR ORAL ", "Peptamen Junior", "", "oral", "liquid"],
                        ["PEPTAMEN ORAL ", "Peptamen", "", "oral", "liquid"],
                        ["PEPTAMEN WITH PREBIO 1", "Peptamen with Prebio 1", "", "oral", "liquid"],
                        ["PMS-IPRATROPIUM (1ML)", "PMS-Ipratropium", "250 mg/ mL (1 mL)", "inhalation", "unit dose solution"],
                        ["PMS-IPRATROPIUM (2ML)", "PMS-Ipratropium", "250 mg/mL (2 mL)", "inhalation", "unit dose solution"],
                        ["PORTIA 21", "Portia 21", "150 mcg * 30 mcg", "oral", "tablet"],
                        ["PORTIA 28", "Portia 28", "150 mcg * 30 mcg", "oral", "tablet"],
                        ["RATIO-TECNAL-C 1/2", "RATIO-Tecnal-C 1/2", "50 mg * 30 mg * 330 mg * 40 mg", "oral", "capsule"],
                        ["RATIO-TECNAL-C 1/4", "RATIO-Tecnal-C 1/4", "50 mg * 15 mg * 330 mg * 40 mg", "oral", "capsule"],
                        ["REBIF (0.5 ML SYRINGE) 22 MCG / SYR", "Rebif", "22 mcg/0.5 mL syringe", "injection", "syringe"],
                        ["REBIF (0.5 ML SYRINGE) 44 MCG / SYR", "Rebif", "44 mcg/0.5 mL syringe", "injection", "syringe"],
                        ["REBIF (1.5 ML CARTRIDGE) 44 MCG / ML", "Rebif", "44 mcg/1.5 mL cartridge", "injection", "cartridge"],
                        ["REBIF (1.5 ML CARTRIDGE) 88 MCG / ML", "Rebif", "88 mcg/1.5 mL cartridge", "injection", "cartridge"],
                        ["RECLIPSEN (21 DAY)", "Reclipsen (21 Day)", "0.15 mg * 0.03 mg", "oral", "tablet"],
                        ["RECLIPSEN (28 DAY)", "Reclipsen (28 Day)", "0.15 mg * 0.03 mg", "oral", "tablet"],
                        ["RESOURCE 2.0 ORAL", "Resource 2.0", "", "oral", "liquid"],
                        ["RESOURCE DAIRY THICK ORAL ", "Resource Dairy Thick", "", "oral", "liquid"],
                        ["RESOURCE DIABETIC ORAL ", "Resource Diabetic Oral", "", "oral", "liquid"],
                        ["RESOURCE KID ESSENTIALS 1.5 CAL ORAL", "Resource Kids Essentials 1.5 Cal", "", "oral", "liquid"],
                        ["RESOURCE THICKENED JUICE ORAL", "Resource Thickened Juice", "", "oral", "liquid"],
                        ["RESOURCE THICKENUP CLEAR ORAL", "Resoure ThickenUp Clear", "", "powder", "instant food thickener"],
                        ["RESOURCE THICKENUP ORAL ", "Resource ThickenUp", "", "powder", "instant food thickener"],
                        ["SAIZEN (1.5 ML)", "Saizen", "8 mg/mL (1.5 mL)", "injection", "solution"],
                        ["SAIZEN (2.5 ML)", "Saizen", "8 mg/mL (2.5 mL)", "injection", "solution"],
                        ["SALOFALK (2G/60G)", "Salofalk", "2 g/60 g enema", "rectal", "enema"],
                        ["SALOFALK (4G/60G)", "Salofalk", "4 g/60 g enema", "rectal", "enema"],
                        ["SANDOZ ESTRADIOL DERM 50", "Sandoz Estradiol Derm 50", "50 mcg/day (4 mg/patch)", "transdermal", "patch"],
                        ["SANDOZ ESTRADIOL DERM 75", "Sandoz Estradiol Derm 75", "75 mcg/day (6 mg/patch)", "transdermal", "patch"],
                        ["SANDOZ ESTRADIOL DERM 100", "Sandoz Estradiol Derm 100", "100 mcg/day (8 mg/patch)", "transdermal", "patch"],
                        ["SELECT 1/35 (21 DAY)", "Select 1/35 (21 Day)", "1 mg * 0.035 mg", "oral", "tablet"],
                        ["SELECT 1/35 (28 DAY)", "Select 1/35 (28 Day)", "1 mg * 0.035 mg", "oral", "tablet"],
                        ["SIMILAC NEOSURE ORAL", "Similac NeoSure", "", "oral", "powder"],
                        ["SINEMET 250/25", "Sinemet 250/25", "250 mg * 25 mg", "oral", "tablet"],
                        ["SINEMET 100/10", "Sinemet 100/10", "100 mg * 10 mg", "oral", "tablet"],
                        ["SINEMET 100/25", "Sinemet 100/25", "100 mg * 25 mg", "oral", "tablet"],
                        ["SINEMET CR 200/50", "Sinemet CR 200/50", "200 * 50 mg", "oral", "sustained-release tablet"],
                        ["SINEMET CR 100/25", "Sinemet CR 100/25", "100 mg * 25 mg", "oral", "sustained-release tablet"],
                        ["SOMATULINE AUTOGEL (0.3 ML SYRINGE)", "Somatuline Autogel", "60 mg/0.3 mL syringe", "injection", "syringe"],
                        ["SOMATULINE AUTOGEL (0.3 ML SYRINGE)", "Somatuline Autogel", "90 mg/0.3 mL syringe", "injection", "syringe"],
                        ["SOMATULINE AUTOGEL (0.5 ML SYRINGE)", "Somatuline Autogel", "120 mg/0.5 mL syringe", "injection", "syringe"],
                        ["STELARA (0.5 ML VIAL OR SYRINGE) 45 MG", "Stelara", "45 mg/0.5 mL (vial or syringe)", "injection", "vial or syringe"],
                        ["STELARA (1.0 ML VIAL OR SYRINGE) 90 MG", "Stelara", "90 mg/1 mL (vial or syringe)", "injection", "vial or syringe"],
                        ["SUMATRIPTAN SUN (0.5 ML) 6 MG / SYR", "Sumatriptan Sun", "6 mg/0.5 mL syringe", "injection", "syringe"],
                        ["SYMBICORT 100 TURBUHALER", "Symbicort 100 Turbuhaler", "100 mcg/dose * 6 mcg/dose", "inhalation", "metered inhalation powder"],
                        ["SYMBICORT 200 TURBUHALER", "Symbicort 200 Turbuhaler", "200 mcg/dose * 6 mcg/dose", "inhalation", "metered inhalation powder"],
                        ["TENORETIC 100/25", "Tenoretic 100/25", "100 mg * 25 mg", "oral", "tablet"],
                        ["TENORETIC  50/25", "Tenoretic 50/25", "50 mg * 25 mg", "oral", "tablet"],
                        ["TESTIM 1% 1 %", "Testim 1%", "1%", "topical", "gel"],
                        ["TEVA-CEPHALEXIN 250 50 MG / ML", "Teva-Cephalexin 250", "50 mg/mL", "oral", "suspension"],
                        ["TEVA-CEPHALEXIN 125 25 MG / ML", "Teva-Cephalexin 125", "25 mg/mL", "oral", "suspension"],
                        ["TRANSDERMAL NICOTINE 14 MG/DAY", "Transdermal Nicotine 14 mg/day", "14 mg/day", "transdermal", "patch"],
                        ["TRANSDERMAL NICOTINE 7 MG/DAY", "Transdermal Nicotine 7 mg/day", "7 mg/day", "transdermal", "patch"],
                        ["TRANSDERMAL NICOTINE 21 MG/DAY", "Transdermal Nicotine 21 mg/day", "21 mg/day", "transdermal", "patch"],
                        ["TRANSDERM-NITRO 0.2", "Transderm-Nitro 0.2", "0.2 mg/hr", "transdermal", "patch"],
                        ["TRANSDERM-NITRO 0.4", "Transderm-Nitro 0.4", "0.4 mg/hr", "transdermal", "patch"],
                        ["TRANSDERM-NITRO 0.6", "Transderm-Nitro 0.6", "0.6 mg/hr", "transdermal", "patch"],
                        ["TRICIRA LO 21", "Tricira Lo 21", "0.18 mg * 0.025 mg * 0.215 mg * 0.025 mg * 0.25 mg * 0.025 mg", "oral", "tablet"],
                        ["TRICIRA LO 28", "Tricira Lo 28", "0.18 mg * 0.025 mg * 0.215 mg * 0.025 mg * 0.25 mg * 0.025 mg", "oral", "tablet"],
                        ["TRI-CYCLEN LO 21", "Tri-Cyclen Lo 21", "0.18 mg * 0.025 mg * 0.215 mg * 0.025 mg * 0.25 mg * 0.025 mg", "oral", "tablet"],
                        ["TRI-CYCLEN LO 28", "Tri-Cyclen Lo 28", "0.18 mg * 0.025 mg * 0.215 mg * 0.025 mg * 0.25 mg * 0.025 mg", "oral", "tablet"],
                        ["TRINIPATCH 0.6 0.6 MG/HR", "Trinipatch 0.6", "0.6 mg/hr", "transdermal", "patch"],
                        ["TRINIPATCH 0.4 0.4 MG/HR", "Trinipatch 0.4", "0.4 mg/hr", "transdermal", "patch"],
                        ["TRINIPATCH 0.2 0.2 MG/HR", "Trinipatch 0.2", "0.2 mg/hr", "transdermal", "patch"],
                        ["TYLENOL NO. 3", "Tylenol No. 3", "30 mg * 300 mg * 15 mg", "oral", "tablet"],
                        ["TYLENOL NO. 4", "Tylenol No. 4", "60 mg * 300 mg", "oral", "tablet"],
                        ["TYLENOL NO. 2", "Tylenol No. 2", "15 mg * 300 mg * 15 mg", "oral", "tablet"],
                        ["VIOKASE 16", "Viokase 16", "16,000 unit * 60,000 unit * 60,000 unit", "oral", "tablet"],
                        ["VITAL PEPTIDE 1.5 CAL ORAL", "Vital Peptide 1.5 Cal", "", "oral", "liquid"],
                        ["VITAL PEPTIDE 1 CAL ORAL", "Vital Peptide 1 Cal", "", "oral", "liquid"],
                        ["VIVONEX PEDIATRIC ORAL ", "Vivonex Pediatric", "", "oral", "powder"],
                        ["VIVONEX PLUS ORAL ", "Vivonex Plus", "", "oral", "powder"],
                        ["VIVONEX T.E.N. ORAL ", "Vivonex T.E.N.", "", "oral", "powder"],
                        ["ZAMINE 21", "Zamine 21", "3 mg * 0.03 mg", "oral", "tablet"],
                        ["ZAMINE 28", "Zamine 28", "3 mg * 0.03 mg", "oral", "tablet"],
                        ["ZARAH 21", "Zarah 21", "3 mg * 0.03 mg", "oral", "tablet"],
                        ["ZARAH 28", "Zarah 28", "3 mg * 0.03 mg", "oral", "tablet"],
                        ["ZENHALE 100/5", "Zenhale 100/5", "5 mcg/dose * 100 mcg/dose", "inhalation", "metered dose aerosol"],
                        ["ZENHALE 50/5", "Zenhale 50/5", "5 mcg/dose * 50 mcg/dose", "inhalation", "metered dose aerosol"],
                        ["ZENHALE 200/5", "Zenhale 200/5", "5 mcg/dose * 200 mcg/dose", "inhalation", "metered dose aerosol"]
			        ]
                    
                    for correction in correction_list:
                        if correction[0] in output[0]:
                            output[0] = correction[1]
                            output[1] = correction[2]
                            output[2] = correction[3]
                            output[3] = correction[4]
                            match = True
            
            if match == False:
                temp = split_brand_strength(output[0])
                output[0] = temp[0]
                output[1] = temp[1]
            
            output[0] = parse_brand_name(output[0])
            output[1] = parse_strength(output[1])
            output[2] = parse_route(output[2])
            output[3] = parse_dosage_form(output[3])
            
            return output

        def parse_brand_name(text):
            '''Manually corrects errors that are not fixed by .title()'''

            text = text.title()

            # Removes extra space characters
            text = re.sub(r"\s{2,}", " ", text)

            # Regex Replacements			
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
            text = text.replace("Sod.(Unpreserved)", "Sodium (Unpreserved)")

            return text

        def parse_strength(text):
            '''Manually corrects errors not fixed by .lower().'''
            text = text.lower()
            # Removes extra space characters
            text = re.sub(r"\s{2,}", " ", text)

            # Regex Replacements			text = re.sub(r"", "", text)
            text = re.sub(r"\s/\s", "/", text)
            text = re.sub(r"\s%", "%", text)

            text = re.sub(r"\benm\b", "enema", text)
            text = re.sub(r"\biu\b", "IU", text)
            text = re.sub(r"\bmeq\b", "mEq", text)
            text = re.sub(r"\bml\b", "mL", text)
            text = re.sub(r"\bpth\b", "patch", text)
            text = re.sub(r"\bsyr\b", "syringe", text)

            return text
        
        def parse_route(text):
            '''Converts route to lower case.'''
            text = text.lower()

            return text

        def parse_dosage_form(text):
            '''Converts dosage form to lower case'''

            text = text.lower()

            return text

    def extract_generic_name():
        """"""
        generic_name = html.find_all('tr', class_="idblTable")[2].td.div.string.strip()

        def parse_generic(text):
            '''Manually corrects errors that are not fixed by .lower()'''

            text = text[1:len(text) - 1]
            text = text.lower()

            # Removes extra space characters
            text = re.sub(r"\s{2,}", " ", text)
            text = re.sub(r"/\s", "/", text)

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

            return text

    def convert_date(date):
        search = re.search(r"\d{2}-\w{3}-\d{4}", text)
        
        if search != None:
            text = text.split("-")
            
            # Convert months to numerical value
            text[1] = text[1].replace("JAN", "01")
            text[1] = text[1].replace("FEB", "02")
            text[1] = text[1].replace("MAR", "03")
            text[1] = text[1].replace("APR", "04")
            text[1] = text[1].replace("MAY", "05")
            text[1] = text[1].replace("JUN", "06")
            text[1] = text[1].replace("JUL", "07")
            text[1] = text[1].replace("AUG", "08")
            text[1] = text[1].replace("SEP", "09")
            text[1] = text[1].replace("OCT", "10")
            text[1] = text[1].replace("NOV", "11")
            text[1] = text[1].replace("DEC", "12")
            
            date = "%s-%s-%s" % (text[2], text[1], text[0])
        else:
            date = None
        return date

    def extract_date_listed():
        """"""
        date_listed = html.find_all('tr', class_="idblTable")[3].find_all('td')[1].string.strip()

    def extract_date_discontinued():
        """"""
        date_discontinued = html.find_all('tr', class_="idblTable")[4].find_all('td')[1].string.strip()

    def extract_unit_price():
        """"""
        unit_price = html.find_all('tr', class_="idblTable")[5].find_all('td')[1].string.strip()

        def parse_unit_price(text):
            '''Replaces N/A with None'''

            if "N/A" in text:
                text = None

            return text

    def extract_lca():
        """"""
        lca = html.find_all('tr', class_="idblTable")[6].find_all('td')[1].div.get_text().strip()

        def parse_lca(text):
            '''Splits LCA into a number and text, as required.'''
            index = text.find(" ")
            if index == -1:
                if "N/A" in text:
                    output = [None, None]
                else:
                    output = [text, None]
            else:
                if "N/A" in text:
                    output = [None, text[index + 1:-1].strip()]
                else:
                    output = [text[0:index].strip(), text[index + 1:-1].strip()]

            return output

        lca_temp = parse_lca(lca_temp)
        lca = lca_temp[0]
        lca_text = lca_temp[1]

    def extract_unit_issue():
        """"""
        unit_issue =  html.find_all('tr', class_="idblTable")[7].find_all('td')[1].string.strip()

        # Unit of Issue
        unit_issue = unit_issue.lower()

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
    pageContent = PageContent()

    return pageContent

def collect_content(config, session, urlList, today, crawlDelay):
    """Takes a list of URLs and extracts drug pricing information
        args:
            config:     config object holding extraction details
            urlList:    a list of valid URL strings
            today:      todays date as a string (yyyy-mm-dd)
            crawlDelay: time to pause between each request

        returns:
            content:    a lost of object containing the pricing data

        raises:
            none.
    """
    
    from bs4 import BeautifulSoup
    import time
    import re

    # List to hold all the extracted content
    content = []

    # Gets folder path to save files to
    dataLocation = config.get("misc", "data_location")

    # Opens text files to save extracted data
    pricePath = dataLocation.child("%s_price.csv" % today).absolute()
    coveragePath = dataLocation.child("%s_coverage.csv" % today).absolute()
    specialPath = dataLocation.child("%s_special.csv" % today).absolute()
    ptcPath = dataLocation.child("%s_ptc.csv" % today).absolute()
    atcPath = dataLocation.child("%s_atc.csv" % today).absolute()
    extraPath = dataLocation.child("%s_extra.csv" % today).absolute()
    errorPath = dataLocation.child("%s_price.txt" % today).absolute()
    
    with open(pricePath, "w") as priceCSV,\
         open(coveragePath, "w") as coverageCSV,\
         open(specialPath, "w") as specialCSV,\
         open(ptcPath, "w") as ptcCSV,\
         open(atcPath, "w") as atcCSV,\
         open(extraPath, "w") as extraCSV,\
         open(errorPath, "w") as errorText:

        for url in urlList:
            try:
                page = download_page(session, url)
            except Exception as e:
                log.warn("Unable to download page content: %e"
                         % (url, e))
                page = None

            if page:
                try:
                    pageContent = extract_page_content(page)
                except Exception as e:
                    log.warn("Unable to extract %s page content: %s" 
                             % (url, e))
                    pageContent = None

            if pageContent:
                content.append(pageContent)
                
                # Write content to file
                write_price(pageContent, priceCSV)

            time.sleep(0.25)

    return content