
import pymysql
from Messenger_Pigeon.Objects.Database_Objects.database_object import DataBase_Object
from Messenger_Pigeon.Objects.Database_Objects.database_error import ScraperException


##BUILDING NEW WEBSERER TO HOLD DATA
#           #Username:
#           #Password:369Pinegar

class SQL_Connection(object):
    # Database Properties
    host = 'localhost'  # the host address of the MySQL server
    user = 'user'  # the user you are logging in as
    password = 'password'  # the password to be used
    db_name = 'db'  # the MySQL db you are connecting too
    connection_buffer = True  # Turn False for large amount of data, True is more memory expensive
    as_dict = True  # recieve the information as a dictionary

    connection = None  # the connection to the server
    cursor_type = None  # the cursor to retrieve and interact with the server

    sql_query = ''  # the current sql_query
    credentials = None  # the credentials to log in
    query_return = None  # the latest sql query execution return

    def __init__(self, host, user, password, db_name, connection_buffer=True, as_dict=True):
        """
        This is constructor of the sql connection object, it creates a connection object
        but does not open it.
        """
        self.set_cursor(connection_buffer=connection_buffer, as_dict=as_dict)
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name

    def open_connection(self):
        """
        opens a connection with the mySQL server
        :return: 
        """
        self.connection = pymysql.connect(host=self.host,
                                          user=self.user,
                                          password=self.password,
                                          db=self.db_name,
                                          cursorclass=self.cursor_type)

    def remove_object(self, the_object):
        """
        Deletes an object, returning a boolean value based on whether or not the object was found and removed
        :param the_object: the dict representation of the object to be deleted
        :return bool: a boolean of whether the object was found and removed or not
        """
        self.is_sql_compatible(the_object)
        self.clear_query()
        self.sql_query = f"DELETE FROM {the_object.table} WHERE {the_object.unique_where()};"
        self.execute()
        return self.modified()


    def add_object(self, the_object, increment = True):
        """
        adds an object to the database. If it is a new one, it adds it to the database, if it exists it increments it.
        
        :param the_object: the object you want to add to the database 
        :param increment: If you want to increment the object if it already exists
        :return: A boolean true if the object was added or incremented, else false
        """
        self.is_sql_compatible(the_object)
        self.clear_query()
        if not self.is_duplicate(the_object):
            return self.post_object(the_object)
        elif increment:
            return self.increment_object(the_object)
        else:
            return False




    def increment_object(self, the_object):
        """
        Increments the data_base object in the database if possible, returning true if the object was found and incremented
        :param the_object: the object to be incremented
        :return bool: Whether the object was found and incremented
        """
        self.is_sql_compatible(the_object)
        self.clear_query()
        if the_object.field_to_increment == None:
            return False
        new_val = getattr(the_object, the_object.field_to_increment) + 1
        self.sql_query = f"UPDATE {the_object.table} SET {the_object.field_to_increment} = {new_val} WHERE {the_object.unique_where()};"
        self.execute()
        return self.modified()


    def close_connection(self):
        """
        closes the current connection with the mySQL server
        """
        try:
            self.connection.close()
        finally:
            return

    def grab_listings(self, table, where=None, limit=None):
        """
        This method grabs a listing(s) from the table given
        :param where: A MYSQL where clause as string ex: 'column_name < 0'
        :param limit: the total amount of listing to be returned - int
        :param table: the MySQL table you want to work with
        :return: a list of the table listings as dictionaries
        """
        self.clear_query()
        self.sql_query = f"SELECT * FROM {table} "
        if where != None:
            self.sql_query = self.sql_query + f"WHERE {where} "
        if limit != None:
            self.sql_query = self.sql_query + f"LIMIT {limit}"
        self.sql_query = self.sql_query.strip() + ';'
        self.execute(return_item=True)
        return self.query_return


    def grab_listing(self, table, where=None):
        """
        Grabs a single listing based off a table and mySQL where statement
        :param table: 
        :param where: 
        :return: 
        """
        return self.grab_listings(table, where, limit=1)[0]


    def is_duplicate(self, the_object):
        """
        This method searches the database for exisisting object based on its primary key, returning true if it 
        the primary key already exists within the database, and false if it does not. You can put in a custom
        defitinion of duplicate as well with the where param
        :param the_object: The object who's instance we are checking for
        :return: A bool - true if object is already represented in the db
        """
        SQL_Connection.is_sql_compatible(the_object)
        where = the_object.unique_where()
        self.clear_query()
        self.sql_query = f"SELECT * FROM {the_object.table} WHERE {where}"
        self.execute()
        return self.modified()

    def modify_object_attribute(self, the_object, key, value):
        """
        modifies a collumn attribute of an object
        :param the_object: The object you want to modify
        :param key: the key you want to modify 
        :param value: the new value of the key
        :return: True if the object was found and modified, else false.
        :raises ObjectArgumentException, IllegalObjectException
        """

        SQL_Connection.is_sql_compatible(the_object)
        self.clear_query()

        if key in self.table_keys(the_object.table):
            if key in the_object.unchanging_fields:
                raise UnmutableKey(key)
            self.sql_query = f"UPDATE {the_object.table} SET {key}='{value}' WHERE {the_object.unique_where()};"
            self.execute()
        else:
            raise KeyArgumentException(key, the_object.table)

    def modify_table_attribute(self, table_name, key, value, where=None, value_is_string=False):
        """
        modifies a collumn attribute of an object
        :param table_name: The table you want to modify
        :param key: the key you want to modify 
        :param value: the new value of the key
        :return: True if the object was found and modified, else false.
        :raises TableArgumentException, KeyArgumentException
        """
        self.clear_query()
        self.valid_key(table_name, key)

        self.sql_query = f"""UPDATE {table_name} SET {key}="""
        if value_is_string:
            self.sql_query = self.sql_query+f"'{value}'"
        else:
            self.sql_query = self.sql_query + f"{value}"
        if where != None:
            self.sql_query = self.sql_query + f' WHERE {where}'
        self.sql_query = self.sql_query+';'
        self.execute()
        return self.modified()


    def post_object(self, the_object, credentials=None):
        """
        This method takes a object and posts it into a sql database. The object's instance variable names must match
        the names of the fields in the MYSQL database and the type must be correct as well

        :param credentials: Tuple ('username', 'password') - Any authentication that is required to interact with the db
        :param the_object: The object to be entered into the table
        """
        SQL_Connection.is_sql_compatible(the_object)

        self.clear_query()
        self.credentials = credentials
        self.sql_query = f"INSERT INTO {the_object.table} {SQL_Connection.sqlify_object_for_upload(the_object=the_object)};"
        self.execute()
        return self.modified()

    def post_objects(self, the_objects: list, creditials=None):
        """
        posts a list of object to the database
        :param the_objects: the object to post - they must all be the same class
        :param creditials: the credentials needed to make the command
        """

        if len(the_objects) == 0:
            return

        SQL_Connection.is_sql_compatible(the_objects[0])
        the_keys = SQL_Connection._get_object_keys(the_objects[0])
        self.sql_query = f"INSERT INTO {the_objects[0].table} {the_keys} Values"

        for an_object in the_objects:
            SQL_Connection.is_sql_compatible(an_object)
            self.sql_query = self.sql_query + SQL_Connection.sqlify_object_for_upload(an_object, True) + ','

        self.sql_query = self.sql_query.trim(',') + ';'
        self.execute()
        if len(the_objects) != self.query_return:
            print(f"{len(the_objects) - self.query_return} where not uploaded")


    def set_cursor(self, connection_buffer=None, as_dict=None):
        """
        Sets the cursor type based on connection type
        """
        # checks input to see if buffer attributes were entered in.
        if isinstance(connection_buffer, bool):
            self.connection_buffer = connection_buffer
        if isinstance(as_dict, bool):
            self.as_dict = as_dict

        # sets the buffer type based on its attributes
        if self.connection_buffer and self.as_dict:
            self.cursor_type = pymysql.cursors.DictCursor
        elif self.as_dict:
            self.cursor_type = pymysql.cursors.SSDictCusor
        elif self.connection_buffer:
            self.cursor_type = pymysql.cursors.SSCursor
        else:
            self.cursor_type = pymysql.cursors.Cursor

    def table_names(self):
        """
        Gets a list of all tables the database can view currently
        :return: list of table names ass trings
        """
        self.clear_query()
        self.sql_query = "SELECT table_name FROM information_schema.tables;"
        self.execute(return_item=True)
        data = []
        for json in self.query_return:
            data.append(json['table_name'])
        self.clear_query()
        return data


    def table_keys(self, table):
        """
        Gets a list of all table keys that are editable from a table name
        :param table: The name of the table
        :return: the return 
        """
        self.clear_query()
        self.sql_query = f"SHOW COLUMNS FROM {table}"
        self.execute(return_item=True)
        keys = []
        for json in self.query_return:
            if json['Extra'].__contains__('VIRTUAL') or json['Extra'].__contains__('PERSISTENT'):
                continue
            keys.append(json['Field'])
        self.clear_query()
        return keys

    def valid_key(self, table, key):
        self.valid_table(table)
        if key in self.table_keys(table):
            return
        else:
            raise KeyArgumentException(key, table)



    def valid_table(self, table):
        if table in self.table_names():
            return
        else:
            raise TableArgumentException(table)




    def modified(self):
        """
        checks to see if there was a sql response. If there was returns true, if not
        returns falls. The clear query method must be used prior to word for this
        method to return accurate information
        :return: Bool - True if the sql statement modified a object in a table
        """
        if self.query_return >= 1:
            return True
        else:
            return False


    def clear_query(self):
        """
        Clears the objects sql_query
        """
        self.sql_query = ''
        self.query_return = -1

    def execute(self, open_con=False, close_con=False, return_item=False):
        """
        Executes the current sql query with the current credentials.
        :param open_con: True if you want to open a connection before the call
        :param close_con: True if you close the connection after the call
        :param return_item: True if you are trying to retrieve objects from db
        """
        #if open_con:
         #   self.open_connection()

        try:
            with self.connection.cursor() as cursor:
                # Create a new record
                if self.credentials != None:
                    self.query_return = cursor.execute(self.sql_query, self.credentials)
                else:
                    self.query_return = cursor.execute(self.sql_query)
                if return_item:
                    self.query_return = cursor.fetchall()
                self.connection.commit()
        except Exception as e:
            raise ExecutionException(e, self.sql_query)
        finally:
            if close_con:
                self.close_connection()

    @staticmethod
    def is_sql_compatible(the_object):
        """
        Checks the object to see if it is compatible with teh sql_connection object
        :param the_object: the item whos compatibility is being test
        :raises: ValueError - if object is not compatible with sql_connection
        """
        if not issubclass(type(the_object), DataBase_Object):
            raise IllegalObjectException(the_object)

    @staticmethod
    def sqlify_object_for_upload(the_object, just_values=False):
        """
        Takes in an object and returns a partial SQL statement that represents the object's keys and 
        values (compressed if included in values_to_compress)
        
        :param the_object: object - The object you want the SQL query for
        :param just_values: Bool - True if you would only want the values in SQL format
        :return: String - A partial SQL statement representing the object
        """
        SQL_Connection.is_sql_compatible(the_object)
        upload_data_dict = the_object.database_dict()
        # for key in the_object.fields_to_compress:
        #     try:
        #         uncompressed_value = upload_data_dict[key]
        #         compressed_value = SQL_Connection.compress_string(uncompressed_value)
        #         upload_data_dict[key] = compressed_value
        #     except KeyError:
        #         raise ValueError(
        #             f'unable to find {key} in {type(the_object).__name__} database dict. Modify the fields_to_compress instance variable'
        #             f'or the database_dict method so key names align')
        dict_values_tuple = tuple(upload_data_dict.values())
        if just_values:
            return f'\n{dict_values_tuple}'
        else:
            dict_key_tuple = SQL_Connection._get_object_keys(the_object)
            return f'{dict_key_tuple} \nVALUES {dict_values_tuple}'

    @staticmethod
    def _get_object_keys(the_object):
        """
        returns the objects keys in mySQL key format (key_name1, key_name2, key_name3)
        :param the_object: the object whos keys we want
        :return: the keys in mySQL format as string
        """
        upload_data_dict = the_object.database_dict()
        return str(tuple(upload_data_dict.keys())).replace("'", "")

    # @staticmethod
    # def compress_string(string):
    #     """
    #     compresses a given string into bytes
    #     :param string: the string to be compressed
    #     :return: a compressed byte string of the original
    #     """
    #     string = str(string)
    #     return zlib.compress(string.encode('utf-8'))
    #
    # @staticmethod
    # def decompress_string(cmpstr):
    #     """
    #     decompresses a byte string
    #     :param cmpstr: the byte string to be decompressed
    #     :return: the decompressed string
    #     """
    #     return zlib.decompress(cmpstr).decode('utf-8')

class UnmutableKey(ScraperException):

    def __init__(self, keyname):

        message = f'The key - {keyname} - cannot be changed when it has been set'
        super().__init__('', message, UnmutableKey)


class TableArgumentException(ScraperException):
    """
    this exception is raised when the connection/cursor has issues executing the current mySQL Query
    """
    def __init__(self, table_name):
        """
        builds the Exception
        """
        message = f'The MySQL database does not have a table name {table_name} to modify'

        super().__init__('', message, TableArgumentException)


class IllegalObjectException(ScraperException):
    """
    this exception is raised when the connection/cursor has issues executing the current mySQL Query
    """
    def __init__(self, the_object):
        """
        builds the Exception
        """
        message = f'The object class you tried to upload  -- {type(the_object).__name__} -- does not inherit ' \
                  f'from the database_object class - it must also have a table in the KSL_Webscraper database'

        super().__init__('', message, IllegalObjectException)

class KeyArgumentException(ScraperException):
    """
    this exception is raised when a user tries to modify an invalid field in an object
    """
    def __init__(self, attribute, table):
        """
        builds the Exception
        """
        message = f'You tried to modify an unidentified attribute. The {table} does not have an attribute name {attribute}'

        super().__init__('', message, KeyArgumentException)

class ExecutionException(ScraperException):
    """
    this exception is raised when the connection/cursor has issues executing the current mySQL Query
    """
    def __init__(self, e, mySQLQuery):
        """
        builds the Exception
        :param mySQLQuery:  the query that could not be executed
        """
        message = f'Could not execute SQL query of {mySQLQuery}'
        super().__init__(e, message, ExecutionException)

# fake_unproccessed = unproccessed_listing.Unprocessed_Listing('1234566', 'myfakeurl')
#     # seller.Seller(seller_id=1234567, name='Frank Ocean', member_since='Apr 2017', phone='(801) 772-1913', private_seller=True)
# fake_connection = SQL_Connection(host='localhost', user ='root', password='', db_name='KSL_WebScraper')
# fake_connection.post_object(fake_unproccessed)
