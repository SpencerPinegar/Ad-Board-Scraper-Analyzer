import os
import datetime
import errno
from time import gmtime, strftime

class Logger:



    log_file_path = ''

    def __init__(self, project_primary_file_path):

        self.log_file_path = os.path.join(project_primary_file_path, 'Logs')
        Logger.make_dir(self.log_file_path)




    def log(self, input):
        """
        logs an input into the at the current time
        :param input:
        :return:
        """
        my_datetime = strftime("%Y-%m-%d %H:%M:%S", gmtime()).split(' ')
        current_text = os.path.join(self.log_file_path, my_datetime[0])
        time_stamp = my_datetime[1]
        Logger.edit_file(current_text, input + ' ' + time_stamp + '\n')


    @staticmethod
    def edit_file(relative_file_path, input):
        """
        Tries to open and edit an existing file,
        if it cannot find the file it creates it and is ready to edit
        :param relative_file_path: The file path relative to the file you are calling
                this function from, use os.path.dirname(__file__) to get it
        :return: A an open editable file object
        """
        file = None
        try:
            file = open(relative_file_path, 'a')
            with file as the_file:
                the_file.write(input)
        except FileNotFoundError:
            file = open(relative_file_path, 'w')
            with file as the_file:
                the_file.write(input)


    @staticmethod
    def make_dir(directory: str):
        """
        Makes a directory if one doesnt exist
        :param directory: The filepath of the directory to be created
        :return:
        """

        try:

            dir = os.path.dirname(__file__)
            filename = os.path.join(dir, directory)
            os.makedirs(filename)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise e



