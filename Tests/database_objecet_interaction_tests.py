import unittest
from Messenger_Pigeon.Objects import sql_connection as SQL
from Messenger_Pigeon.Objects.Database_Objects import car, seller, database_error, processed_listing, \
    unproccessed_listing, database_object
from Messenger_Pigeon.Objects import sql_connection
from Tests.generic_test_base_class import Generic_Test_Class
from pymysql import err as E

from Messenger_Pigeon.Objects.sql_connection import SQL_Connection


class SQL_Connection_Tester(Generic_Test_Class):
    def setUp(self):
        super().setUp()
        self.connection_object = SQL_Connection(host='localhost',
                                                user='root',
                                                password='',
                                                db_name='KSL_WebScraper'
                                                )

        self.connection_object.open_connection()

    #####
    #####       The following tests are for endge cases invoving the sql_connection_object
    #####

    def test_sql_compatible_uncompatible(self):
        with self.assertRaises(SQL.IllegalObjectException):
            self.connection_object.remove_object('')

    def test_invalid_server_info_connection_attempt(self):
        self.connection_object = SQL_Connection(host='localhos',
                                                user='root',
                                                password='',
                                                db_name='KSL_WebScraper'
                                                )
        with self.assertRaises(E.OperationalError):
            self.connection_object.open_connection()

    def test_modify_invalid_table_name(self):
        with self.assertRaises(sql_connection.TableArgumentException):
            self.connection_object.modify_table_attribute('Invalid', 'valid', '0')

    def test_modify_invalid_key_name(self):
        with self.assertRaises(sql_connection.KeyArgumentException):
            self.connection_object.modify_table_attribute('Cars', 'Invalid', 0)


        #####
        #####       The following tests are to check the database_object
        #####

    def test_database_obj_not_none_true(self):
        the_car = car.Car.generic_self()
        self.assertTrue(the_car.not_none('l'))

    def test_database_obj_not_none_false(self):
        the_car = car.Car.generic_self()
        self.assertFalse(the_car.not_none(''))

    def test_database_obj_normalize_for_varchar_normal(self):
        origional_string = 'hey_bob'
        for_varchar = database_object.DataBase_Object.normalize_for_varchar(origional_string)
        self.assertTrue(str(for_varchar) == str(origional_string))

    def test_database_obj_normalize_for_varchar_contains_single_quote(self):
        orgin_string = "that's a wrap"
        for_varchar = database_object.DataBase_Object.normalize_for_varchar(orgin_string)
        self.assertTrue(for_varchar == 'thats a wrap')

    #####
    #####           THE FOLLOWING TESTS WILL TEST THE real_self(), from_database_json(dict), and generic_self() of all database_object subclasses
    #####

    # ----------------------------------- CAR -------------------------------------------------------------------------------
    def test_build_from_database_values_car(self):
        the_car = car.Car.real_self(self.connection_object)
        is_duplicate = self.connection_object.is_duplicate(the_car)
        self.assertTrue(is_duplicate)

    def test_generic_self_car(self):
        the_car = car.Car.generic_self()
        self.connection_object.remove_object(the_car)
        self.assertFalse(self.connection_object.is_duplicate(the_car))

    def test_upload_duplicate_object_car(self):
        duplicate_car = car.Car.real_self(self.connection_object)
        with self.assertRaises(sql_connection.ExecutionException):
            self.connection_object.post_object(duplicate_car)

    def test_upload_original_car(self):
        origional_car = car.Car.generic_self()
        exited_prior = self.connection_object.remove_object(origional_car)
        could_add = self.connection_object.post_object(origional_car)
        could_remove = self.connection_object.remove_object(origional_car)
        self.assertTrue(could_add == could_remove == True)

    def test_increment_car(self):
        the_car = car.Car.real_self(self.connection_object)
        increment_result = self.connection_object.increment_object(the_car)
        self.assertFalse(increment_result)

    def test_remove_fake_car(self):
        the_car = car.Car.generic_self()
        remove_result = self.connection_object.remove_object(the_car)
        self.assertFalse(remove_result)

    def test_remove_real_car(self):
        the_car = car.Car.real_self(self.connection_object)
        remove_result = self.connection_object.remove_object(the_car)
        add_result = self.connection_object.post_object(the_car)
        self.assertTrue(True == add_result == remove_result)

    def test_add_fake_car(self):
        the_car = car.Car.generic_self()
        add_result = self.connection_object.add_object(the_car)
        remove_result = self.connection_object.remove_object(the_car)
        self.assertTrue(True == add_result == remove_result)

    def test_add_real_car(self):
        the_car = car.Car.real_self(self.connection_object)
        add_result = self.connection_object.add_object(the_car)
        self.assertFalse(add_result)

    def test_modify_object_attribute_real_car(self):
        first_car = car.Car.real_self(self.connection_object)
        first_model = first_car.model
        self.connection_object.modify_object_attribute(first_car, 'model', "second", )
        second_car = car.Car.from_database_json(
            self.connection_object.grab_listing(first_car.table, first_car.unique_where()))
        second_model = second_car.model
        self.connection_object.modify_object_attribute(second_car, 'model', f"{first_model}")
        final_car = car.Car.from_database_json(
            self.connection_object.grab_listing(first_car.table, first_car.unique_where()))
        final_model = final_car.model
        self.assertTrue(first_model == final_model and second_model == 'second')

    def test_modify_object_attribute_real_car_unstringed_string_atrribute(self):
        first_car = car.Car.real_self(self.connection_object)
        first_model = first_car.model
        self.connection_object.modify_object_attribute(first_car, 'model', "second", )
        second_car = car.Car.from_database_json(
            self.connection_object.grab_listing(first_car.table, first_car.unique_where()))
        second_model = second_car.model
        self.connection_object.modify_object_attribute(second_car, 'model', f"{first_model}")
        final_car = car.Car.from_database_json(
            self.connection_object.grab_listing(first_car.table, first_car.unique_where()))
        final_model = final_car.model
        self.assertTrue(first_model == final_model and second_model == 'second')

    def test_modify_nonstring_atrribute_car(self):
        first_car = car.Car.real_self(self.connection_object)
        first_value = first_car.title_type
        self.connection_object.modify_object_attribute(first_car, 'title_type', "3", )
        second_car = car.Car.from_database_json(
            self.connection_object.grab_listing(first_car.table, first_car.unique_where()))
        second_value = second_car.title_type
        self.connection_object.modify_object_attribute(second_car, 'title_type', f"{first_value.value}")
        final_car = car.Car.from_database_json(
            self.connection_object.grab_listing(first_car.table, first_car.unique_where()))
        final_value = final_car.title_type
        self.assertTrue(first_value == final_value and second_value.value == 3)

    # ----------------------------------- ERROR -----------------------------------------------------------------------------
    def test_build_from_database_values_error(self):
        the_error = database_error.ScraperException.real_self(self.connection_object)
        is_duplicate = self.connection_object.is_duplicate(the_error)
        self.assertTrue(is_duplicate)

    def test_generic_self_error(self):
        the_error = database_error.ScraperException.generic_self()
        self.assertFalse(self.connection_object.is_duplicate(the_error))

    def test_upload_duplicate_object_error(self):
        duplicate_exception = database_error.ScraperException.real_self(self.connection_object)
        with self.assertRaises(sql_connection.ExecutionException):
            self.connection_object.post_object(duplicate_exception)

    def test_upload_original_error(self):
        origional_error = database_error.ScraperException.generic_self()
        exited_prior = self.connection_object.remove_object(origional_error)
        could_add = self.connection_object.post_object(origional_error)
        could_remove = self.connection_object.remove_object(origional_error)
        self.assertTrue(could_add == could_remove == True)

    def test_increment_error(self):
        the_error = database_error.ScraperException.real_self(self.connection_object)
        preincrement = the_error.seen
        increment_result = self.connection_object.increment_object(the_error)
        incremented_errer = database_error.ScraperException.from_database_json(self.connection_object.grab_listing(the_error.table, the_error.unique_where()))
        post_increment = incremented_errer.seen
        self.connection_object.modify_object_attribute(the_error, 'seen', preincrement)
        final_error = database_error.ScraperException.from_database_json(self.connection_object.grab_listing(the_error.table, the_error.unique_where()))
        final_increment = final_error.seen
        self.assertTrue(
            preincrement == post_increment - 1 == final_increment and True == increment_result)

    def test_remove_fake_error(self):
        the_error = database_error.ScraperException.generic_self()
        remove_result = self.connection_object.remove_object(the_error)
        self.assertFalse(remove_result)

    def test_remove_real_error(self):
        the_error = database_error.ScraperException.real_self(self.connection_object)
        remove_result = self.connection_object.remove_object(the_error)
        add_result = self.connection_object.post_object(the_error)
        self.assertTrue(True == add_result == remove_result)

    def test_add_fake_error(self):
        the_error = database_error.ScraperException.generic_self()
        add_result = self.connection_object.add_object(the_error)
        remove_result = self.connection_object.remove_object(the_error)
        self.assertTrue(True == add_result == remove_result)

    def test_add_real_error(self):
        the_error = database_error.ScraperException.real_self(self.connection_object)
        origionaly_seen = the_error.seen
        add_or_increment_result = self.connection_object.add_object(the_error)
        error_two = database_error.ScraperException.from_database_json(self.connection_object.grab_listing(the_error.table, the_error.unique_where()))
        seen_incremented = error_two.seen
        self.connection_object.modify_object_attribute(the_error, 'seen', origionaly_seen)
        final_error = database_error.ScraperException.from_database_json(self.connection_object.grab_listing(the_error.table, the_error.unique_where()))
        final_seen = final_error.seen
        self.assertTrue(True == add_or_increment_result and origionaly_seen == seen_incremented -1 == final_seen)

    def test_modify_object_attribute_real_error(self):
        with self.assertRaises(sql_connection.UnmutableKey):
            first_error = database_error.ScraperException.real_self(self.connection_object)
            first_reason = first_error.why_thrown
            self.connection_object.modify_object_attribute(first_error, 'why_thrown', "TEST", )
            second_error = database_error.ScraperException.from_database_json(
                self.connection_object.grab_listing(first_error.table, first_error.unique_where()))
            second_reason = second_error.why_thrown
            self.connection_object.modify_object_attribute(second_error, 'model', f"{first_reason}")
            final_error = database_error.ScraperException.from_database_json(
                self.connection_object.grab_listing(first_error.table, first_error.unique_where()))
            final_reason = final_error.why_thrown
            self.assertTrue(first_reason == final_reason and second_reason == 'BAD')

    # -------------------------------- PROCCESSED_LISTING -------------------------------------------------------------------
    def test_build_from_database_values_processed_listing(self):
        the_proccessed_listing = processed_listing.Processed_Listing.real_self(self.connection_object)
        is_duplicate = self.connection_object.is_duplicate(the_proccessed_listing)
        self.assertTrue(is_duplicate)

    def test_generic_self_processed_listing(self):
        the_processed_listing = processed_listing.Processed_Listing.generic_self()
        self.assertFalse(self.connection_object.is_duplicate(the_processed_listing))

    def test_upload_duplicate_object_processed_listing(self):
        duplicate_processed_listing = processed_listing.Processed_Listing.real_self(self.connection_object)
        with self.assertRaises(sql_connection.ExecutionException):
            self.connection_object.post_object(duplicate_processed_listing)

    def test_upload_original_processed_listing(self):
        origional_processed_listing = processed_listing.Processed_Listing.generic_self()
        exited_prior = self.connection_object.remove_object(origional_processed_listing)
        could_add = self.connection_object.post_object(origional_processed_listing)
        could_remove = self.connection_object.remove_object(origional_processed_listing)
        self.assertTrue(could_add == could_remove == True)

    def test_increment_processed_listing(self):
        the_processed_listing = processed_listing.Processed_Listing.real_self(self.connection_object)
        increment_result = self.connection_object.increment_object(the_processed_listing)
        self.assertTrue(False == increment_result)

    def test_remove_fake_processed_listing(self):
        the_processed_listing = processed_listing.Processed_Listing.generic_self()
        remove_result = self.connection_object.remove_object(the_processed_listing)
        self.assertFalse(remove_result)

    def test_remove_real_processed_listing(self):
        the_processed_listing = processed_listing.Processed_Listing.real_self(self.connection_object)
        remove_result = self.connection_object.remove_object(the_processed_listing)
        add_result = self.connection_object.post_object(the_processed_listing)
        self.assertTrue(True == add_result == remove_result)

    def test_add_fake_processed_listing(self):
        the_processed_listing = processed_listing.Processed_Listing.generic_self()
        add_result = self.connection_object.add_object(the_processed_listing)
        remove_result = self.connection_object.remove_object(the_processed_listing)
        self.assertTrue(True == add_result == remove_result)

    def test_add_real_processed_listing(self):
        the_error = processed_listing.Processed_Listing.real_self(self.connection_object)
        add_or_increment_result = self.connection_object.add_object(the_error)
        self.assertTrue(False == add_or_increment_result)

    def test_modify_object_attribute_processed_listing(self):
        with self.assertRaises(sql_connection.UnmutableKey):
            first_processed_listing = processed_listing.Processed_Listing.real_self(self.connection_object)
            first_id = first_processed_listing.id
            self.connection_object.modify_object_attribute(first_processed_listing, 'id', "TEST", )
            second_listing = processed_listing.Processed_Listing.from_database_json(self.connection_object.grab_listing(first_processed_listing.table, first_processed_listing.unique_where()))


    # ----------------------------------- UNPROCCESSED_LISTING --------------------------------------------------------------
    def test_build_from_database_values_unprocessed_listing(self):
        the_unproccessed_listing = unproccessed_listing.Unprocessed_Listing.real_self(self.connection_object)
        is_duplicate = self.connection_object.is_duplicate(the_unproccessed_listing)
        self.assertTrue(is_duplicate)

    def test_generic_self_unprocessed_listing(self):
        the_unprocessed_listing = unproccessed_listing.Unprocessed_Listing.generic_self()
        self.assertFalse(self.connection_object.is_duplicate(the_unprocessed_listing))


    def test_upload_duplicate_object_unprocessed_listing(self):
        duplicate_unprocessed_listing = unproccessed_listing.Unprocessed_Listing.real_self(self.connection_object)
        with self.assertRaises(sql_connection.ExecutionException):
            self.connection_object.post_object(duplicate_unprocessed_listing)

    def test_upload_original_unprocessed_listing(self):
        origional_unprocessed_listing = unproccessed_listing.Unprocessed_Listing.generic_self()
        exited_prior = self.connection_object.remove_object(origional_unprocessed_listing)
        could_add = self.connection_object.post_object(origional_unprocessed_listing)
        could_remove = self.connection_object.remove_object(origional_unprocessed_listing)
        self.assertTrue(could_add == could_remove == True)

    def test_increment_unprocessed_listing(self):
        the_unprocessed_listing = unproccessed_listing.Unprocessed_Listing.real_self(self.connection_object)
        preincrement = the_unprocessed_listing.attempts
        increment_result = self.connection_object.increment_object(the_unprocessed_listing)
        incremented_unprocessed_listing = unproccessed_listing.Unprocessed_Listing.from_database_json(self.connection_object.grab_listing(the_unprocessed_listing.table, the_unprocessed_listing.unique_where()))
        post_increment = incremented_unprocessed_listing.attempts
        self.connection_object.modify_object_attribute(the_unprocessed_listing, 'attempts', preincrement)
        final_unprocessed_listing = unproccessed_listing.Unprocessed_Listing.from_database_json(self.connection_object.grab_listing(the_unprocessed_listing.table, the_unprocessed_listing.unique_where()))
        final_increment = final_unprocessed_listing.attempts
        self.assertTrue(
            preincrement == post_increment - 1 == final_increment and True == increment_result)

    def test_remove_fake_unprocessed_listing(self):
        the_unprocessed_listing = unproccessed_listing.Unprocessed_Listing.generic_self()
        remove_result = self.connection_object.remove_object(the_unprocessed_listing)
        self.assertFalse(remove_result)

    def test_remove_real_unprocessed_listing(self):
        the_unprocessed_listing = unproccessed_listing.Unprocessed_Listing.real_self(self.connection_object)
        remove_result = self.connection_object.remove_object(the_unprocessed_listing)
        add_result = self.connection_object.post_object(the_unprocessed_listing)
        self.assertTrue(True == add_result == remove_result)

    def test_add_fake_unprocessed_listing(self):
        the_unprocessed_listing = unproccessed_listing.Unprocessed_Listing.generic_self()
        add_result = self.connection_object.add_object(the_unprocessed_listing)
        remove_result = self.connection_object.remove_object(the_unprocessed_listing)
        self.assertTrue(True == add_result == remove_result)

    def test_add_real_unprocessed_listing(self):
        the_unprocessed_listing = unproccessed_listing.Unprocessed_Listing.real_self(self.connection_object)
        origionaly_seen = the_unprocessed_listing.attempts
        add_or_increment_result = self.connection_object.add_object(the_unprocessed_listing)
        unprocessed_listing_two = unproccessed_listing.Unprocessed_Listing.from_database_json(self.connection_object.grab_listing(the_unprocessed_listing.table, the_unprocessed_listing.unique_where()))
        seen_incremented = unprocessed_listing_two.attempts
        self.connection_object.modify_object_attribute(the_unprocessed_listing, 'attempts', origionaly_seen)
        final_unprocessed_listing = unproccessed_listing.Unprocessed_Listing.from_database_json(self.connection_object.grab_listing(the_unprocessed_listing.table, the_unprocessed_listing.unique_where()))
        final_seen = final_unprocessed_listing.attempts
        self.assertTrue(True == add_or_increment_result and origionaly_seen == seen_incremented -1 == final_seen)

    def test_modify_object_attribute_real_unprocessed_listing(self):
        with self.assertRaises(sql_connection.UnmutableKey):
            first_unprocessed_listing = unproccessed_listing.Unprocessed_Listing.real_self(self.connection_object)
            first_reason = first_unprocessed_listing.ad_identifier
            self.connection_object.modify_object_attribute(first_unprocessed_listing, 'ad_identifier', "TEST", )


    # ---------------------------------------------- SELLER -----------------------------------------------------------------
    def test_build_from_database_values_seller(self):
        the_seller = seller.Seller.real_self(self.connection_object)
        is_duplicate = self.connection_object.is_duplicate(the_seller)
        self.assertTrue(is_duplicate)

    def test_generic_self_seller(self):
        the_seller = seller.Seller.generic_self()
        self.assertFalse(self.connection_object.is_duplicate(the_seller))

    def test_upload_duplicate_object_seller(self):
        duplicate_seller = seller.Seller.real_self(self.connection_object)
        with self.assertRaises(sql_connection.ExecutionException):
            self.connection_object.post_object(duplicate_seller)

    def test_upload_original_seller(self):
        origional_seller = seller.Seller.generic_self()
        exited_prior = self.connection_object.remove_object(origional_seller)
        could_add = self.connection_object.post_object(origional_seller)
        could_remove = self.connection_object.remove_object(origional_seller)
        self.assertTrue(could_add == could_remove == True)

    def test_increment_seller(self):
        the_seller = seller.Seller.real_self(self.connection_object)
        preincrement = the_seller.cars_posted
        increment_result = self.connection_object.increment_object(the_seller)
        incremented_seller = seller.Seller.from_database_json(self.connection_object.grab_listing(the_seller.table, the_seller.unique_where()))
        post_increment = incremented_seller.cars_posted
        self.connection_object.modify_object_attribute(the_seller, 'cars_posted', preincrement)
        final_seller = seller.Seller.from_database_json(self.connection_object.grab_listing(the_seller.table, the_seller.unique_where()))
        final_increment = final_seller.cars_posted
        self.assertTrue(
            preincrement == post_increment - 1 == final_increment and True == increment_result)

    def test_remove_fake_seller(self):
        the_seller = seller.Seller.generic_self()
        remove_result = self.connection_object.remove_object(the_seller)
        self.assertFalse(remove_result)

    def test_remove_real_seller(self):
        the_seller = seller.Seller.real_self(self.connection_object)
        remove_result = self.connection_object.remove_object(the_seller)
        add_result = self.connection_object.post_object(the_seller)
        self.assertTrue(True == add_result == remove_result)

    def test_add_fake_seller(self):
        the_seller = seller.Seller.generic_self()
        add_result = self.connection_object.add_object(the_seller)
        remove_result = self.connection_object.remove_object(the_seller)
        self.assertTrue(True == add_result == remove_result)

    def test_add_real_seller(self):
        the_seller = seller.Seller.real_self(self.connection_object)
        origionaly_seen = the_seller.cars_posted
        add_or_increment_result = self.connection_object.add_object(the_seller)
        seller_two = seller.Seller.from_database_json(self.connection_object.grab_listing(the_seller.table, the_seller.unique_where()))
        seen_incremented = seller_two.cars_posted
        self.connection_object.modify_object_attribute(the_seller, 'cars_posted', origionaly_seen)
        final_seller = seller.Seller.from_database_json(self.connection_object.grab_listing(the_seller.table, the_seller.unique_where()))
        final_seen = final_seller.cars_posted
        self.assertTrue(True == add_or_increment_result and origionaly_seen == seen_incremented -1 == final_seen)

    def test_modify_object_attribute_real_seller(self):
        with self.assertRaises(sql_connection.UnmutableKey):
            first_seller = seller.Seller.real_self(self.connection_object)
            first_reason = first_seller.seller_id
            self.connection_object.modify_object_attribute(first_seller, 'seller_id', "1234", )



if __name__ == '__main__':
    unittest.main()

#'67c1cbb549407d754fe1894f74b40c3e'