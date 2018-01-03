import requests
from selenium import webdriver
import bs4.element as bs4_class
from bs4 import BeautifulSoup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import asyncio
#from proxybroker import Broker
import random

"""
This class contains static generic functions that are used when scraping webpages
"""


class Requester(object):
    proxy_urls: list = []
    proxy_ip: bool = True
    chrome_path = r'../Driver_Binaries/chromedriver'



    def __init__(self, proxy_ip = True):
        self.proxy_ip = proxy_ip
        self.proxy_urls = []
        if proxy_ip:
            self.load_proxies()





    def get_website_object(self,
                           base_url,
                           url_params=None,
                           doc_parser='lxml',
                           user_agent=None,
                           javascript_required=False,
                           xpath_to_look_for=None,
                           ):
        """This function creates a beautiful soup object from a url and returns it if possible                                                   
            or else this function just returns a None object                                                                                     
    
        :param xpath_to_look_for: The xpath of an expected object on the page
        :param javascript_required: If the website only allows entry if javascript is enabled
        :param user_agent: The user headers associated with the request
        :param base_url: The base URL of the site you would like to search - String                                                              
        :param url_params: The params (searching critera from URL in dict form - see BeautifulSoup4 Documentation)                               
            of the base URL you would like to see - Dict of Strings                                                                              
        :param doc_parser: The parser you would like to use to within the beautifulsoup object - String                                          
        :return: A beautifulsoup object of the given url and params created with specified parser - BeautifulSoup                                
            will return None if the object cannot be created                                                                                     
        """
        proxy_dict = {}
        proxy = {}
        if self.proxy_ip:
            proxy = self.get_proxy()
            if proxy[4] == ':':
                proxy_dict = {'http': proxy}
            else:
                proxy_dict = {'https': proxy}
        if url_params is None:
            url_params = {}
        if user_agent is None:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.2 (KHTML, like Gecko) Chrome/22.0.1216.0 Safari/537.2'}
        else:
            headers = {'User-Agent': str(user_agent)}


        if self.proxy_ip:
            website = requests.get(base_url, params=url_params, headers=headers, proxies=proxy_dict)
        else:
            proxy = None
            website = requests.get(base_url, params=url_params, headers=headers)

        if website.status_code != requests.codes.ok:
            print('URL: "{}" encountered error: "{}"'.format(website.url, website.status_code))
            # Need to track these in a dictionary object and store them
            website.raise_for_status()
            raise InvalidBaseURLException(website.url, website.status_code)
        else:
            if javascript_required:

                if self.proxy_ip:
                    driver = self.create_chrome_driver(ip=proxy)
                else:
                    driver = self.create_chrome_driver()
                try:
                    driver.get(website.url)
                except:
                    driver.get(website.url)
                if xpath_to_look_for != None:
                    try:
                        wait = WebDriverWait(driver, 10)
                        element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_to_look_for)))
                    except:
                        raise InvalidBaseURLException(website.url, website.status_code)
                beutifulsoup_website = BeautifulSoup(driver.page_source, doc_parser)

                driver.close()
            else:
                beutifulsoup_website = BeautifulSoup(website.content, doc_parser)
            return beutifulsoup_website

    def get_proxy(self):
        """
        Grabs and removes proxy from list, if proxy_url's are empty it reloads them.
        :return: 
        """
        if len(self.proxy_urls) == 0:
            self.load_proxies()
        proxy = random.choice(self.proxy_urls)
        self.proxy_urls.remove(proxy)
        proxy = proxy.strip('\n')
        return proxy


    async def save(self, proxies):
        """Save proxies to a file."""

        while True:
            proxy = await proxies.get()
            if proxy is None:
                break
            proto = 'https' if 'HTTPS' in proxy.types else 'http'
            row = '%s://%s:%d\n' % (proto, proxy.host, proxy.port)
            self.proxy_urls.append(row)

    def load_proxies(self):
        """
        Asyncronously grabs proxies and saves them to the proxy_urls list in a usable string format
        """
        self.proxy_urls = []
        proxies = asyncio.Queue()
        #broker = Broker(proxies)
        #tasks = asyncio.gather(broker.find(types=['HTTP', 'HTTPS'], limit=10),
        #                       self.save(proxies))
        #loop = asyncio.get_event_loop()
        #loop.run_until_complete(tasks)

    @staticmethod
    def grab_attribute(_attribute,
                       beautifulsoup_tag,
                       spacing_index=-1,
                       chars_to_strip=[],
                       default_to_string=False,
                       ):
        """A method that grabs an attribute from a beautifulsoup tag object                                                                      
        while handling potential failures                                                                                                        
    
        :param _attribute: The name of the attribute in the beautifulsoup tag dict - String (url, text, etc.)                                    
        :param beautifulsoup_tag: The tag object the attribute is to be gotten from - beautifulsoup tag                                          
        :param spacing_index: The index position of the attribute if in a string separated by spaces -1 indicates                                
        :param chars_to_strip: A list of any extra chars that needed to be removed - List                                                        
        :param default_to_string: True if you want the value to be returned as a string - Boolean                                                
        :return: The attribute as the correct primitive type                                                                                     
        """
        try:
            if _attribute == 'text':
                attribute = beautifulsoup_tag.text
            else:
                attribute = beautifulsoup_tag[_attribute]
        except:
            return -1
        attribute = str(attribute)
        attribute = attribute.strip()
        for char in chars_to_strip:
            attribute = attribute.replace(char, '')
        if spacing_index != -1:
            list_with_attribute = attribute.split(' ')
            if len(list_with_attribute) > 1:
                attribute = list_with_attribute[spacing_index]
        if attribute.isdigit() and default_to_string != True:
            return int(attribute)
        else:
            return str(attribute)

    @staticmethod
    def is_tag(tag):
        """
        Checks to make sure only tags are taken
        :param tag: the tag whose type is being ensured
        :return: True if the tag is a Tag type
        """
        return type(tag) == bs4_class.Tag

    @staticmethod
    def create_chrome_driver(ip: str = None, headless: bool = True):
        """
        This function creates a chrome driver to be used with selenium
        :param ip: the ip we are using to hide our identity
        :param headless: If the browser should be headless or not - headless is faster but invisiible
        :return: webdriver.Chrome() object - used to navigate to websites
        """

        options = webdriver.ChromeOptions()
        if headless:
            options.add_argument('headless')
        if ip != None:
            options.add_argument(f'--proxy-server={ip}')
        browser = webdriver.Chrome(Requester.getChromePath(), chrome_options=options)
        return browser


    @staticmethod
    def getChromePath():
        import os
        script_dir = os.path.dirname(__file__)  # <-- absolute dir the script is in
        rel_path = Requester.chrome_path
        return os.path.join(script_dir, rel_path)


class InvalidBaseURLException(Exception):
    """
    This exception is raised when we are unable to access a page
    """

    def __init__(self, url, response_code):
        """
        creates exception
        :param url: The url of the page that could not be loaded
        :param response_code: HTTP response of the websie
        """
        message = f'Unable to load home page for URL {url} with the response code: {response_code}'
        super(InvalidBaseURLException, self).__init__(message)



