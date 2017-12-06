import Messenger_Pigeon.Objects.phone as phone
from Tests.generic_test_base_class import Generic_Test_Class
import unittest
import scrape


class PHONE_TESTER(Generic_Test_Class):

    def setUp(self):
        super().setUp()
        self.cell_phone = phone.Phone()
        self.functional_number_one = '8016692828'
        self.functional_number_two = '8015921989'


    def test_normalize_number_basic(self):
        unnormalized = '8016692828'
        normalized_number = phone.Phone.normalize_number(unnormalized)
        self.assertTrue(normalized_number == '+18016692828')

    def test_normalize_number_full(self):
        unnormalized = '+18016692828'
        normalized_number = phone.Phone.normalize_number(unnormalized)
        self.assertTrue(normalized_number == '+18016692828')

    def test_normalize_number_extra(self):
        unnormalized = '+1801(669)2828'
        normalized_number = phone.Phone.normalize_number(unnormalized)
        self.assertTrue(normalized_number == '+18016692828')

    def test_normalize_number_strange(self):
        unnormalized = '+801(669)2828'
        normalized_number = phone.Phone.normalize_number(unnormalized)
        self.assertTrue(normalized_number == '+18016692828')

    def test_single_number_to_array(self):
        numb_array = phone.Phone.format_number_array('8016692828')
        self.assertTrue(['8016692828'] == numb_array)

    def test_many_number_to_array(self):
        numb_array = phone.Phone.format_number_array('8011234567, 1112223333')
        self.assertTrue(['8011234567', '1112223333'] == numb_array)

    def test_send_one_number(self):
        self.cell_phone.send_message(self.functional_number_one, 'lol')

    def test_send_multiple_number(self):
        self.cell_phone.send_message(f"'{self.functional_number_one}, {self.functional_number_two}'", '1&2')

    def test_read_from_settings(self):
        settings = scrape.get_settings()
        number_to_notify = settings['Number_To_Notify']
        self.cell_phone.send_message(number_to_notify, "read number from settings")




if __name__ == '__main__':
    unittest.main()
