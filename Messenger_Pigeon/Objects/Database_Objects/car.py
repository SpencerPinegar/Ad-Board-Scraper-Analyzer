from math import floor
import re
from Messenger_Pigeon.Generic_Funcs import blue_book_funcs as BB
from Messenger_Pigeon.Generic_Funcs import generic_seleniun_fuc as GS
from Messenger_Pigeon.Objects.Database_Objects.database_object import DataBase_Object
from Messenger_Pigeon.Generic_Funcs import requester as GW
from Messenger_Pigeon.Objects.Database_Objects.database_error import ScraperException
import uuid

# Edmunds api Username: Spencer Pinegar  - Password: MemoriseMyMusic3$

"""
This class creates a car object which can be uploaded into a database using the sql_connection object wrapper.
It builds cars using scrape attributes, and predicts their value
"""


def normalize(item, to_number=False, make_int=True, essential_field_name=None):
    """
    If the value was not entered in it is set to an empty string
    :param item: the value to be normalized
    :return: the normalized item
    """
    if str(item).lower() == 'not specified' or item == None or item == '':
        if essential_field_name is not None:
            raise MissingEssentialDataException(essential_field_name)
        item = ''
    else:
        item = str(item)
    if to_number:
        if item == '':
            return 0
        else:
            if make_int:
                return int(round(float(item)))
            else:
                return float(item)
    else:
        return item


class Car(DataBase_Object):
    """
    The Car class is used to model cars that have been created, pulling as much info as possible and then
    using this info
    """

    # basic fields about the car
    id: str = ''
    ad_identifier: int = 0
    title: str = ''
    mileage: int = 0
    year: int = 0
    make = ''
    model: str = ""
    trim: str = ""
    body: str = ""
    vin: str = ""
    title_type = ''
    transmission = ''
    exterior_color = ''
    interior_color = ''
    liters: int = 0
    fuel_type = ''
    exterior_condition = ''
    interior_condition = ''
    drive_type = ''
    make_label: str = ""
    listed_as: str = ""

    price: int = 0

    # values
    value: tuple = (-1, 0)
    carfax_value: int = -1
    kbb_value: tuple = (-1, 0)
    edmunds_value: int = -1

    # analytics
    popularity: int = 0
    longevity: int = 11
    make_reliability: int = 0
    is_bad_model: int = 0

    fields_to_compress: list = []
    table: str = 'Cars'
    primary_key: str = 'id'
    unchanging_fields = ['ad_identifier', 'price', 'mileage']

    def __init__(self, item_id, identifier, mileage, year, make, model, trim, body, vin, title_type, exterior_color,
                 interior_color,
                 transmission, liters, fuel_type, exterior_condition, interior_condition, drive_type, cylinders,
                 door_amount, title, price, get_value=True):
        """
        This class creates a car object from the given fields and estimates its value if possible, 
        if it is not then the value is set to -1
        :param identifier: The ad identifier of the listing the car was pulled from
        :param mileage: The total mileage the car has traveled
        :param year: The year the car was manufactured
        :param make: The make of the car
        :param model: The model of the car
        :param trim: The trim of the car
        :param body: The body of the car
        :param vin: The vin number associated with the car
        :param title_type: The title type of the car
        :param exterior_color: The exterior color of the car
        :param interior_color: The interior color of the car
        :param transmission: The transmission type of the car
        :param liters: The amount of liters the car has
        :param fuel_type: The fuel type the car uses
        :param exterior_condition: The exterior condition of the car (poor - excellent)
        :param interior_condition: The interior condition of the car (poor - excellent)
        :param drive_type: The drive type of the car
        :param cylinders: The amount of cylinders the car has
        :param door_amount: The amount of doors the car has
        :param title: The listing title
        :param price: The amount of money wanted for the car
        """

        try:
            self.id = normalize(item=item_id, essential_field_name='car id')
            self.ad_identifier = normalize(identifier, True, essential_field_name='car ad_identifier')
            self.title = normalize(title)
            self.mileage = normalize(mileage, True, essential_field_name='car mileage')
            self.year = normalize(year, True, essential_field_name='car year')
            self.normalize_make(make)
            self.model = normalize(model)
            self.trim = normalize(trim)
            self.body = normalize(body)
            self.vin = normalize(vin).upper()
            self.normalize_title_type(title_type)
            self.exterior_color = self.normalize_color(exterior_color)
            self.interior_color = self.normalize_color(interior_color)
            self.normalize_transmission(transmission)
            self.liters = normalize(liters, True, False)
            self.normalize_fuel(fuel_type)
            self.exterior_condition = self.normalize_condition(exterior_condition)
            self.interior_condition = self.normalize_condition(interior_condition)
            self.normalize_drive_type(drive_type)
            self.cylinders = normalize(cylinders, True)
            self.door_amount = normalize(door_amount, True)
            self.price = normalize(price, True, True, 'car price')
            self._popularity_score()
            self._car_longevity()
            self._get_brand_reliability_rating()
            self._is_bad_model_year()
        except MissingEssentialDataException as e:
            raise e
        except Exception as e:
            raise BuildCarException(e, self.id)
        if get_value:
            try:
                self.get_carfax()
                return
            except Exception as e:
                try:
                    self.get_bluebook_value()
                except Exception as e:
                    return
        else:
            return

    def _set_value(self, value: int, accuracy: int):
        """
        this method sets the value and accuracy of the car
        :param value: the value estimated
        :param accuracy: the estimated accuracy of the value
        """
        self.value = (value, accuracy)

    def _fuzzy_model_string(self):
        """
        This is a helper function so the model of the car can easily be found with fuzzy screen selection
        :return: 
        """

        if self.not_none(self.model):
            model = str(self.model) + ' '
        else:
            model = ''
        if self.not_none(self.trim):
            trim = str(self.trim) + ' '
        else:
            trim = ''
        if self.not_none(self.body):
            body = str(self.body) + ' '
        else:
            body = ''
        if self.not_none(self.liters):
            liters = str(self.liters) + 'L '
        else:
            liters = ''
        if self.not_none(self.door_amount):
            door = str(self.door_amount) + 'D '
        else:
            door = ''
        car_label = f'{model}{trim}{body}{liters}{door}{self.title}'.replace('-', '')
        return car_label

    def _calculate_condition(self):
        """                                                                                                                                
        Conservatively calculates the condition of the car based off the KSL ads given                                                      
        interior condition and exterior condition                                                                                                                                                          
        :return string: a 'P' for poor, a 'F' for fair, a 'G' for good, and a 'E' for excellent                                                   
        """
        condition = floor((self.interior_condition.value + self.exterior_condition.value) / 2)
        if condition is 1:
            return 'P'
        elif condition is 2:
            return 'F'
        elif condition is 3:
            return 'G'
        else:
            return 'E'

            ########################################################################################################################
            ###                     The following are car value evaluation functions
            ########################################################################################################################

    def _popularity_score(self):
        """
        Calculates and sets the popularity score of the car. 0 is average, 100 is the best.
        This data comes from a list of the 20 most popular used cars from consumer reports
        """
        popularity_score = 0
        if self.make in Car_Data.popular_cars:
            model = self._normilized_model_string()
            popular_models = Car_Data.popular_cars[self.make]
            if model in popular_models:
                popularity_score = popular_models[model]
        self.popularity = popularity_score * 100

    def _is_bad_model_year(self):
        """
        Checks to see if the car is a bad model year based off consumer reports
        """
        model = self._normilized_model_string()
        if self.make in Car_Data.bad_car_models_by_year:
            makes_bad_models = Car_Data.bad_car_models_by_year[self.make]
            if model in makes_bad_models:
                bad_years = makes_bad_models[model]
                if int(self.year) in bad_years:
                    self.is_bad_model = 1
        self.is_bad_model = 0

    def _car_longevity(self):
        """
        Calculates and sets how long the car may run for, ~100 is the best score, 11 is the worst score.
        These statistics are base off of consumer data reports of the longest running cars 
        """
        percentage_over_200K = .65
        model = self._normilized_model_string()
        if self.make in Car_Data.durable_cars:
            makes_durable_models = Car_Data.durable_cars[self.make]
            if model in makes_durable_models:
                percentage_over_200K = makes_durable_models[model]

        self.longevity = round(percentage_over_200K * 17.5)

    def _get_brand_reliability_rating(self):
        """
        gets the brand reliabilty rating, 50 is normal, 100 is the best, 0 is the worst. 
        Based off information from consumer reports
        """
        brand_reliablity_rating = 50
        if self.make in Car_Data.make_reliability_rating:
            brand_reliablity_rating = Car_Data.make_reliability_rating[self.make]
        self.make_reliability = brand_reliablity_rating

    def get_bluebook_value(self):

        """                                                                                                                                
        This Function gets the kbb value of the car object and determines how accurate the value is. If there is a
        problem getting this value a KellyBlueBookException is raised.
        :raises KellyBlueBookException:
        """
        if self.year == '' or self.make == '' or self.make == Make.PROBLEM or self.mileage == '' or int(
                self.year) < 1992:
            self.kbb_value = (-1, 0)
            self.make_label = ''
            return
        try:
            driver = GW.Requester.create_chrome_driver()
            driver.get('http://www.autobytel.com/kelley-blue-book/')
            driver.maximize_window()
            GS.drop_down_select_and_wait(driver=driver,
                                         element_identifier='ValueType',
                                         label='Private Party',
                                         n_element_name='Year',
                                         backup_xpath='//select[@id="ValueType"]'
                                         )
            GS.drop_down_select_and_wait(driver=driver,
                                         element_identifier='Year',
                                         label=str(self.year),
                                         n_element_name='Make',
                                         backup_xpath='//select[@id="Year"]'
                                         )
            GS.drop_down_select_and_wait(driver=driver,
                                         element_identifier='Make',
                                         label=str(self.make.name),
                                         n_element_name='ModelId',
                                         backup_xpath='//select[@id="Make"]'
                                         )
            make_label, accuracy = GS.fuzzy_drop_down_select(driver=driver,
                                                             model_string=self._fuzzy_model_string(),
                                                             element_identifier='ModelId'
                                                             )
            GS.drop_down_select_and_wait(driver=driver,
                                         element_identifier='ModelId',
                                         label=str(make_label),
                                         backup_xpath='//select[@id="ModelId"'
                                         )
            GS.next_page(driver=driver,
                         el_locator=('xpath', '//input[@type="submit" and @value="Next"]'),
                         next_el_locator=('xpath', '//input[@id="Mileage"]')
                         )
            GS.enter_text(driver=driver,
                          locator=('name', 'Mileage'),
                          text=str(self.mileage)
                          )
            GS.enter_text(driver=driver,
                          locator=('name', 'PostalCode'),
                          text='84101'
                          )
            GS.select_correct_button(driver=driver,
                                     buttons_id='DriveTrain'
                                     )  # Need to search the paragraph for 4WD, AWD, 2WD and identify
            GS.select_correct_button(driver=driver,
                                     buttons_id='Transmission',
                                     button_text_wanted=str(self.transmission.name)
                                     )
            GS.select_correct_button(driver=driver,
                                     buttons_id='Engine'
                                     )  # Need to search the paragraph for Cycles and synonyms of the word as well as
            #  Liter etc.
            BB.select_condition_button(driver=driver,
                                       condition_value=self._calculate_condition()
                                       )
            GS.drop_down_select_and_wait(driver=driver,
                                         element_identifier='NextVehicle',
                                         label='Undecided',
                                         backup_xpath='//select[@id="NextVehicle"]'
                                         )
            GS.next_page(driver=driver,
                         el_locator=('xpath', '//input[@type="submit" and @value="Show My Car Value"]'),
                         next_el_locator=('xpath', '//div[@id="js-promo-popup"]/div/div[2]/div[1]/div[3]/p')
                         )
            price = BB.grab_price(driver=driver)
            driver.close()
            self.kbb_value = (price, accuracy)
            self._set_value(price, accuracy)
            self.make_label = make_label
        except Exception as e:
            raise GetBlueBookException(e, self.id)

    def get_carfax(self):
        """
        This function gets the carfax value of the vehicle based off the vin of the car. It also resets the 
        year, model, and trim of the car because carfax is more trustworthy on vin lookup than values entered in 
        on a listing
        :raises LoadCarFaxException - if the CarFaxPage cannot be loaded
        :raises CarFaxHistoryException - if Carfax does not have data on the car
        """
        if self.year > 1995 and self.vin != '':
            driver = None
            try:
                driver = GW.Requester.create_chrome_driver()
                driver.get('http://www.carfax.com/value/')
                driver.maximize_window()
                GS.enter_text(driver=driver,
                              locator=('name', 'zip'),
                              text='84101'
                              )
                GS.enter_text(driver=driver,
                              locator=('xpath', '//div[@id="vin-input"]/div/input'),
                              text=str(self.vin)
                              )
            except Exception as e:
                driver.quit()
                raise LoadCarFaxException(e, self.id)
            finally:
                try:
                    GS.next_page(driver=driver,
                                 el_locator=('xpath', '//input[@id="btnGetCarfax"]'),
                                 next_el_locator=(
                                 'css selector', 'div.vehicle-info__trade > div:nth-child(2) > h2.vehicle-info__value'),
                                 the_long_wait=False
                                 )

                    price = driver.find_element_by_css_selector(
                        'div.vehicle-info__trade > div:nth-child(2) > h2.vehicle-info__value').text
                    price = re.sub('[^0-9]', '', price)

                    main_info = driver.find_element_by_css_selector('h2.vehicle-info__vehicle-type').text
                    main_info_parts = main_info.split(' ')
                    trim = driver.find_element_by_css_selector(
                        'ul.vehicle-info__stats-list > li.vehicle-info__stat-item:nth-child(1)').text
                    driver.quit()
                    self.year = int(main_info_parts[0])
                    self.trim = str(trim).lower().strip().strip('trim: ')
                    price = int(price)
                    self.carfax_value = price
                    self._set_value(price, 100)
                    return
                except Exception as e:
                    no_history = driver.find_element_by_css_selector('p.error-page-text').text
                    driver.quit()
                    raise CarFaxHistoryException(e, self.ad_identifier)
        else:
            raise CarFaxHistoryException('The car being evaluated is too old for the databases', self.id)
            # condition = driver.find_element_by_css_selector('ul.vehicle-info__stats-list > li.vehicle-info__stat-item:nth-child(2)').text

            ########################################################################################################################
            ###                            The following are helper functions
            ########################################################################################################################


            ########################################################################################################################
            ###                     The following are car normalizing functions
            ########################################################################################################################

    def _normilized_model_string(self):
        """
        returns a normilized model type for the car as a string
        :return: 
        """
        return str(self.model).lower().replace(' ', '').replace('-', '')

    def normalize_fuel(self, fuel_type):
        """
        Sets the fuel_type as the correct FUEL enum type
        :param fuel_type: the fuel_type as a string
        """
        fuel_type = normalize(fuel_type).upper()
        fuel_type = fuel_type.replace(' ', '_')
        fuel_type = fuel_type.replace('-', '_')
        fuel_type = fuel_type.replace('4', 'FOUR')
        fuel_type = fuel_type.replace('2', 'TWO')
        try:
            self.fuel_type = Fuel_Type[fuel_type]
        except KeyError:
            self.fuel_type = Fuel_Type.OTHER
            if self.not_none(fuel_type) and fuel_type.upper() != 'NOT_SPECIFIED':
                print(f"unable to determine Drive Type - {fuel_type}")

    def normalize_make(self, make):
        """
        Sets the make as the correct MAKE enum type
        :param make: the make as a string
        """
        make = str(make).upper().replace(' ', '_').replace('-', '_')
        try:
            self.make = Make[make]
        except KeyError:
            if self.not_none(make) and make.upper() != 'NOT_SPECIFIED':
                print(f"un-identified make - {make}")
            self.make = Make.PROBLEM
            # Add the unidentified make to a list we can view somewhere

    def normalize_title_type(self, title):
        """
        sets the title of the car to the proper TITLE enum type
        :param title: the title as a string
        """
        title_type = normalize(title)
        title_type = title_type.upper()
        title_type = title_type.strip('TITLE')
        title_type = title_type.strip()
        if title_type.__contains__('REBUILT'):
            title_type = 'REBUILT'
        try:

            self.title_type = Title_Type[title_type]
        except KeyError:
            if self.not_none(title_type) and title_type.upper() != 'NOT SPECIFIED':
                print(f'not sure about this title type - {title_type}')
            self.title_type = Title_Type.PROBLEM

    def normalize_transmission(self, transmission):
        """
        sets the transmission as the proper Transmission type
        :param transmission: the transmission as a type
        """
        tranny = str(transmission).upper()
        try:
            self.transmission = Transmission[tranny]
        except KeyError:
            if self.not_none(tranny) and tranny.upper() != 'NOT SPECIFIED':
                print(f"not sure about this transmission value - {tranny}")
            self.transmission = Transmission.PROBLEM

    def normalize_condition(self, condition):
        """
        gets the condition as the proper Condition type
        :param condition: the condition
        :return: the proper condition enum
        """
        if condition == '' or condition == 'Not Specified':
            condition = 'fair'
        condition = str(condition).upper().replace(' ', '_')
        try:
            return Condition[condition]
        except KeyError:
            if self.not_none(condition) and condition.upper() != 'NOT SPECIFIED':
                print(f'unexpected condition - {condition}')
            return Condition.FAIR

    def normalize_color(self, color):
        """
        returns the color as the proper Color enum
        :param color: the color as a string
        :return: the proper color enum
        """
        try:
            return Color[color.upper()]
        except KeyError:
            if self.not_none(color) and color.upper() != 'NOT SPECIFIED':
                print(f'unsure about color - {color}')
            return Color.OTHER

    def normalize_drive_type(self, drive):
        """
        sets the drive_type as the proper Drive_Type enum
        :param drive: the drive type as a string
        """
        drive = str(drive).upper()
        drive = drive.replace(' ', '_')
        drive = drive.replace('-', '_')
        drive = drive.replace('4', 'FOUR')
        drive = drive.replace('2', 'TWO')
        try:
            self.drive_type = Drive_Type[drive]
        except KeyError:
            self.drive_type = Drive_Type.PROBLEM
            if self.not_none(drive) and drive.upper() != 'NOT_SPECIFIED':
                print(f"unable to determine Drive Type - {drive}")

            ########################################################################################################################
            ###                     The following function reprepresents the object as a dict for the database
            ########################################################################################################################

    def unique_where(self):
        return f"ad_identifier={self.ad_identifier} AND price={self.price} AND mileage={self.mileage}"

    def database_dict(self):
        """
        This returns a dictionary that represents the object. The instance variable are in the same order as the 
        collumn names in the database, they are also 
        
        :return: a dictionary item containing all needed fields to be uploaded to the database
        """
        if self.carfax_value > 0:
            value = self.carfax_value
        elif self.kbb_value[0] > 1:
            value = self.kbb_value[0]
        else:
            value = -1
        return {'id': DataBase_Object.normalize_for_varchar(self.id),
                'ad_identifier': self.ad_identifier,
                'title': DataBase_Object.normalize_for_varchar(self.title),
                'mileage': self.mileage,
                'year': self.year,
                'make': self.make.value,
                'model': DataBase_Object.normalize_for_varchar(self.model),
                'trim': DataBase_Object.normalize_for_varchar(self.trim),
                'body': DataBase_Object.normalize_for_varchar(self.body),
                'vin': DataBase_Object.normalize_for_varchar(self.vin),
                'title_type': self.title_type.value,
                'transmission': self.transmission.value,
                'exterior_color': self.exterior_color.value,
                'interior_color': self.interior_condition.value,
                'liters': DataBase_Object.normalize_for_varchar(self.liters),
                'fuel_type': self.fuel_type.value,
                'exterior_condition': self.exterior_condition.value,
                'interior_condition': self.interior_condition.value,
                'drive_type': self.drive_type.value,
                'make_label': DataBase_Object.normalize_for_varchar(self.make_label),
                'cylinders': DataBase_Object.normalize_for_varchar(self.cylinders),
                'popularity': self.popularity,
                'longevity': self.longevity,
                'make_reliability': self.make_reliability,
                'bad_model': self.is_bad_model,
                'value_accuracy': self.value[1],
                'value': self.value[0],
                'price': self.price
                }

    @staticmethod
    def generic_self():
        """
        Returns a generic Car
        :return: 
        """
        unique_id = str(uuid.uuid4())
        return Car(unique_id,
                   4444444,
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
                   'manual',
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

    @staticmethod
    def real_self(sql_connection):
        """
        returns a car object representing a record from the actual_database
        :return: 
        """
        obj = sql_connection.grab_listings(Car.table, limit=1)[0]
        return Car.from_database_json(obj)

    @staticmethod
    def from_database_json(JSON_dict):
        """
        Creates a moc car from database json data
        :param JSON_dict: 
        """
        car = Car.generic_self()

        car.id = JSON_dict['id']
        car.ad_identifier = JSON_dict['ad_identifier']
        car.mileage = JSON_dict['mileage']
        car.year = JSON_dict['year']
        car.make = Make(JSON_dict['make'])
        car.model = JSON_dict['model']
        car.trim = JSON_dict['trim']
        car.body = JSON_dict['body']
        car.vin = JSON_dict['vin']
        car.title_type = Title_Type(JSON_dict['title_type'])
        car.exterior_color = Color(JSON_dict['exterior_color'])
        car.interior_color = Color(JSON_dict['interior_color'])
        car.transmission = Transmission(JSON_dict['transmission'])
        car.liters = JSON_dict['liters']
        car.fuel_type = Fuel_Type(JSON_dict['fuel_type'])
        car.exterior_condition = Condition(JSON_dict['exterior_condition'])
        car.interior_condition = Condition(JSON_dict['interior_condition'])
        car.drive_type = Drive_Type(JSON_dict['drive_type'])
        car.cylinders = JSON_dict['cylinders']
        car.door_amount = 4
        car.title = JSON_dict['title']
        car.value = JSON_dict['value']
        car.price = JSON_dict['price']
        car._set_value(JSON_dict['price'], JSON_dict['value_accuracy'])
        car._popularity_score()
        car._car_longevity()
        car._is_bad_model_year()
        car._get_brand_reliability_rating()
        return car


from enum import Enum, unique


@unique
class Title_Type(Enum):
    """
    A title type enum that represents all the different kinds of car titles.
    The value of the enum is stored in the db to reduce the file size
    """
    PROBLEM = 0
    CLEAN = 1
    DISMANTLED = 2
    REBUILT = 3
    SALVAGE = 4
    TOTALED = 5


@unique
class Transmission(Enum):
    """
    A transmission type enum that represents all the different kinds of transmissions
    The value of the enum is stored in the db to reduce the file size
    """
    PROBLEM = 0
    AUTOMANUAL = 1
    AUTOMATIC = 2
    CVT = 3
    MANUAL = 4


@unique
class Color(Enum):
    """
    A color type enum that represents all the different kinds of colors
    The value of the enum is stored in the db to reduce the file size
    """
    OTHER = 0
    BEIGE = 1
    BLACK = 2
    BLUE = 3
    BRONZE = 4
    BROWN = 5
    CREME = 6
    GOLD = 7
    GRAY = 8
    GREEN = 9
    ORANGE = 10
    PINK = 11
    PURPLE = 12
    RED = 13
    SILVER = 14
    TAN = 15
    WHITE = 16
    YELLOW = 17


@unique
class Condition(Enum):
    """
    A condition type enum that represents the most common classifications of car condition (NADA, KBB, EDMUNDS)
    The value of the enum is stored in the db to reduce the file size
    """
    POOR = 0
    FAIR = 1
    GOOD = 2
    VERY_GOOD = 3
    EXCELLENT = 4


@unique
class Make(Enum):
    """
    A make type enum that represents all the different car makes
    The value of the enum is stored in the enum to reduce file size
    """
    PROBLEM = 0
    AC_CARS = 1
    AC_COBRA = 2
    AM_GENERAL = 3
    ACURA = 4
    ALFA_ROMEO = 5
    ALLARD = 6
    AMERICAN_MOTORS_AMC = 7
    ASTON_MARTIN = 8
    AUDI = 9
    AUSTIN = 10
    AUSTIN_HEALEY = 11
    AVANTI = 12
    BMW = 13
    BENTLEY = 14
    BERING = 15
    BLUE_BIRD = 16
    BUICK = 17
    CADILLAC = 18
    CHEVROLET = 19
    CHRYSLER = 20
    CITROEN = 21
    COLLINS = 22
    CROSLEY = 23
    DAEWOO = 24
    DAIHATSU = 25
    DATSUN = 26
    DESOTO = 27
    DELOREAN = 28
    DIAMOND_T = 29
    DODGE = 30
    EAGLE = 31
    EDSEL = 32
    ESSEX = 33
    FERRARI = 34
    FIAT = 35
    FISKER = 36
    FORD = 37
    FREIGHTLINER = 38
    GMC = 39
    GENESIS = 40
    GEO = 41
    HONDA = 42
    HUDSON = 43
    HUMMER = 44
    HYUNDAI = 45
    INFINITI = 46
    INTERNATIONAL = 47
    ISUZU = 48
    IVECO = 49
    JAGUAR = 50
    JEEP = 51
    JEEPSTER = 52
    JENSEN = 53
    KAISER = 54
    KENWORTH = 55
    KIA = 56
    LAMBORGHINI = 57
    LAND_ROVER = 58
    LEXUS = 59
    LINCOLN = 60
    LOTUS = 61
    MG = 62
    MV_1 = 63
    MACK = 64
    MARMON = 65
    MASERATI = 66
    MAXIM = 67
    MAYBACH = 68
    MAZDA = 69
    MCLAREN = 70
    MERCEDES_BENZ = 71
    MERCURY = 72
    MERKUR = 73
    MINI = 74
    MITSUBISHI = 75
    MORGAN = 76
    MORRIS = 77
    NASH = 78
    NISSAN = 79
    OLDSMOBILE = 80
    PACKARD = 81
    PETERBILT = 82
    PEUGEOT = 83
    PINZGAUER = 84
    PLYMOUTH = 85
    PONTIAC = 86
    PORSCHE = 87
    RAM = 88
    RENAULT = 89
    ROLLS_ROYCE = 90
    SAAB = 91
    SATURN = 92
    SCION = 93
    SEBRING_VANGUARD = 94
    SMART = 95
    STERLING = 96
    STUDEBAKER = 97
    SUBARU = 98
    SUNBEAM = 99
    SUZUKI = 100
    TESLA = 101
    TOYOTA = 102
    TRIUMPH = 103
    VPG = 104
    VOLKSWAGEN = 105
    VOLVO = 106


class Fuel_Type(Enum):
    """
    a fuel type enum to represent all the car fuel types
    The value is stored in the db to save file space
    """
    OTHER = 0
    BIO_DIESEL = 1
    BI_FUEL = 2
    COMPRESSED_NATURAL_GAS = 3
    DIESEL = 4
    ELECTRIC = 5
    ETHANOL = 6
    FLEX_FUEL = 7
    GASOLINE = 8
    HYBRID = 9
    LIQUIFIED_NATURAL_GAS = 10
    LIQUIFIED_PETROLEUM = 11


class Drive_Type(Enum):
    """
    a drive type enum to represent all the car drive types
    The value is stored in the db to save file space
    """
    PROBLEM = 0
    TWO_WHEEL_DRIVE = 1
    FOUR_WHEEL_DRIVE = 2
    AWD = 3
    FWD = 4
    RWD = 5


class Car_Data(object):
    """
    This class simply hold useful car data, such as how car color affects purchase rate, the most popular used cars,
    the most durable cars, and bad models of cars by year. This data helps decide car metrics that determine
    if it will be flipped or not
    """
    # hold car name and then car popularity in last two string parts 0-20
    popular_cars = {Make.HONDA: {'accord': 1, 'civic': .8, 'crv': .45},
                    Make.TOYOTA: {'camry': .95, 'corolla': .85, 'highlander': .3},
                    Make.NISSAN: {'altima': .9, 'maxima': .4},
                    Make.FORD: {'f150': .75, 'escape': .55, 'mustang': .5, 'fusion': .35, 'focus': .2},
                    Make.CHEVROLET: {'silverado': .7, 'impala': .65, 'malibu': .6, 'camaro': .15},
                    Make.BMW: {'3series': .25},
                    Make.DODGE: {'charger': .1},
                    Make.ACURA: {'tl': .5}
                    }

    # holds car percentage shited right once of percentage of cars on road > 200K miles
    # we rank average cars .6-.7
    durable_cars = {Make.FORD: {'expedition': 5.7, 'f150': 2.1, 'taurus': 1.9},
                    Make.TOYOTA: {'sequoia': 5.6, '4runner': 4.7, 'avalon': 2.6, 'tacoma': 2.5, 'camry': 1.5,
                                  'sienna': 1.5, 'prius': 1.1},
                    Make.CHEVROLET: {'suburban': 4.8, 'tahoe': 3.5, 'silverado': 2.0, 'impala': 1.5},
                    Make.GMC: {'yukon': 3.5, 'sierra': 2.0},
                    Make.HONDA: {'accord': 2.3, 'odyssey': 2.3, 'civic': 1.3},
                    Make.NISSAN: {'maxima': 1.5, 'quest': 1.1},
                    Make.DODGE: {'grandcaravan': 1.3},
                    Make.SUBARU: {'legacy': 1.6, 'outback': 1.4, 'forester': .9}
                    }

    average_days_on_market_by_color = {Color.ORANGE: 44.1,
                                       Color.YELLOW: 49.5,
                                       Color.GREEN: 45,
                                       Color.BROWN: 46.2,
                                       Color.RED: 49,
                                       Color.GRAY: 41.4,
                                       Color.WHITE: 42.8,
                                       Color.BLUE: 43.6,
                                       Color.BLACK: 42.1,
                                       Color.SILVER: 46.6,
                                       Color.BEIGE: 55.8,
                                       Color.GOLD: 42.6
                                       }
    bad_car_models_by_year = {Make.ACURA: {'tlx': {2015, 2016}},
                              Make.AUDI: {'a3': {2016}, 'a4': {2009, 2010}, 'q7': {2015}},
                              Make.BMW: {'1series': {2011}, '3series': {2008, 2009, 2010, 2011}, '4series': {20014},
                                         '5series': {2008, 2012}, 'x3': {2007, 2008, 2011}, 'x5': {2011, 2012}
                                         },
                              Make.BUICK: {'enclave': {2008, 2009, 2010, 2011}, 'lacrosse': {2007}, 'lucerne': {2008}},
                              Make.CADILLAC: {'ats': {2013, 2015}, 'escalade': {2015, 2016}, 'srx': {2013}},
                              Make.CHEVROLET: {'camaro': {2013}, 'colorado': {2015}, 'corvette': {2016},
                                               'cruze': {2011, 2012, 2013}, 'equinox': {2010, 2011}, 'hhr': {2009},
                                               'impala': {2010}, 'malibulimited': {2016},
                                               'silverado2500': {2011, 2012, 2015, 2016},
                                               'silverado3500': {2015}, 'sonic': {2012},
                                               'suburban': {2008, 2014, 2015, 2016},
                                               'tahoe': {2014, 2015, 2016}, 'traverse': {2009, 2010, 2011, 2013},
                                               'volt': {2016}
                                               },
                              Make.CHRYSLER: {'200': {2015}, '300': {2013, 2014},
                                              'town&country': {2008, 2009, 2010, 2011, 2012}},
                              Make.DODGE: {'challenger': {2015}, 'charger': {2014, 2015}, 'dart': {2013},
                                           'durango': {2012, 2013, 2015},
                                           'grandcaravan': {2008, 2009, 2010, 2011, 2012},
                                           'journey': {2012, 2013, 2015}, 'ram2500': {2007}
                                           },
                              Make.FIAT: {'500': {2012, 2013, 2015}, '500l': {2014}},
                              Make.FORD: {'escape': {2013}, 'expedition': {2012}, 'explorer': {2016},
                                          'f250': {2008, 2010, 2014},
                                          'f350': {2008, 2013}, 'fiesta': {2011, 2012, 2013, 2014},
                                          'focus': {2012, 2013, 2014, 2015, 2016},
                                          'mustang': {2015, 2016}, 'taurus': {2010}
                                          },
                              Make.GMC: {'acadia': {2007, 2008, 2009, 2010, 2011, 2012, 2013, 2014}, 'canyon': {2015},
                                         '2500': {2011, 2012, 2015, 2016}, '3500': {2015}, 'terrain': {2010, 2011},
                                         'yukon': {2014, 2015, 2016}, 'yukonxl': {2008, 2014, 2015, 2016}
                                         },
                              Make.HONDA: {'accordcrosstour': {2011}, 'civic': {2016}},
                              Make.HYUNDAI: {'genesis': {2016}, 'sonata': {2011}},
                              Make.INFINITI: {'jx35': {2013}, 'qx60': {2014}},
                              Make.JEEP: {'cherokee': {2014, 2015}, 'grandcherokee': {2011, 2013, 2014, 2016},
                                          'liberty': {2008},
                                          'renegade': {2015}, 'wrangler': {2015}
                                          },
                              Make.KIA: {'rondo': {2009}},
                              Make.LINCOLN: {'mkc': {2015, 2016}, 'mks': {2013}},
                              Make.MAZDA: {'mazda3': {2016}, 'mazda5': {2008}},
                              Make.MERCEDES_BENZ: {'cclass': {2015}, 'glclass': {2014, 2015}, 'mclass': {2011},
                                                   'gleclass': {2016},
                                                   'sclass': {2015}
                                                   },
                              Make.MINI: {'cooper': {2007, 2008, 2009, 2010, 2011, 2015}, 'countryman': {2012}},
                              Make.NISSAN: {'juke': {2012}, 'murano': {2016}, 'pathfinder': {2013, 2014},
                                            'rouge': {2014},
                                            'sentra': {2013}
                                            },
                              Make.RAM: {'1500': {2014, 2016}, '2500': {2012, 2014, 2015}},
                              Make.SUBARU: {'impreza': {2009}, 'outback': {2008}, 'wrx': {2015}},
                              Make.TESLA: {'models': {2014}, 'modelx': {2016}},
                              Make.TOYOTA: {'tacoma': {2016}},
                              Make.VOLKSWAGEN: {'beetle': {2014}, 'cc': {2010}, 'golf': {2010, 2015, 2016},
                                                'gti': {2012, 2013}, 'jetta': {2010, 2014, 2015, 2016},
                                                'passat': {2007, 2014},
                                                'tiguan': {2011, 2013}, 'touareg': {2014}
                                                },
                              Make.VOLVO: {'s60': {2015}, 'xc90': {2016}}
                              }

    make_reliability_rating = {Make.LEXUS: 86,
                               Make.TOYOTA: 78,
                               Make.BUICK: 75,
                               Make.AUDI: 71,
                               Make.KIA: 69,
                               Make.MAZDA: 68,
                               Make.HYUNDAI: 66,
                               Make.INFINITI: 62,
                               Make.BMW: 57,
                               Make.HONDA: 57,
                               Make.LINCOLN: 33,
                               Make.CADILLAC: 32,
                               Make.VOLKSWAGEN: 30,
                               Make.JEEP: 30,
                               Make.GMC: 29,
                               Make.TESLA: 28,
                               Make.DODGE: 28,
                               Make.CHRYSLER: 26,
                               Make.FIAT: 17,
                               Make.RAM: 16
                               }


class MissingEssentialDataException(ScraperException):
    """
    This exception is thrown when The scraper could not pull all the needed data
    """

    def __init__(self, fieldname):
        """
        Creates a CarFaxHistoryException
        :param ad_identifier: The ad identifier associated with the car without carfax vehicle history
        """
        message = f'The essential fieldname {fieldname} was missing'
        super().__init__('', message, MissingEssentialDataException)


class CarFaxHistoryException(ScraperException):
    """
    This exception is thrown when carfax doesnt have any history on the vehicle you are trying to look up
    """

    def __init__(self, e, ad_identifier):
        """
        Creates a CarFaxHistoryException
        :param ad_identifier: The ad identifier associated with the car without carfax vehicle history
        """
        message = f'CarFax has no history for {ad_identifier}'
        super().__init__(e, message, CarFaxHistoryException)


class LoadCarFaxException(ScraperException):
    """
    This exception is thrown when carfax doesn't load correctly
    """

    def __init__(self, e, ad_identifier):
        message = f'Unable to load Carfax for {ad_identifier}'
        super().__init__(e, message, LoadCarFaxException)


class BuildCarException(ScraperException):
    """
    This exception is thrown when there is an issue building a car from the inputted values
    """

    def __init__(self, e, ad_identifier):
        """
        builds the BuildCarException
        :param ad_identifier: the ad identifier associated with the car that had issues being built
        :return: 
        """
        message = f'Unable to build Car with {ad_identifier}'
        super().__init__(e, message, BuildCarException)


class GetBlueBookException(ScraperException):
    """
    This exception is thrown when there is an issue getting the kbb value of the car
    """

    def __init__(self, e, ad_identifier):
        """
        builds the GetBlueBookException
        :param ad_identifier: the ad identifier associated with the car that had issues getting a KBB value
        :return: 
        """
        message = f'Unable to get KBB value for Car with {ad_identifier}'
        super().__init__(e, message, GetBlueBookException)
