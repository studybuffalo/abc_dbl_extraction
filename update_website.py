def update_details():
    # Connect to server
    ftp_address = config.get('ftp_sb', 'address')
    ftp_user = config.get('ftp_sb', 'user')
    ftp_password = config.get('ftp_sb', 'password')

    print("Connecting to Study Buffalo server")
    ftp = FTP(ftp_address, ftp_user, ftp_password)

    # Change to proper directory
    ftp.cwd('/public_html/studybuffalo/practicetools/albertadrugprice')

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
    phpFile = open('details.php', 'rb')

    # Upload the temp file
    print (("Uploading new 'details.php'... "), end='')
    ftp.storlines('STOR details.php', phpFile)

    phpFile.close()
    ftp.quit()

    os.remove('details.php')