import unittest
from Messenger_Pigeon.Objects.Database_Objects.car import Car
from Messenger_Pigeon.Objects.Database_Objects.seller import Seller
from Messenger_Pigeon.Objects.Database_Objects.processed_listing import Processed_Listing
from Messenger_Pigeon.Objects.Database_Objects.database_error import ScraperException
from Messenger_Pigeon.Objects.Database_Objects.unproccessed_listing import Unprocessed_Listing
import scrape
from Messenger_Pigeon.Objects.sql_connection import SQL_Connection
import uuid


class Generic_Test_Class(unittest.TestCase):
    def setUp(self):
        settings = scrape.get_settings()
        db_host = settings['DB_Host']
        db_user = settings['DB_User']
        db_password = settings['DB_Password']
        db_name = settings['DB_Name']
        self.connection_object = SQL_Connection(host=db_host,
                                                user=db_user,
                                                password=db_password,
                                                db_name=db_name
                                                )

        self.connection_object.open_connection()


    def unique_id(self):
        da_id = uuid.uuid4()
        str_id = str(da_id)
        return str_id