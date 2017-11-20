from Messenger_Pigeon.Objects.Database_Objects.database_object import DataBase_Object
import hashlib

class ScraperException(DataBase_Object, Exception):

    fields_to_compress = []  # The fields of the object that need to be compressed
    table: str = 'Errors'  # The table the object will be uploaded too
    primary_key: str = ''  # the primary key of the object and table
    field_to_increment: str = 'seen'  # If the object is being accessed and this needs to be tracked - this is the field
    unchanging_fields = ['causing_error', 'why_thrown']


    causing_error: str = None
    why_thrown: str = ''
    exception_class: str = ''
    seen = 1

    def __init__(self, e, why_thrown, exception_class):
        Exception.__init__(self)
        self.exception_class = str(exception_class)
        self.causing_error = str(e)
        self.why_thrown = why_thrown
        self.seen = 1


    def unique_hash(self):
        hash_obj = hashlib.md5((self.causing_error + self.why_thrown).encode())
        return hash_obj.hexdigest()


    def database_dict(self):
        return {'Hash': self.unique_hash(),
                'causing_error': DataBase_Object.normalize_for_varchar(self.causing_error),
                'why_thrown': DataBase_Object.normalize_for_varchar(self.why_thrown)
                }

    def unique_where(self):
        return f"Hash = '{DataBase_Object.normalize_for_varchar(self.unique_hash())}'"


    @staticmethod
    def generic_self():
        """
        Returns a generic Car
        :return: 
        """
        return ScraperException('THis is a fake original Exception', 'This is a generic Scraper Exception', ScraperException)


    @staticmethod
    def real_self(sql_connection):
        """
        returns a car object representing a record from the actual_database
        :return: 
        """
        obj = sql_connection.grab_listings(ScraperException.table, limit=1)[0]
        return ScraperException.from_database_json(obj)


    @staticmethod
    def from_database_json(JSON_dict):
        """
        Creates a moc car from database json data
        :param JSON_dict: 
        """
        exception = ScraperException.generic_self()
        exception.causing_error = JSON_dict['causing_error']
        exception.why_thrown = JSON_dict['why_thrown']
        exception.seen = JSON_dict['seen']
        return exception


