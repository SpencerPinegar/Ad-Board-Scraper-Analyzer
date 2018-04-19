
---------------------------------------   Ad-Board-Scraper-Analyzer  ------------------------------------------------------


    This project is a web-scraper for KSL Cars ad board. It consistently runs pulling new ad listings from KSL Cars Classifieds. When it has all of the new listings it automatically processes them; evaluating the accuracy of each listings using Levenshtein string comparison, representing each listing as a car object. 
    
    Once the car object is built the program analyzes each car object to determine it's value and the risk. The following metrics are used to evaluate each car:
    - The VIN is checked against Carfax to estimate the cars individual value based on known condition 
    - The car is run through Kelly Blue Book to determine it's value based on local comparables with similar mileage
    - The car is run through the Consumer Reports database to check if the model year had a disproportional amount of         defects
    - The life expectancy of the car is scaled based on the percentage of cars of that model that drove more than 200K miles on the road.
    - The seller of the car is tracked based on phone number so purchases from unlicensed resellers can be avoided
    - The Manufacturer of each car is evaluated based on reviews from Consumer Reports
    - The Popularity of the car is ranked based on reviews from Consumer Reports.
    
    Based on these metrics a value difference, ROI, and risk can be evaluated for each vehicle. If a car meets a buyers specific ROI, value difference, and risk they will be notified via email. Here is an example of a notification.
    
    
         -----------------------------------   Example Notification   ---------------------------------------------
     
   INFO

    ___  CAR INFO  ___
    Make: TOYOTA,
    Model: Camry,
    Price: 1000,
    Value: 1980,
    Mileage: 135000,
    Title Type: CLEAN,
    Year: 1998,
    Trim: ,
    Condition: E,
    Color: SILVER

    ___  CAR ANALYSIS  ___
    Value Accuracy: 90,
    Price Dif: 980,
    ROI: 0.98,
    Bad Model: false,
    Popularity: 95.0 - avg 0,
    Longevity: 26 - avg 11,
    Make Rating: 78 - avg 50

    ____  SELLER INFO ____
    Name: Lydia,
    Number: 3852088805,
    Member Since: 2017-11-01,

    ____ AD INFO ____
    URL: http://www.ksl.com/auto/listing/4362280,
    Location: HIGHLAND UT,
    Date Posted: 2018-01-04,
    Page Views: 1,
    Page Favs: 0,
    Info: Car that runs great but needs a bit of fixing up.
    
---------------------------------------------------------------------------------------------------------------------------- 
  
  
    
-----------------------------------------------  Getting Started  ----------------------------------------------------------
    


1. You must have a mySQL database set up with 4 tables within it - I call this Database KSL_WebScraper:
    First, set up an independent database using the SQL table templates. After this is done you can customize connection         settings in the setting.txt file. This allows the web scraper to accumilate data so you can make a more informed             decision when buying your vehicle

2. Set up Twilio/Email:
    To be notified of the good deals you must have a Twilio or Gmail account. This can easily be done, go to twilio's           website and applying for a twilio api key and password. When this is set up you can enter the relevant information into     the settings.txt file. 


3. Finish Customizing the Settings file:
    Go through each of the relevant fields in the setting.txt file and customize them to meet the specifications of your SQL database, your email, etc.

---------------------------------------------------   Usage   --------------------------------------------------------------


    The KSL_Scraper is meant to be run 24/7 - so Error handling is a must. You will be able to see different types of
    errors through the console. A single "Error" in the Error Log signifies there was an unknown issue when processing the pulled listings.
    These are not uncommon but should occur at a rate of less than 1-10. Other issues such as the scraper being unable
    to build a certain listings car will be displayed as well.

    The Scraper can be started by running the scrape.py file from the command line.

    1. Verify the relevant mySQL server is activated
    2. Verify the relevant Emails are activated
    2. Go to /Messenger_Pigeon --- not /Messenger_Pigeon/Messenger_Pigeon
    3. type python3 scrape.py
    
    
----------------------------------------------  Run Continuosly  -----------------------------------------------------------

    This will run continuosly on your computer. Network conditions may cause the system to fail - Because of this of this a chron job should be scheduled to:

    1. Check the status of the program
    2. If the program has crashed - simply run scrape.py
    3. If the program is currently running allow it to continue
    
   
   An additional chron job to can be added to run the program during non peak hours in intervals. This will limit the amount of network requests sent and shrink you digital footprint - and its enviormentally friendly.
   
   
----------------------------------   Error Logging and System Preformance    -----------------------------------------------

    The program is monitored in by both a local system log  and an online error database so system preformance and points of failure can be tracked on multiple levels. 
    
    The local system log monitors the basic proccesess of the program so system preformance and points of failure can be monitored from a modular level. Important process names and thier start times are loaded to a .txt file into a Log folder that is created when the program is initially run (if it does not exist). ErrorsThere is an example log provided below.
    
    - loading objects - The ad page data is being extracted and transformed into relevant objects (See Objects section)
    - objects loaded - The objects were succesfully loaded into the database
    - Should send Car Deal - The objects met specification and the relevant email should be notified
    - Sent Deal of Car - The relevant email was succesfully notified
    - success - An ad car page was succesfully proccessed
    - Processed all listings - All current listings posted on the ad board have been proccessed
    - Scraper Exception - A known exception occured and was succesfully handled
    - Unknown Exception - An unknown exception occured
    
    The online error database is used to track events that cause Scraper Exceptions, and the relevant data assosiated with them. When an error occurs it is handled, classified, and uploaded to the database along with the relevant car ad data. This allows errors to be tracked to specific ads, data upload attempts, or notification attempts. It also allows each modules error rate to be evaluated over the lifespan of the program.

   
           ----------------------------------    Example Log   ---------------------------------------------
   
loading objects 17:16:34
objects loaded 17:16:40
success 17:16:40
loading objects 17:16:45
objects loaded 17:16:51
Should send Car Deal 17:16:51
Sent deal of car with id of c8eb5aaa-9494-44b9-9451-a2e9783e8766 17:16:52
success 17:16:53
loading objects 17:16:58
objects loaded 17:17:05
success 17:17:06
loading objects 17:17:11
objects loaded 17:18:19
success 17:18:19
loading objects 17:18:26
objects loaded 17:18:32
Scraper Exception 17:18:33
loading objects 17:18:38
objects loaded 17:18:44
success 17:18:45
loading objects 17:18:50
objects loaded 17:18:56
Processed all listings 17:19:01
