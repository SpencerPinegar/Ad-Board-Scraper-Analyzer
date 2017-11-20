from Messenger_Pigeon.Objects.Database_Objects.database_object import DataBase_Object
from Messenger_Pigeon.Objects.Database_Objects.database_error import ScraperException


class Unprocessed_Listing(DataBase_Object):
    """
    This represents a listing that does not have an associated car or seller object
    """
    ad_identifier = 0  # the ad identfier of lsiting
    attempts = 1  # number of proccessing attempts

    # analytics
    fields_to_compress = []
    table = 'Unprocessed_Listings'
    primary_key = 'ad_identifier'
    field_to_increment = 'attempts'
    primary_key_is_string = False
    unchanging_fields = ['ad_identifier']
    def __init__(self, ad_identifier, attempts=1):
        """
        creates an unproccessed listing object
        :param ad_identifier: The ad identifier associated with the listing
        :param attempts: number of proccesing attempts
        :raises BuildUnproccessedListingException: if there is an issue building the unprocessed_listing
        """
        try:
            self.normalize_ad_identifier(ad_identifier)
            self.attempts = attempts
        except Exception as e:
            raise BuildUnproccesedListingException(e, ad_identifier)

    def normalize_ad_identifier(self, ad_identifier):
        """
        sets the ad identifier to the normilized verison of the ad_identifier
        :param ad_identifier: the ad identifier associated with the listing
        """
        self.ad_identifier = int(str(ad_identifier).strip())

    def unique_where(self):
        return f"ad_identifier = {self.ad_identifier}"

    def database_dict(self):
        """
        represents the object as a dictionary so it can be uploaded into the MYSQL database
        :return: dict(string, value)
        """
        return {'ad_identifier': self.ad_identifier,
                'attempts': 1
                }

    @staticmethod
    def generic_self():
        """
        Returns a generic Car
        :return: 
        """
        return Unprocessed_Listing(1111111)


    @staticmethod
    def real_self(sql_connection):
        """
        returns a car object representing a record from the actual_database
        :return: 
        """
        obj = sql_connection.grab_listings(Unprocessed_Listing.table, limit=1)[0]
        return Unprocessed_Listing.from_database_json(obj)

    @staticmethod
    def from_database_json(JSON_dict):
        """
        Creates a moc car from database json data
        :param JSON_dict: 
        """
        unproccesed_ad = Unprocessed_Listing.generic_self()
        unproccesed_ad.ad_identifier = JSON_dict['ad_identifier']
        unproccesed_ad.attempts = JSON_dict['attempts']
        return unproccesed_ad


class BuildUnproccesedListingException(ScraperException):
    """
    this Exception is thrown if there is an issue building an Unprocessed Listing
    """

    def __init__(self, e, ad_identifier):
        """
        build the Exception
        :param ad_identifier: The ad identifier associated with the unprocessed listing that could not be created 
        :return: 
        """
        message = f'Unable to build unproccessed listing with {ad_identifier}'
        super().__init__(e, message, BuildUnproccesedListingException)
