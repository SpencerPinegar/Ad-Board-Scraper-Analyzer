from Messenger_Pigeon.Objects.ksl_scraper import KSL_SCRAPER
from Messenger_Pigeon.Objects.Database_Objects.database_error import ScraperException

required_keys = ['Range', 'Number_To_Notify', 'Max_Pages', 'Proxy_IP', 'DB_Host', 'DB_User', 'DB_Password', 'DB_Name']

def main():

    settings = get_settings()
    _range = settings['Range']
    number_to_notify = settings['Number_To_Notify']
    proxy_ip = settings['Proxy_IP']
    db_host = settings['DB_Host']
    db_user = settings['DB_User']
    db_password = settings['DB_Password']
    db_name = settings['DB_Name']
    max_pages = int(settings['Max_Pages'])

    the_scraper = KSL_SCRAPER(_range=_range,
                              number_to_notify=number_to_notify,
                              proxy_ip=proxy_ip,
                              db_host=db_host,
                              db_user=db_user,
                              db_password=db_password,
                              db_name=db_name
                              )
    while True:
        try:
            the_scraper.work(max_pages)
        except Exception as e:
            print(str(e))
            new_error = ScraperException(e, 'Main level exception', ScraperException)
            try:
                the_scraper.data_base.add_object(new_error)
                the_scraper = KSL_SCRAPER(_range=_range,
                                      number_to_notify=number_to_notify,
                                      proxy_ip=proxy_ip,
                                      db_host=db_host,
                                      db_user=db_user,
                                      db_password=db_password,
                                      db_name=db_name
                                      )
            except Exception as e:
                the_scraper.notifier.send_message(the_scraper.to_number, "THE SCRAPER IS SHUTTING DOWN!!!! "
                                                                         f"Cause:: {str(e)}")
                exit(-1)


def get_settings():
    """
    Reads the settings file and
    :return:
    """
    settings = {}
    try:
        with open(r'Messenger_Pigeon/SETTINGS') as settings_file:
            for line in settings_file.readlines():
                if line.__contains__('::'):
                    key_value = line.split('::')
                    key = key_value[0]
                    value = key_value[1].split("'")[1]
                    settings[key] = value
        for key in required_keys:
            if not settings.keys().__contains__(key):
                raise Exception()
        return settings
    except Exception as e:
        raise Exception("There was an issue reading the SETTINGS.txt file.")





if __name__ == '__main__':
    main()
