from Messenger_Pigeon.Objects.ksl_scraper import KSL_SCRAPER
from Messenger_Pigeon.Objects.Database_Objects.database_error import ScraperException


def main(_range,
         number_to_notify,
         max_pages,
         proxy_ip=False,
         db_host='localhost',
         db_user='root',
         db_password='',
         db_name='KSL_WebScraper'):
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
            the_scraper.data_base.add_object(new_error)
            the_scraper = KSL_SCRAPER(_range=_range,
                                      number_to_notify=number_to_notify,
                                      proxy_ip=proxy_ip,
                                      db_host=db_host,
                                      db_user=db_user,
                                      db_password=db_password,
                                      db_name=db_name
                                      )

if __name__ == '__main__':
    main(_range=50, number_to_notify=8016692828, max_pages=3, proxy_ip=False)
