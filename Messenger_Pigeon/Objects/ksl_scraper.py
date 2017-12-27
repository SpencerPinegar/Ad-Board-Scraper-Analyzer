"""
This Project is Designed to pull the most recent listing from KSL for Cars the Project will:
    0- Scan KSL Cars Home Page for all latest listings
    1- Pull all relevant info for all listings
    2- Organize all Info into a Dictionary with values
        
"""
import uuid

from Messenger_Pigeon.Objects.Database_Objects import car
from Messenger_Pigeon.Generic_Funcs import requester
from Messenger_Pigeon.Objects.Database_Objects import processed_listing
from Messenger_Pigeon.Objects.Database_Objects import seller
from Messenger_Pigeon.Objects import sql_connection
from Messenger_Pigeon.Objects.Database_Objects import unproccessed_listing
from Messenger_Pigeon.Objects.Database_Objects.database_error import ScraperException
from Messenger_Pigeon.Objects import phone
from Messenger_Pigeon.Objects import logger
import time
import json


class KSL_SCRAPER(object):
    base_url = 'http://www.ksl.com'  # the base url of the site being scraped
    search_url = '/auto/search/index?'  # the search url used to navigate through pages of listings
    listing_url = '/auto/listing/'  # the listing url used for grabbing individual listing
    photo_url = '/auto/photo?ssid='  # the photo url used to find photos of listing
    url_args = {}  # the args being used to get the web page (see requests module)
    data_base = None  # The database object to be uploaded too
    queue_table = 'Unprocessed_Listings'  # the table in the db that hold the listings to be processed

    max_attempts = 2  # how many times you want to attempt to process each listing

    got_new_listings = False  # A field determining if all the new listings posted were seen or not
    check_dealerships = False  # Do you want the listing pages to include listing posted by dealerships
    range = 100  # include listings with a range of how many miles
    current_bs_object = None  # holds the last web page data loaded
    to_number = ''  # the number to be notified
    notifier = None  # the object that will be notifying the to_number
    logger = None



    def __init__(self,
                 _range,
                 number_to_notify,
                 proxy_ip=True,
                 db_host='localhost',
                 db_user='root',
                 db_password='',
                 db_name='KSL_WebScraper',
                 logs_file_path = ''
                 ):
        """
        Creates a webscraper object that will notify you about good deals on cars based on their price and value
        :param _range: The range of miles you want to see listings in
        :param number_to_notify: The numbers that will be texted about good deals that pop-up entered as an array of strings
        :param db_host: The address of the location hosting the db
        :param db_user: The user accessing the db
        :param db_password: The password for accessing the db
        :param db_name: The name of the db you are accessing
        """
        if str(proxy_ip).lower() == 'true':
            proxy_ip = True
        else:
            proxy_ip = False
        self.requester = requester.Requester(proxy_ip)
        self.range = int(_range)
        self.data_base = sql_connection.SQL_Connection(host=db_host,
                                                       user=db_user,
                                                       password=db_password,
                                                       db_name=db_name
                                                       )
        self.to_number = number_to_notify
        self.notifier = phone.Phone()
        self.logger = logger.Logger(logs_file_path)

    def load_new_listings(self,
                          max_pages=10,
                          ):
        """This Function grabs all the most recent listings from the KSL cars home page and uploads them to a
        mySQL database as Unprocessed Listing, these will be processed later
        :param max_pages: how many pages you want to cycle through, each page consigns 24 listings
        :raises InvalidBaseURLException: If the listing page url is unreachable
        """
        if self.check_dealerships:
            self.url_args = {'p': '',
                             'miles': str(self.range),
                             'page': '0',
                             }
        else:
            self.url_args = {'p': '',
                             'miles': str(self.range),
                             'sellerType[]': 'For Sale By Owner',
                             'page': '0',
                             }
        self.load_listings_page()
        max_possible_pages = self.current_bs_object.find('a', {'class': 'link', 'title': 'Go to last page'}).text
        self.got_new_listings = False
        for page_number in range(int(max_possible_pages)):
            if self.got_new_listings == True or page_number >= max_pages:
                break
            self.increment_page(page_number=page_number)
            self.load_unproccessed_listings()

    def increment_page(self, page_number):
        """
        This function increments the url args so we can view the next page, it also ensures the next page loads correctly
        :param page_number: The page number we want to view
        """

        if str(page_number) != self.url_args['page']:
            self.url_args['page'] = str(page_number)
            self.load_listings_page()
        listing_page_attempts = 0
        while not self.all_twentyfour_listings():
            if listing_page_attempts > 3:
                raise LoadListingPageException(url=self.base_url + self.search_url, url_args=str(self.url_args))
            self.load_listings_page()
            listing_page_attempts += 1

    def load_listings_page(self):
        """
        This function loads the current page we want to view based off the base_url, search_urls, and url_args
        """
        try:
            self.current_bs_object = self.requester.get_website_object(
                base_url=self.base_url + self.search_url,
                url_params=self.url_args,
                javascript_required=True,
                xpath_to_look_for='//a[@title="Go to last page"]'
            )
        except requester.InvalidBaseURLException:
            raise LoadListingPageException(url=self.base_url + self.search_url, url_args=str(self.url_args))

    def all_twentyfour_listings(self):
        """
        This function ensures that all 24 listings were loaded from the ksl page, returning true if they were, false if
        they where not
        :return: True if all 24 listings where loaded
        """
        listing_groups = self.current_bs_object.select('div[class^="listing-group"]')
        if len(listing_groups) != 4:
            return False
        for listing_group in listing_groups:
            listings = listing_group.select('div[class^="listing js-listing-"]')
            if len(listings) != 6:
                return False
        return True

    def load_unproccessed_listings(self):
        """
        This function goes through and processes all of the listings on the page in chronological order. It checks to see
        if the listing is a duplicate and if it is it finishes and sets the got_new_listings value to true
        :raises UnresolvedListingIDException: if the page loaded with listings that have invalid listing ID's 
        """

        duplicates = 0
        listing_groups = self.current_bs_object.select('div[class^="listing-group"]')
        for listing_group in listing_groups:
            listings = listing_group.select('div[class^="listing js-listing-"]')
            for the_listing in listings:
                listing_id = the_listing.get('data-id')
                info_dict = json.loads(the_listing.get('data-listing'))
                price = info_dict['price']
                mileage = info_dict['mileage']
                if listing_id is None:
                    raise UnresolvedListingIDException()
                if not self.upload_unproccessed_listing(listing_id, price, mileage):
                    duplicates = duplicates + 1
                if duplicates > 10:
                    self.got_new_listings = True

    def upload_unproccessed_listing(self, listing_identifier, price, mileage):
        """
        This function uploads the unprocessed listing to a mySQL database to be processed, if the listings has been
        it returns setting the got_new_listings instance variable to True
        :param listing_identifier: the listing ad_identifier as a string
        """
        unproccessed_to_be_uploaded = unproccessed_listing.Unprocessed_Listing(listing_identifier)
        unproccessed_car_version = unproccessed_listing.Unprocessed_Listing(listing_identifier)
        unproccessed_car_version.table = 'Cars'
        if self.data_base.is_duplicate(unproccessed_to_be_uploaded) or self.data_base.is_duplicate(
                unproccessed_car_version):
            return False
        self.data_base.post_object(unproccessed_to_be_uploaded)
        return True

    # All Above functions are used as helper functions for the load_new_listings method. They grab all unseen listings from
    # KSL and upload them to the unproccessed Listings database
    ########################################################################################################################

    def process_unproccessed_listings(self):
        """
        This page goes through and grabs all unprocessed listings from the database they are stored in. It loads all 
        seller, car, and proccessed_lising objects to the database, handling errors as they come to avoid crashing.
        This is the main lifter of the scraper object.
        """

        while True:
            unproc_listing = None
            try:
                unproc_items = self.data_base.grab_listings(table=self.queue_table,
                                                            where=f"attempts < {self.max_attempts}",
                                                            limit=1)
                if len(unproc_items) == 0:
                    self.logger.log("Processed all listings")
                    return
                unproc_dict = unproc_items[0]
                unproc_listing = unproccessed_listing.Unprocessed_Listing(unproc_dict['ad_identifier'],
                                                                          unproc_dict['attempts'])
                self.data_base.increment_object(unproc_listing)
                self.load_ad_page(unproc_listing.ad_identifier)
                self.logger.log("loading objects")
                ad_car, the_seller, the_listing = self.initlize_objects_from_page()
                self.logger.log("objects loaded")
                if not self.is_good_deal(ad_car):
                    self.logger.log("Should send Car Deal")
                    self.notifier.send_message(self.to_number, self.write_up_ad_page(ad_car, the_seller, the_listing))
                    self.logger.log(f"Sent deal of car with id of {the_listing.id}")
                self.data_base.add_object(ad_car)
                self.data_base.add_object(the_listing)
                self.data_base.add_object(the_seller)
                self.data_base.remove_object(unproc_listing)
                self.logger.log("success")

            except DeletedAdPageURLException:
                self.data_base.remove_object(unproc_listing)
            except ScraperException as e:
                self.logger.log('scraperException')
                self.data_base.add_object(e)
            except Exception as e:
                self.logger.log('unknown Exception')
                message = 'Unknown Error While Proccessing Listings'
                raise ScraperException(e, message, ScraperException)


    def work(self, max_pages):
        """
        The main function of the object, scrapes and reports on KSL Listings
        :param max_pages: 
        :return: 
        """
        try:
            self.data_base.open_connection()
            self.load_new_listings(max_pages)
            self.process_unproccessed_listings()
            self.data_base.close_connection()
            print('one cycle complete')
            time.sleep(60)

        except ScraperException as e:
            the_scraper = KSL_SCRAPER(_range=self.range,
                                      number_to_notify=self.to_number,
                                      proxy_ip=self.requester.proxy_ip,
                                      db_host=self.data_base.host,
                                      db_user=self.data_base.user,
                                      db_password=self.data_base.password,
                                      db_name=self.data_base.db_name
                                      )
            the_scraper.data_base.add_object(e)


                #     except car.CarFaxHistoryException:
                #     print(f'no car history available for {unproc_listing.ad_identifier}')
                # except car.GetBlueBookException:
                #     print(f"unable to get KBB value for {unproc_listing.ad_identifier}")
                # except car.LoadCarFaxException:
                #     print(f'unable to load carfax for {unproc_listing.ad_identifier} -- check your selenium funcs')
                #
                #
                # except unproccessed_listing.BuildUnproccesedListingException:
                #     print("unable to build unproccessed listing")
                # except processed_listing.BuildProccessedListingException:
                #     print(f"unable to build proccessed listing for page {unproc_listing.ad_identifier}")
                # except seller.BuildSellerException:
                #     print(f"unable to build seller for page {unproc_listing.ad_identifier}")
                # except car.BuildCarException:
                #     print(f"unable to build car with {unproc_listing.ad_identifier}")
                # except InvalidAdPageURLException:
                #     print(f"The URL for the Ad Page {unproc_listing.ad_identifier} is not real")
                #
                # except PullAdPageDataException:
                #     print(f"unable to pull neccesary data fields from {unproc_listing.ad_identifier}")
                # except sql_connection.ExecutionException as e:
                #     print(e.__str__())

                # except:
                #     print('shit')
                #     print('shit')

    def load_ad_page(self, ad_number):
        """
        loads a listing page with the associated ad number and sets it as the current_bs_object
        :param ad_number: the ad number of the page to be loaded
        :raises InvalidPageURLException: if the ad page does not exist
        :raises DeletedAdPageException: if the ad page has been removed
        """
        url = self.build_ad_url(ad_number)
        try:
            self.current_bs_object = self.requester.get_website_object(url, javascript_required=True,
                                                                       xpath_to_look_for='//h2[@class="specifications"]')
        except requester.InvalidBaseURLException:
            raise InvalidAdPageURLException(ad_number)
        if self.get_ad_title() == 'Missing or invalid ID!':
            raise DeletedAdPageURLException(url)

    def initlize_objects_from_page(self):
        """This function pulls all relevant data
            -Contact info: name, number, email, location
            -Car Specifications table: see read_specifications for more info
            -Sale Type: owner or dealership
            -Car Details: mileage, price, location
            -Add details: Ad Number, Page Views, Number of Favorites
            -Extra Car Info: photos, explanation
            
            And puts them into 3 objects:
                A Listing
                A Seller
                A Car
        :return: A car, seller, and a processing_listing
        :raises PullAdPageDataException: If certain data fields could not be pulled
        """
        unique_id = uuid.uuid4()
        try:
            title = self.get_ad_title()
            specifications = self.get_specifications()
            date_posted_and_location = self.get_date_posted_and_location()
            private_seller = self.get_private_seller()
            price = self.get_price()
            paragraph = self.get_paragraph()
            seller_name = self.get_seller_name()
            phone_number = self.get_seller_number()
            add_details = self.get_ad_details()
            seller_id = self.get_seller_id()

        except:
            raise PullAdPageDataException(unique_id)
        ad_car = car.Car(
            item_id=unique_id,
            identifier=add_details['Ad Number'],
            mileage=specifications['Mileage'],
            year=specifications['Year'],
            make=specifications['Make'],
            model=specifications['Model'],
            trim=specifications['Trim'],
            body=specifications['Body'],
            vin=specifications['VIN'],
            title_type=specifications['Title Type'],
            exterior_color=specifications['Exterior Color'],
            interior_color=specifications['Interior Color'],
            transmission=specifications['Transmission'],
            liters=specifications['Liters'],
            fuel_type=specifications['Fuel Type'],
            exterior_condition=specifications['Exterior Condition'],
            interior_condition=specifications['Interior Condition'],
            drive_type=specifications['Drive Type'],
            cylinders=specifications['Cylinders'],
            door_amount=specifications['Number of Doors'],
            title=title,
            price=price
        )

        the_seller = seller.Seller(name=seller_name,
                                   phone=phone_number,
                                   member_since=add_details['Member Since'],
                                   private_seller=private_seller,
                                   seller_id=seller_id
                                   )
        the_listing = processed_listing.Processed_Listing(
            item_id=unique_id,
            date_posted=date_posted_and_location['Date Posted'],
            page_views=add_details['Page Views'],
            page_favorites=add_details['Favorite of'],
            ad_identifier=add_details['Ad Number'],
            seller_id=seller_id,
            info=paragraph,
            location=date_posted_and_location['Location']
        )
        return ad_car, the_seller, the_listing

    def is_good_deal(self, car):
        """
        This function evaluates the value of the car
        :param car: the car we are checking to see if its a good deal
        :return: True if the car is a good deal
        """
        car_value = car.value[0]
        car_price = car.price
        car_accuracy = car.value[1]
        roi = (car_value - car_price) / car_price
        if car_value < 0:
            return False
        if car_accuracy < 35:
            return False
        if car_price > 4000 and roi < 1:
            return False
        if roi < .5:
            return False
        return True

    def write_up_ad_page(self, the_car, the_seller, the_listing):
        """
        Creates a write up for the ad page based on its page objects
        :param the_car: The car object scraped from the page
        :param the_seller: The seller object scraped from the page
        :return:  The page written up with all the important info as string
        """
        bad_model = 'false'
        if the_car.is_bad_model == 1:
            bad_model = 'true'
        return_string = f"""   INFO
        
    ___  CAR INFO  ___
    Make: {the_car.make.name},
    Model: {the_car.model},
    Price: {the_car.price},
    Value: {the_car.value[0]},
    Mileage: {the_car.mileage},
    Title Type: {the_car.title_type.name},
    Year: {the_car.year},
    Trim: {the_car.trim},
    Condition: {the_car._calculate_condition()},
    Color: {the_car.exterior_color.name}
        
    ___  CAR ANALYSIS  ___
    Value Accuracy: {the_car.value[1]},
    Price Dif: {the_car.value[0] - the_car.price},
    ROI: {(the_car.value[0] - the_car.price)/the_car.price},
    Bad Model: {bad_model},
    Popularity: {the_car.popularity} - avg 0,
    Longevity: {the_car.longevity} - avg 11,
    Make Rating: {the_car.make_reliability} - avg 50
         
    ____  SELLER INFO ____
    Name: {the_seller.name},
    Number: {the_seller.phone_number},
    Member Since: {the_seller.member_since},
         
    ____ AD INFO ____
    URL: {self.build_ad_url(the_car.ad_identifier)},
    Location: {the_listing.location},
    Date Posted: {the_listing.date_posted},
    Page Views: {the_listing.page_views},
    Page Favs: {the_listing.page_favorites},
    Info: {the_listing.info}
    """
        return return_string

    def build_ad_url(self, ad_number):
        """                                                                 
        returns the url for and ad number                                   
        :param ad_number: the ad number                                     
        :return: the page url as a string                                   
        """
        return f"{self.base_url}{self.listing_url}{ad_number}"

    #####ALL OF THE BELOW FUNCTIONS ARE TO GRAB ITEMS TO BUILD THE SELLER, LISTING, AND CAR BASED FROM THE CURRENT PAGE
    ########################################################################################################################

    def get_seller_id(self):
        """
        Grabs the unique seller ID from the currect_bs_object.
        :return seller_id: the seller id as a string
        """
        data_tag = self.current_bs_object.select_one('div[class="main-column"]')
        data = data_tag.get('data-listing')
        data = data[1:-1]
        key_val_pairs = data.split(',')
        seller_id = int(key_val_pairs[1].split(':')[1])
        return seller_id

    def get_date_posted_and_location(self):
        """
        This function grabs posting date of the ad and the location from the current_bs_object
        :return: A dict item containing when the car was posted and where the car is located - Dict
        """
        location_date_posted_and_tag = self.current_bs_object.select('h2[class="location"]')[0]
        location_and_date_posted = requester.Requester.grab_attribute(_attribute='text',
                                                                      beautifulsoup_tag=location_date_posted_and_tag,
                                                                      chars_to_strip=['$', ',', ',']
                                                                      )
        location_and_date_posted = location_and_date_posted.split('|')
        location = location_and_date_posted[0]
        location = location.strip()
        date_posted = location_and_date_posted[1]
        date_posted = date_posted.strip()
        date_posted = date_posted.strip('Posted ')
        date_posted_and_location_dict = {'Location': location, 'Date Posted': date_posted}
        return date_posted_and_location_dict

    def get_private_seller(self):
        """
        This function determines the seller type from the current_bs_object
        :return: True if from private seller - Boolean
        """
        seller_type_tag = self.current_bs_object.select('div[class="fsbo"]')[0]
        seller_type = requester.Requester.grab_attribute(_attribute='text',
                                                         beautifulsoup_tag=seller_type_tag,
                                                         chars_to_strip=['$', ',', ',']
                                                         )
        return seller_type.__contains__('For Sale By Owner')

    def get_price(self):
        """This function grabs the price of the car from the current_bs_object
          :return: the price of the car - Int
          :raises PullAdPageDataException: if unable to pull data from current_bs_object
          """
        try:
            price_tag = self.current_bs_object.select('h3[class="price cXenseParse"]')[0]
            price = requester.Requester.grab_attribute(_attribute='text',
                                                       beautifulsoup_tag=price_tag,
                                                       chars_to_strip=['$', ',', ' ', ',']
                                                       )
            return price
        except:
            raise PullAdPageDataException

    def get_seller_name(self):
        """
        This function grabs the name of the seller from the current_bs_object
        :return: the sellers name - String
        """
        try:
            name_tag = self.current_bs_object.select('span[class="vdp-contact-text first-name"]')[0]
            name = requester.Requester.grab_attribute(_attribute='text',
                                                      beautifulsoup_tag=name_tag,
                                                      )
            return name
        except IndexError:
            return ''

    def get_seller_number(self):
        """
        This function grabs the number of the seller from the current_bs_object
        :return: the number of the seller - Int
        """
        try:
            number_tag = self.current_bs_object.select('span[class="vdp-contact-text"]')[0]
            number = requester.Requester.grab_attribute(_attribute='text',
                                                        beautifulsoup_tag=number_tag,
                                                        chars_to_strip=['(', ')', ' ', '-'],
                                                        )
            return number
        except IndexError:
            return '-1'

    def get_paragraph(self):
        """
        This function grabs the info paragraph posted by the seller from the current_bs_object
        :return: the description paragraph - String
        """
        paragraph_tag = self.current_bs_object.select('div[class="hide full cXenseParse"]')[0]
        paragraph = requester.Requester.grab_attribute(_attribute='text',
                                                       beautifulsoup_tag=paragraph_tag,
                                                       )
        return paragraph

    def get_ad_title(self):
        """
        Grabs the ads title from the current_bs_object
        :return: the ad title of the listing as string
      """
        title_tag = self.current_bs_object.select_one('#titleMain > h1 > div')
        return_val = requester.Requester.grab_attribute(_attribute='text', beautifulsoup_tag=title_tag)
        return return_val

    def get_specifications(self):
        """
        This function grabs info from the specification table in the current_bs_object
        :return: a dict object with the key value pairs from the table
        """

        dict_key = None
        dict_value = None
        specifications_dictionary = {}
        specifications = self.current_bs_object.select('li[class^="specificationsTableRow"]')
        for specification in specifications:
            dict_key_found = False
            dict_value_found = False
            for tag in specification.contents:
                if tag.name == 'span':
                    if tag['class'][0] == 'title':
                        dict_key = requester.Requester.grab_attribute(_attribute='text',
                                                                      beautifulsoup_tag=tag,
                                                                      chars_to_strip=[':', ',']
                                                                      )
                        dict_key_found = True
                    elif tag['class'][0] == 'value':
                        dict_value = requester.Requester.grab_attribute(_attribute='text',
                                                                        beautifulsoup_tag=tag,
                                                                        chars_to_strip=[':', ',']
                                                                        )
                        dict_value_found = True
                        if dict_value is 'Not Specified':
                            dict_value = ''
                    if dict_key_found and dict_value_found:
                        specifications_dictionary[dict_key] = dict_value
        return specifications_dictionary

    def get_ad_details(self, ):
        """
        Grabs the ad details from the current_bs_object
        :return: a dict object with the key value pairs from the add details
        """
        dict_value = None
        dict_key = None
        add_details_dictionary = {}
        add_details = self.current_bs_object.select('li[class="vdp-contact-info"]')
        for add_detail in add_details:
            dict_key_found = False
            dict_value_found = False
            for tag in add_detail.contents:
                if tag.name == 'span':
                    if tag['class'][0] == 'vdp-info-key':
                        dict_key = requester.Requester.grab_attribute(_attribute='text',
                                                                      beautifulsoup_tag=tag,
                                                                      chars_to_strip=[':', ','],
                                                                      )
                        dict_key_found = True
                    elif tag['class'][0] == 'vdp-info-value':
                        if dict_key == 'Member Since':
                            spacing_index = -1
                        else:
                            spacing_index = 0
                        dict_value = requester.Requester.grab_attribute(_attribute='text',
                                                                        beautifulsoup_tag=tag,
                                                                        chars_to_strip=[':', ','],
                                                                        spacing_index=spacing_index,
                                                                        )

                        dict_value_found = True
                    if dict_key_found and dict_value_found:
                        add_details_dictionary[dict_key] = dict_value
        return add_details_dictionary


class DeletedAdPageURLException(ScraperException):
    """
    This exception is raised when the ad page has been removed
    """

    def __init__(self, ad_id):
        """
        creates Exception
        :param ad_id: The ad identifier associated with the delted listing
        """
        message = f'The listing page for for URL {ad_id} has been taken down'
        super().__init__('', message, DeletedAdPageURLException)


class InvalidAdPageURLException(ScraperException):
    """
    This exception is raised when the ad page cannot be found
    """

    def __init__(self, ad_id):
        """
        creates Exception
        :param ad_id: The ad identifier associated with the invalid listing
        """
        message = f'Unable to load listing page for URL {ad_id}'
        super().__init__('', message, InvalidAdPageURLException)


class PullAdPageDataException(ScraperException):
    """
    This exception is raised when a value from the ad page cannot be pulled/found
    """

    def __init__(self, ad_id):
        """
        creates Exception
        :param ad_id: The ad identifier associated with the listing that cannot be pulled
        """
        message = f'Unable to load listing page for URL {ad_id}'
        super().__init__('', message, PullAdPageDataException)


class LoadListingPageException(ScraperException):
    """
    This exception is raised when the Listing page cannot be loaded
    """

    def __init__(self, url, url_args):
        """
        creates exception
        :param url: The url of the page that could not be loaded
        :param url_args: The url args (see requests module) of the page that could not be loaded
        """
        message = f'Unable to load all 24 listings for the URL {url} with the args {url_args}'
        super().__init__('', message, LoadListingPageException)


class UnresolvedListingIDException(ScraperException):
    """
    This exception is raised when we are trying reference an ID that doesn't exist or doesnt have a number
    """

    def __init__(self):
        """
        Creates Exception
        """
        message = f'Unable to pull ID from Unprocessed Listing'
        super().__init__('', message, UnresolvedListingIDException)


