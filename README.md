# Alberta Blue Cross Drug Benefit List Extraction
This is a tool I use to extract data from the Alberta Blue Cross Drug Benefit List. That data is fed into the studybuffalo.com website database to allow users to quickly determine the prices of medications in Alberta, Canada.

## Program Details
* The program was originally built using Python 2.7, but has been upgraded to 3.5
* The program was one of the first ones I built, so there is significant opportunities for refactoring and optimizing (should time ever allow)
* Program is currently built to work using an Unbuntu server and run automatically in the background using a cron job
 * To facilitate this, unipath is used to generate absolute directories based of a specified root
* To minimize the work on the Alberta Blue Cross servers, the program is intended to only run once a month and to download the minimum amount of data possible. The robots.txt is adhered to and there is a 0.25s delay with each query to avoid blacklisting.
