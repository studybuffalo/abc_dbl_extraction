def update_details(conf, today, log):
    from ftplib import FTP

    # Connect to server
    ftp_address = conf.get("ftp_sb", "address")
    ftp_user = conf.get("ftp_sb", "user")
    ftp_password = conf.get("ftp_sb", "password")

    try:
        ftp = FTP(ftp_address, ftp_user, ftp_password)
        log.debug("Connecting to FTP server")
    except:
        log.critical("Unable to connect to FTP server")
        return None

    # Change to proper directory
    try:
        ftp.cwd("/public_html/studybuffalo/practicetools/albertadrugprice")
    except:
        log.critical("Unable to access proper sesrver directory")
        return None

    # Create the details.php file
    with open('details.php', 'w') as file:
        file.write("<?\n"
                   "\t$title = 'Alberta Drug Price Calculator';\n"
                   "\t$description = 'Calculates the cost of a list "
                   "of medications for your patient. Also identifies "
                   "any requirements for drug coverage under Alberta "
                   "Blue Cross.';\n"
                   "\t$update = '%s';" % today)

    # Access the details file to upload
    phpFile = open("details.php", "rb")

    # Upload the temp file
    try:
        ftp.storlines('STOR details.php', phpFile)
        log.debug("Successfully uploaded details.php")

        phpFile.close()
        ftp.quit()
    except:
        log.critical("Unable to upload details.php")
        return None

    os.remove("details.php")