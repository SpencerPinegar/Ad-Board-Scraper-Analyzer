Messenger-Pigeon

    This project is a web-scraper, evaluator, and notifier for listings on KSL Cars Classifieds. It gathers all of the
new listings, grabs their value (carfax value, else kbb value, else none) compares that value to the listing price. If
that listing is yields the desired ROI and net increase a text is sent to the number to be notified. All listings are
posted into a database that can be viewed later for analysis.

Getting Started

1. You must have a mySQL database set up with 4 tables within it - I call this Database KSL_WebScraper:

        This is the database that the sql_connection will interact with

     Table 1 - Cars:

            Default is null unless otherwise specified. The following table holds all data for
            all cars that have been analyzed from the listings. It holds all the car data
            along with some other analytics that effect value.

        Column Name:        Type:       Length:     Null:       Primary:        Unique:     Misc:
        ad_identifier       int         10          No          Yes             Yes         Unsigned
        title               varchar     100         Yes         No              No          -
        mileage             mediumint   6           Yes         No              No          Unsigned
        year                smallint    4           Yes         No              No          Unsigned
        make                tinyint     3           Yes         No              No          Unsigned
        model               varchar     15          Yes         No              No          -
        trim                varchar     15          Yes         No              No          -
        body                varchar     15          Yes         No              No          -
        vin                 varchar     17          Yes         No              No          -
        title_type          tinyint     1           Yes         No              No          -
        transmission        tinyint     1           Yes         No              No          -
        exterior_color      tinyint     2           Yes         No              No          -
        interior_color      tinyint     2           Yes         No              No          -
        liters              varchar     5           Yes         No              No          -
        fuel_type           tinyint     2           Yes         No              No          -
        exterior_condition  tinyint     1           Yes         No              No          -
        interior_condition  tinyint     1           Yes         No              No          -
        drive_type          tinyint     1           Yes         No              No          -
        make_label          varchar     100         Yes         No              No          -
        cylinders           varchar     4           Yes         No              No          -
        popularity          tinyint     3           No          No              No          Unsigned, Default = 0
        longevity           tinyint     3           No          No              No          Unsigned, Default = 11
        make-reliability    tinyint     3           No          No              No          Unsigned, Default = 50
        bad_model           bit         1           No          No              No          Default = 0
        value_accuracy      tinyint     3           Yes         No              No          -
        value               mediumint   6           No          No              No          -
        price               mediumint   6           No          No              No          -
        price_diff          smallint    5           Yes         No              No          Virtual
        ROI                 float       2           Yes         No              No          Virtual


     Table 2 - Processed_Listings:

             The following table contains all listings that have been processed and their info.

        Column Name:        Type:       Length:     Null:       Primary:        Unique:     Misc:
    -------------------------------------------------------------------------------------------------
        ad_identifier       int         10          No          Yes             Yes         Unsigned
        date_posted         date                    No          No              No          -
        page_views          smallint    5           No          No              No          Unsigned
        page_favorites      smallint    4           No          No              No          Unsigned
        seller_id           bigint      15          No          No              No          Unsigned
        info                varchar     2000        No          No              No          -
        location            varchar     100         No          No              No          -



     Table 3 - Sellers:

            The following table contains all sellers that have been processed and their info.

        Column Name:        Type:       Length:     Null:       Primary:        Unique:     Misc:
    --------------------------------------------------------------------------------------------------
        seller_id           bigint      15          No          Yes             Yes         Unsigned
        name                varchar     2           No          No              No          -
        phone_number        bigint      10          Yes         No              Yes         Unsigned
        member_since        date                    No          No              No          -
        private_seller      bit         1           No          No              No          -
        cars_posted         tinyint     3           No          No              No          Unsigned, Default = 1


     Table 4 - Unprocessed_Listings:

             The following table contains all listings that have been seen but not processed.

        Column Name:        Type:       Length:     Null:       Primary:        Unique:     Misc:
    -------------------------------------------------------------------------------------------------
        ad_identifier       int         10          No          Yes             Yes         Unsigned
        attempts            tinyint     1           No          No              No          Unsigned


    Table 5 - Unprocessed_Listings:

             The following table contains all listings that have been seen but not processed.

        Column Name:        Type:       Length:     Null:       Primary:        Unique:     Misc:
    -------------------------------------------------------------------------------------------------
        Hash                varchar     32          No          Yes             Yes         -
        causing_error       varchar     1000        No          No              No          -
        why_thrown          varchar     1000        No          No              No          -
        AddedOnDate         timestamp   -           Yes         No              No          Defalt = CURRENT_TIMESTAMP
        seen                int         10          No          No              No          Default = 1

2. Set up Twilio:
    To be notified of the good deals you must have a twilio keys. This can easily be done, go to twilio's website
    and applying for a twilio api key and password. You will use this to receive mobile notifications of bad deals.
    When you have recieved your account information go to the phone object and replace the neccesary fields. Now
    you just need to enter the number you want notified of good deals in the ksl_scraper object as a parameter.


3. Create a Settings file
    The settings file is a text file created located in the same folder as the scrape function. The name must be in
    all caps. Copy the example Settings file and put all relevant information between the single quotes.

  Ex:

  ------   SETTINGS   ------
--------------------------------

 - Scraper Settings -

Range::'50'
Number_To_Notify::'8016692828'
Max_Pages::'2'
Proxy_IP::'False'


 - Connection Settings -

DB_Host::'localhost'
DB_User::'root'
DB_Password::''
DB_Name::'KSL_WebScraper'


 -- Settigs Info --

 - The Range setting determines how close a listing needs to be within your range to be pulled, stored, and read.
 - The Number_To_Notify setting is the number of the phone you would like to recieve all good deals to
 - The Max_Pages settingis the number of previously listed pages you would like to sort through before only processing new listings
 - The Proxy_IP setting determines if you want your ip to be proxied or not - this is useful to avoid getting blacklisted.
            The only issue is when this setting is on errors occur more frequently ad it is a newer feature.
 - The DB_Host setting is the host of the mySQL server you set up earlier.
 - The DB_User setting is the username of the mySQL server you set up earlier.
 - The DB_Password setting is the password of the mySQL server you set up earlier.
 - The DB_Name setting is the name of the mySQL database you set up in the mySQL server earlier.

-----------------------------------------------------------------------------------------------------------------------

Usage:

    The KSL_Scraper is meant to be run 24/7 - so Error handling is a must. You will be able to see different types of
    errors through the console. A single Shit signifies there was an unknown issue when proccessing the pulled listings.
    These are not uncommon but should occur at a rate of less than 1-10. Other issues such as the scraper being unable
    to build a certain listings car will be displayed as well.

    The Scraper can be started by running the scrape.py file from the command line.

    1. Make sure the relevant mySQL server is activated.
    2. Go to /Messenger_Pigeon --- not /Messenger_Pigeon/Messenger_Pigeon
    3. type python3 scrape.py


