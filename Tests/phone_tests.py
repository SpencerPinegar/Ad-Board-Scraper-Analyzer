from unittest import TestCase
from Tests.generic_test_base_class import Generic_Test_Class
import unittest
import uuid
import nose
import Messenger_Pigeon.Objects.Database_Objects.car as car


class CAR_TESTER(Generic_Test_Class):

    def setUp(self):
        super().setUp()


    def test_ad_identifer_as_empty_string(self):
        with self.assertRaises(car.MissingEssentialDataException):
            the_car = car.Car(self.unique_id(),
                               "",
                               66666,
                               2016,
                               'Ford',
                               'truck',
                               'Its A Vibe',
                               'Hunk',
                               '1N4AL21E38N433799',
                               'clean',
                               'yellow',
                               'brown',
                               'manuel',
                                5.7,
                               'diesel',
                               'fair',
                               'excellent',
                               'AWD',
                                8,
                                4,
                               'THIS IS A TEST',
                                3,
                               False)

    def test_ad_identifer_as_none(self):
        with self.assertRaises(car.MissingEssentialDataException):
            the_car = car.Car(self.unique_id(),
                                  None,
                                  66666,
                                  2016,
                                  'Ford',
                                  'truck',
                                  'Its A Vibe',
                                  'Hunk',
                                  '1N4AL21E38N433799',
                                  'clean',
                                  'yellow',
                                  'brown',
                                  'manuel',
                                  '5.7',
                                  'diesel',
                                  'fair',
                                  'excellent',
                                  'AWD',
                                  '8',
                                  '4',
                                  'THIS IS A TEST',
                                  3,
                                  False)

    def test_all_fields_string_format(self):
        the_car = car.Car(self.unique_id(),
                               "123",
                               "66666",
                               "2016",
                               'Ford',
                               'truck',
                               'Its A Vibe',
                               'Hunk',
                               '1N4AL21E38N433799',
                               'clean',
                               'yellow',
                               'brown',
                               'manuel',
                                "5.7",
                               'diesel',
                               'fair',
                               'excellent',
                               'AWD',
                                "8",
                                "4",
                               'THIS IS A TEST',
                                "3",
                               False)

    def test_liters_miles_and_price_decimal_strings(self):
        the_car = car.Car(self.unique_id(),
                               "123",
                               "66666.6",
                               "2016",
                               'Ford',
                               'truck',
                               'Its A Vibe',
                               'Hunk',
                               '1N4AL21E38N433799',
                               'clean',
                               'yellow',
                               'brown',
                               'manuel',
                                "5.7",
                               'diesel',
                               'fair',
                               'excellent',
                               'AWD',
                                "8",
                                "4",
                               'THIS IS A TEST',
                                "3.18",
                               False)







if __name__ == '__main__':
    unittest.main()
