import datetime
from enum import Enum

from Messenger_Pigeon.Objects.Database_Objects.database_object import DataBase_Object
from Messenger_Pigeon.Objects.Database_Objects.database_error import ScraperException


class Seller(DataBase_Object):
    """
    A seller object that represents a poster of a listing
    """
    seller_id = ''  # the unique seller id
    name = ""  # the name of the seller
    phone_number = ""  # the sellers phone_number
    member_since = ""  # How long the seller has been a member of the posting site
    private_seller = False  # if the seller is posting for a company or not
    cars_posted = 1  # the amount of cars the seller has sold

    fields_to_compress = []
    table = 'Sellers'
    primary_key = 'seller_id'
    primary_key_is_string = False
    field_to_increment = 'cars_posted'
    unchanging_fields = ['seller_id']
    def __init__(self, name, phone, member_since, private_seller, seller_id):
        """
        Create a seller object
        :param name: The name of the seller as a string
        :param phone: The phone number of the seller as a string
        :param member_since: How long the seller has been a member of the sight as a string
        :param private_seller: If the seller isn't associated with a company
        :param seller_id: The unique seller ID
        """
        try:
            self.seller_id = seller_id
            self.name = name
            self.normalize_phone(phone)
            self.normalize_member_since(member_since)
            self.normalize_seller_type(private_seller)
        except Exception as e:
            raise BuildSellerException(e, self.seller_id)


    def normalize_seller_type(self, private_seller):
        """
        sets the seller type to the proper seller type Enum
        :param private_seller: bool - true if the seller isn't posting for a company i.e. a car dealership
        """
        if private_seller:
            self.private_seller = SellerType.PRIVATE
        else:
            self.private_seller = SellerType.DEALER

    def normalize_member_since(self, date_posted):
        """
        sets the member since to a normalized date format YYYY-MM-DD
        :param date_posted: the date posted as a string
        """
        self.member_since = datetime.datetime.strptime(date_posted, "%b %Y").strftime('%Y-%m-%d')

    def normalize_name(self, name):
        """
        sets the name to a normalized version of the name 
        :param name: The name of the seller
        """
        name = name.lower()
        if len(name) > 20:
            self.name = name[0:17] + ' TL'
            print("name was too long for database")

    def normalize_phone(self, phone_number):
        """
        Normalizes the phone number to a 10 digit integer
        :param phone_number: the phone number as a string
        """
        phone_number = str(phone_number)
        phone_number = phone_number.replace('(', '')
        phone_number = phone_number.replace(')', '')
        phone_number = phone_number.replace(' ', '')
        phone_number = phone_number.replace('-', '')
        if len(phone_number) == 11:
            phone_number = phone_number[1:]
        self.phone_number = int(phone_number)


    def unique_where(self):
        return f"seller_id = {self.seller_id}"

    def database_dict(self):
        """
        creates a dictionary that represents the object and that can be uploaded into the database
        :return: dict(string, value)
        """
        return {'seller_id': self.seller_id,
                'name': DataBase_Object.normalize_for_varchar(self.name),
                'phone_number': self.phone_number,
                'member_since': self.member_since,
                'private_seller': self.private_seller.value
                }

    @staticmethod
    def generic_self():
        """
        Returns a generic Car
        :return: 
        """
        return Seller('BOB IRWIN', '801-888-8888', 'May 2017', True, 1234)


    @staticmethod
    def real_self(sql_connection):
        """
        returns a car object representing a record from the actual_database
        :return: 
        """
        obj = sql_connection.grab_listings(Seller.table, limit=1)[0]
        return Seller.from_database_json(obj)

    @staticmethod
    def from_database_json(JSON_dict):
        """
        Creates a moc car from database json data
        :param JSON_dict: 
        """
        the_seller = Seller.generic_self()
        the_seller.seller_id = JSON_dict['seller_id']
        the_seller.name = JSON_dict['name']
        the_seller.phone_number = JSON_dict['phone_number']
        the_seller.normalize_seller_type(bool(JSON_dict['private_seller']))
        the_seller.cars_posted = JSON_dict['cars_posted']
        return the_seller


class SellerType(Enum):
    """
    a seller type enum to represent all kinds of sellers
    the value is used in the db to save db file size
    """
    DEALER = 0
    PRIVATE = 1


class BuildSellerException(ScraperException):
    """
    This exception is raised when there is an issue building a seller
    """

    def __init__(self, e,  seller_id):
        """
        builds the Exception
        :param seller_id: The seller id associated with the seller that could not be built
        :return: 
        """
        message = f'Unable to build Seller with {seller_id}'
        super().__init__(e, message, BuildSellerException)
