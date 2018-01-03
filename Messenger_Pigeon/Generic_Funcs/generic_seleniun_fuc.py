from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from time import sleep
import re
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from Messenger_Pigeon.Objects.Database_Objects.database_error import ScraperException

"""
This page contains static generic functions to run a selenium webdriver
"""

def drop_down_select_and_wait(backup_xpath, driver, element_identifier, label, n_element_name=None, by=By.NAME):
    """                                                                                                                                
    This function is a helper function for the get_bluebook_value function                                                             
    It is used to select an item with selenium from a dropdown menu                                                                    
    :param backup_xpath: A backup used only if the element associated with the element_identifier cant be found
    :param driver: The selenium driver object to be preforming the operation                                                           
    :param element_identifier: The nameof the field you want selected                                                                        
    :param label: The text on the drop down menu you want to click
    :param n_element_name: The next element that needs to be submitted
    :raises: FrozenSelectorException - if the function is unable to select the element it needs or if the 
                                        next element never becomes enabled
    """
    """FIX THIS SHIT SO WE KNOW WHAT IS CAUSING WHAT AND WE DON"T HAVE PROBLEMS"""
    label_to_use = ''
    try:
        the_wait = WebDriverWait(driver, 10)
        options = get_all_options(driver=driver, element_identifier=element_identifier)
        label_to_use, accuracy = process.extractOne(query=label, choices=options, scorer=fuzz.token_set_ratio)
        select_button = the_wait.until(element_enabled_by_name(element_identifier),
                                       f"Could not find the {element_identifier}")
        select = Select(select_button)
        select.select_by_visible_text(label_to_use)
    except exceptions.NoSuchElementException and exceptions.TimeoutException:
        if n_element_name is 'AGAIN':
            print(f'Failed to find {element_identifier}, check the label name -- Quiting Driver')
            driver.quit()
            raise FrozenSelectorException
        else:
            try:
                select_button = driver.find_element_by_xpath(backup_xpath)
                select = Select(select_button)
                select.select_by_visible_text(label_to_use)
            except exceptions.NoSuchElementException:
                print(f'Failed to find {element_identifier} element, trying again')
                drop_down_select_and_wait(driver=driver, element_identifier=element_identifier, label=label_to_use,
                                          n_element_name='AGAIN', backup_xpath=backup_xpath)

    if n_element_name is not None and n_element_name is not 'AGAIN':
        try:
            message = f"Waited to long {n_element_name}"
            the_wait = WebDriverWait(driver, 10)
            the_wait.until(element_enabled_by_name(n_element_name), message)
        except Exception as e:
            driver.quit()
            raise FrozenSelectorException(e, n_element_name, driver.current_url)


def fuzzy_drop_down_select(driver, model_string, element_identifier):
    """
    Finds all options under the Make selector and extracts them - then using fuzzystring comparison
    techniques such as Levensteihn's algorithm it determines which string most closely resembles
    the model_string
    :param element_identifier: The element identifier name of the selector you want the options of
    :param driver: The Kelly Blue Book page Drive - driver
    :param model_string: The model body trim and amount of doors of the car (pulled from KSL)- String
    :return: The label of the Select Button to be chosen
    """
    options = get_all_options(driver=driver, element_identifier=element_identifier)
    if len(options) == 1:
        raise FrozenSelectorException("The ModelID options is broken", str(element_identifier), str(driver.current_url))
    label, accuracy = process.extractOne(query=model_string, choices=options, scorer=fuzz.token_set_ratio)
    if accuracy < 50:
        print(f'Very Inaccurate Results trying to find match for {model_string}')
    return label, accuracy


def get_all_options(driver, element_identifier, by=By.NAME):
    """
    Because the options did not populate perfectly every time, this helper function 
    ensures they are present
    :param driver: the driver driving the page
    :param element_identifier: the identifier of the element (name by default)
    :param by: by defualt it is none - but if the element doesn't have a name you can change the search path, input 
                a selenium by object
    :return: the list of all possible options text
    """
    tries = 0
    options_element = Select(driver.find_element(by, element_identifier))
    options = options_element.options
    while len(options) == 1 and tries < 3:
        sleep(1)
        tries = tries + 1
        options = options_element.options
    for index in range(len(options)):
        options[index] = options[index].text
    return options


def next_page(driver, el_locator, next_el_locator=None, the_long_wait = True):
    """
    This class clicks the next page button and waits for the expected page to load
    :param driver: the driver used in the test - driver
    :param el_locator: The locator of the button that brings us to the next page
    :param next_el_locator: The xpath of the expected element on the next page
    :raises: UnexpectedPageLoaded if the element to be found on the next page is not found
    """
    the_wait = WebDriverWait(driver, 10)
    next_button = the_wait.until(EC.presence_of_element_located(el_locator), "We could not find the button")
    driver.execute_script("arguments[0].click();", next_button)
    the_long_wait = WebDriverWait(driver, 15)
    if next_el_locator is not None:
        try:
            if the_long_wait:
                the_next_page_item = the_long_wait.until(EC.presence_of_element_located(next_el_locator),
                                                        "The Next Page took too long to load")
            else:
                 the_next_page_item = the_wait.until(EC.presence_of_element_located(next_el_locator),
                                                        "The Next Page took too long to load")
            return
        except Exception as e:
            print(driver.current_url)
            raise UnexpectedPageLoaded(e, next_el_locator, driver.current_url)


def enter_text(driver, locator, text):
    """
    A helper function to enter text into a field
    :param driver: The driver for the page
    :param locator: How you want the name to be found string with the associated locator path in a tupel ex("name", "steve")
    :param text: The text to be entered to the element
    """
    element = WebDriverWait(driver, 5).until(EC.presence_of_element_located(locator))
    element.clear()
    element.send_keys(text)


def select_correct_button(driver, buttons_id, button_text_wanted=''):
    """
    A function to click radio buttons on the page
    :param driver: The driver of the page
    :param buttons_id: The button group's ID (they will all have)
    :param button_text_wanted: The visible text associated0 with the button to be clicked
    """

    buttons = driver.find_elements_by_xpath(f'//input[@id="{buttons_id}" and @type="radio"]')

    if button_text_wanted == '' or len(buttons) == 1:
        the_button = buttons[0]
        driver.execute_script("arguments[0].click();", the_button)
    else:
        try:
            parent = buttons[0].find_element_by_xpath('..')
            organzied_text_options = re.split(r'[^,] ', parent.text)[1:]
            label = \
                process.extractOne(query=button_text_wanted, choices=organzied_text_options,
                                   scorer=fuzz.token_set_ratio)[0]
            button_index = organzied_text_options.index(label)
            button_to_click = buttons[button_index]
            driver.execute_script("arguments[0].click();", button_to_click)
        except:
            button_to_click = buttons[0]
            driver.execute_script("arguments[0].click();", button_to_click)


class element_enabled_by_name(object):
    """An expectation for checking that an element has a particular css class.

  locator - used to find the element
  returns the WebElement once it has the particular css class
  """

    def __init__(self, locator):
        self.name = locator

    def __call__(self, driver):
        try:
            element = driver.find_element_by_name(self.name)
            if element.get_attribute('disabled') == 'True':
                return False
            else:
                return element
        except exceptions.NoSuchElementException:
            print(f'could not find element with name of {self.name}')
            return False


class element_exists_by_xpath(object):
    """An expectation for checking that an element has a particular css class.

  locator - used to find the element
  returns the WebElement once it has the particular css class
  """

    def __init__(self, xpath):
        self.xpath = xpath

    def __call__(self, driver):
        try:
            element = driver.find_element_by_xpath(self.xpath)
            if element.get_attribute('disabled') == 'True':
                return False
            else:
                return element
        except exceptions.NoSuchElementException:
            return False


class FrozenSelectorException(ScraperException):
    """
    This Exception is raised when Selectors freeze or are unaccesible when they need to be
    """
    def __init__(self, error, name, url):
        """
        Creates the Exception
        :param name: The name attribute of the selector element that is having an issue
        :param url: The URL of the page containing the selector element having an issue
        """
        message = f'The Page with URL: {url}' \
                  f'had a broken selector with a identifier of {name}'
        super().__init__(error, message, FrozenSelectorException)


class UnexpectedPageLoaded(ScraperException):
    """
    This Exception is returned when the page that was loaded was not expected
    """
    def __init__(self,e,  xpath, url):
        """
        Creates the Exception
        :param xpath: The xpath of the expected element that could not be found
        :param url: The URL of the page that was loaded unexpectedly
        """

        message = f'The Page with URL: {url}' \
                  f'did not load the expected xpath: {xpath}'
        super().__init__(e, message, UnexpectedPageLoaded)
