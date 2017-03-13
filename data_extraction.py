def extract_content(config, urlList, today, crawlDelay):
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
    """
    with open(pricePath, "w") as priceCSV,\
            open(coveragePath, "w") as coverageCSV,\
            open(specialPath, "w") as specialCSV,\
            open(ptcPath, "w") as ptcCSV,\
            open(atcPath, "w") as atcCSV,\
            open(extraPath, "w") as extraCSV,\
            open(errorPath, "w") as errorText:
        from data_extraction import extract_content
    """
    try:
        # Connect to webpage
        response = request.urlopen(url)
        html = response.read().decode('utf-8')
        
        start = html.find("columnLeftFull")
        end = html.find("A drug classification system")
        html = html[start:end]
        html = BeautifulSoup(html, 'html.parser')
        
        # Extract HTML content
        din = html.p.string
        ptc = html.find_all('tr', class_="idblTable")[0].td.div.p.get_text().strip()
        brand_name = html.find_all('tr', class_="idblTable")[1].td.div.string.strip()
        generic_name = html.find_all('tr', class_="idblTable")[2].td.div.string.strip()
        date_listed = html.find_all('tr', class_="idblTable")[3].find_all('td')[1].string.strip()
        date_discontinued = html.find_all('tr', class_="idblTable")[4].find_all('td')[1].string.strip()
        unit_price = html.find_all('tr', class_="idblTable")[5].find_all('td')[1].string.strip()
        lca = html.find_all('tr', class_="idblTable")[6].find_all('td')[1].div.get_text().strip()
        unit_issue =  html.find_all('tr', class_="idblTable")[7].find_all('td')[1].string.strip()
        interchangeable = html.find_all('tr', class_="idblTable")[8].find_all('td')[1].get_text()
        manufacturer = html.find_all('tr', class_="idblTable")[9].find_all('td')[1].a.string.strip()
        atc = html.find_all('tr', class_="idblTable")[10].find_all('td')[1].string.strip()
        schedule = html.find_all('tr', class_="idblTable")[11].find_all('td')[1].string.strip()
        coverage = html.find_all('tr', class_="idblTable")[12].find_all('td')[1].string.strip()
        clients = html.find_all('tr', class_="idblTable")[13].find_all('td')[1].get_text().strip()
        coverage_criteria = html.find_all('tr', class_="idblTable")[14].find_all('td')[1].get_text()
        special_auth_temp = html.find_all('tr', class_="idblTable")[15].find_all('td')[1]
        
        # Basic processing of content
        special_auth = []
        special_auth_link = []
        
        if "YES" in interchangeable:
            interchangeable = 1
        else:
            interchangeable = 0

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


        if "N/A" in special_auth_temp.get_text():
            special_auth = ["N/A"]
            special_auth_link = ["N/A"]
        else:
            for a in special_auth_temp.find_all('a'):
                special_auth.append(a.string.strip())
                special_auth_link.append(a['onclick'])

		# Parsing HTML content into formatted lists
        price_data = parse.price_data(url, din, brand_name,
                                      generic_name, unit_price, lca,
                                      unit_issue)

        coverage_data = parse.coverage_data(url, coverage, clients,
                                            coverage_criteria,
                                            coverage_criteria_sa,
                                            coverage_criteria_p)

        special_data = parse.special_auth_data(url, special_auth,
                                               special_auth_link)
        
        ptc_data = parse.ptc_data(url, ptc)
        
        atc_data = parse.atc_data(url, atc)
        
        extra_data = parse.extra_data(url, date_listed, 
                                      date_discontinued, manufacturer,
                                      schedule, interchangeable)
        
        # Adding parsed lists to list for database upload/saving to .txt
        price_list.append(price_data)
        coverage_list.append(coverage_data)
        ptc_list.append(ptc_data)
        atc_list.append(atc_data)
        extra_list.append(extra_data)
        
        for item in special_data:
            special_list.append(item)

		# Saving parsed lists to .txt files
        price_file.write(('"%s","%s","%s","%s","%s","%s","%s","%s",'
                          '"%s","%s","%s"\n') % 
                         (price_data[0], price_data[1], price_data[2],
                          price_data[3], price_data[4], price_data[5],
                          price_data[6], price_data[7], price_data[8],
                          price_data[9], price_data[10]))
        
        coverage_file.write(('"%s","%s","%s","%s","%s","%s","%s","%s",'
                             '"%s","%s","%s","%s","%s","%s","%s",'
                             '"%s"\n') % 
                            (coverage_data[0], coverage_data[1],
                             coverage_data[2], coverage_data[3],
                             coverage_data[4], coverage_data[5],
                             coverage_data[6], coverage_data[7],
                             coverage_data[8], coverage_data[9],
                             coverage_data[10], coverage_data[11],
                             coverage_data[12], coverage_data[13],
                             coverage_data[14], coverage_data[15]))
        
        for item in special_data:
            special_file.write('"%s","%s","%s"\n' % 
                               (item[0], item[1], item[2]))
        
        ptc_file.write(('"%s","%s","%s","%s","%s","%s","%s","%s","%s"'
                        '\n') %
                       (ptc_data[0], ptc_data[1], ptc_data[2],
                        ptc_data[3], ptc_data[4], ptc_data[5],
                        ptc_data[6], ptc_data[7], ptc_data[8]))
        
        atc_file.write(('"%s","%s","%s","%s","%s","%s","%s","%s",'
                        '"%s","%s","%s"\n') % 
                       (atc_data[0], atc_data[1], atc_data[2], 
                        atc_data[3], atc_data[4], atc_data[5], 
                        atc_data[6], atc_data[7], atc_data[8], 
                        atc_data[9], atc_data[10]))
        
        extra_file.write(('"%s","%s","%s","%s","%s","%s"\n') % 
                         (extra_data[0], extra_data[1], extra_data[2],
                          extra_data[3], extra_data[4], extra_data[5]))
        time.sleep(0.25)
    except Exception as e:
        error_file.write("Error involving %s - %s\n" % (url, e))