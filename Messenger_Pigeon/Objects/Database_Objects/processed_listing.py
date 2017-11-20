import datetime
from Messenger_Pigeon.Objects.Database_Objects.database_object import DataBase_Object
from Messenger_Pigeon.Objects.Database_Objects.database_error import ScraperException


class Processed_Listing(DataBase_Object):
    """
    A lisitng that has an associated car, and seller object.
    """
    id: str = ''
    ad_identifier = 0  # The ad Identifier of the listing
    date_posted = ""  # The date the listing was posted
    page_views = 0  # The amount of views the listing has recieved
    page_favorites = 0  # The amount of favorites the listing has recieved
    seller_id = ""  # The ID of the seller who posted the listing
    location = ""  # The location of the item posted
    info = ""  # The info about the listing posted

    # analytics
    desperation = 0
    fields_to_compress = []
    table = 'Processed_Listings'
    primary_key = 'id'
    unchanging_fields = ['id']


    def __init__(self, item_id, date_posted, page_views, page_favorites, ad_identifier, seller_id, info, location):
        """
        Creates a proccessed listing item
        :param date_posted: The date the listing was posted
        :param page_views:  The amount of views the listing has recieved
        :param page_favorites: The amount of favorites the listing has recieved
        :param ad_identifier: The ad identifier of the listing
        :param seller_id: The seller ID of the poster of the listing
        :param info: The info contained in the posting (paragraph)
        :param location: The location of the item posted
        """
        try:
            self.id = str(item_id)
            self.page_views = page_views
            self.normalize_date(date_posted)
            self.page_favorites = page_favorites
            self.ad_identifier = ad_identifier
            self.seller_id = seller_id
            self.info = info
            self.location = location
        except Exception as e:
            raise BuildProccessedListingException(e, item_id)


    def normalize_date(self, date_posted):
        """
        Sets the date as a normalized date string - format YYY-MM-DD
        :param date_posted: the date the ad was posted as a string
        """
        date_posted = str(date_posted).replace(',', '')
        self.date_posted = datetime.datetime.strptime(date_posted, "%B %d %Y").strftime('%Y-%m-%d')

    def database_dict(self):
        """
        Returns a database dictionary so the item can be uploaded
        :return: dict(stirng, value)
        """
        return {
            'id': DataBase_Object.normalize_for_varchar(self.id),
            'ad_identifier': self.ad_identifier,
            'date_posted': self.date_posted,
            'page_views': self.page_views,
            'page_favorites': self.page_favorites,
            'seller_id': self.seller_id,
            'info': DataBase_Object.normalize_for_varchar(self.info),
            'location': DataBase_Object.normalize_for_varchar(self.location)
        }

    def unique_where(self):
        return f"id = '{DataBase_Object.normalize_for_varchar(self.id)}'"


    @staticmethod
    def real_self(sql_connection):
        """
        returns a car object representing a record from the actual_database
        :return: 
        """
        obj = sql_connection.grab_listings(Processed_Listing.table, limit=1)[0]
        return Processed_Listing.from_database_json(obj)


    @staticmethod
    def generic_self():
        """
        Returns a generic Car
        :return: 
        """
        return Processed_Listing('FAKEIDFORTEST',
                                 'May 17, 1998',
                                 50,
                                 3,
                                 1111111,
                                 12342,
                                 'This is a fake ad and shit',
                                 'UP YOURS')

    @staticmethod
    def from_database_json(JSON_dict):
        """
        Creates a moc car from database json data
        :param JSON_dict: 
        """
        the_listing = Processed_Listing.generic_self()
        the_listing.id = JSON_dict['id']
        the_listing.ad_identifier = JSON_dict['ad_identifier']
        the_listing.date_posted = datetime.datetime.strptime(str(JSON_dict['date_posted']), '%Y-%m-%d').strftime('%Y-%m-%d')
        the_listing.page_views = JSON_dict['page_views']
        the_listing.page_favorites = JSON_dict['page_favorites']
        the_listing.seller_id = JSON_dict['seller_id']
        the_listing.info = JSON_dict['info']
        the_listing.location = JSON_dict['location']
        return the_listing




class BuildProccessedListingException(ScraperException):
    """
    This exception is thrown when there is an issue building a seller
    """

    def __init__(self, e, ad_identifier):
        """
        builds the BuildProccessedListingException
        :param ad_identifier: the ad_identifier of the listing that could not be built
        """
        message = f'Unable to build Proccessed Listing with {ad_identifier}'
        super().__init__(e, message, BuildProccessedListingException)
