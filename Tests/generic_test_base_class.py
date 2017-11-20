import unittest
from Messenger_Pigeon.Objects.Database_Objects.car import Car
from Messenger_Pigeon.Objects.Database_Objects.seller import Seller
from Messenger_Pigeon.Objects.Database_Objects.processed_listing import Processed_Listing
from Messenger_Pigeon.Objects.Database_Objects.database_error import ScraperException
from Messenger_Pigeon.Objects.Database_Objects.unproccessed_listing import Unprocessed_Listing
from Messenger_Pigeon.Objects.sql_connection import SQL_Connection
import uuid


class Generic_Test_Class(unittest.TestCase):
    def setUp(self):
        self.connection_object = SQL_Connection(host='localhost',
                                                user='root',
                                                password='',
                                                db_name='KSL_WebScraper'
                                                )

        self.connection_object.open_connection()