from abc import ABC, abstractmethod


class DataBase_Object(ABC):
    """
    This is an abstract class that must be inherited by any object that is being uploaded into a MySQL server
    using the sql_connection class
    """

    fields_to_compress = []  # The fields of the object that need to be compressed
    table: str = ''  # The table the object will be uploaded too
    primary_key: str = ''  # the primary key of the object and table
    field_to_increment: str = None  # If the object is being accessed and this needs to be tracked - this is the field
    unchanging_fields = []

    @abstractmethod
    def database_dict(self):
        """
        This method must be implemented by any object inherting from DataBase Object
        It should return a dictionary with the values as strings of the database field names, and values as the
        values to be uploaded (types need to be correct). This dictionary should be in the same order as the 
        table.
        :return: dict(string, value)
        """
        raise NotImplementedError(
            "Override this method in your class so it returns a dictionary with keys identical to the database")

    def not_none(self, item):
        """
        Checks if an item is an empty string, returning true if it is not.
        :param item: the string item to be checked
        :return: bool
        """
        if str(item) == '':
            return False
        return True

    @staticmethod
    def normalize_for_varchar(word: str):
        """
        Takes a value and normalizes it so it can be uploaded for a varchar 
        :param str: The string value that will be held in mySQL as a varchar
        :return: 
        """
        string = str(word)
        return string.encode('utf-8', 'ignore').decode('utf-8').replace("'", '')

    @abstractmethod
    def unique_where(self):
        """
        Returns a MySQL string that is able to identify if the object is unique. All non key string values - VARCHAR 
            values in mySQL - must be surrounded in /' characters. Do not include 'WHERE' or a preceding space in this
            string
            
            Ex: 
                return f"objects_unique_identifier_instance_variable_name='{corresponding_string_value}'"
        :return: 
        """
        raise NotImplementedError(
            "Override this method in your class so it returns a dictionary with keys identical to the database")

    @staticmethod
    def from_database_json(JSON_dict):
        """
        Returns an object based off database values

            Ex: 
                car_JSON_data = connection_object.get_listings('Cars')[0]
                car_object = Car.from_database_json(car_JSON_data_
        :param JSON_dict: Dict representing database object
        :return: 
        """
        raise NotImplementedError(
            "Override this method in your class so it returns a dictionary with keys identical to the database")

    @staticmethod
    def generic_self():
        """
        Returns a generic version of the object for testing.
            EX:
                generic_class_object = ClassName.generic_self()
        :return: generic database_object
        """
        raise NotImplementedError(
            "Override this method in your class so it returns a dictionary with keys identical to the database")


    @staticmethod
    def real_self(sql_connection):
        """
        Returns a an object with real values from the database for testing
        
            EX:
                real_database_data_object = ClassName.real_self()
        :return: 
        """
        raise NotImplementedError(
            "Override this method in your class so it returns a dictionary with keys identical to the database")


