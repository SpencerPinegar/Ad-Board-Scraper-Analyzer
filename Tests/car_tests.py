from unittest import TestCase
from Tests.generic_test_base_class import Generic_Test_Class
import unittest
import uuid
import nose
import Messenger_Pigeon.Objects.Database_Objects.car as car


class CAR_TESTER(Generic_Test_Class):

    def setUp(self):
        super().setUp()

    def test_basic_car_build(self):
        self.assertEqual(self.test_car.price, 3)

    def test_ad_identifer_as_empty_string(self):
        the_car = car.Car(self.unique_id,
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
        self.assertEqual(the_car.ad_identifier, '')

    def test_ad_identifer_as_none(self):
        the_car = car.Car(self.unique_id,
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
        self.assertEqual(the_car.ad_identifier, '')






if __name__ == '__main__':
    unittest.main()
