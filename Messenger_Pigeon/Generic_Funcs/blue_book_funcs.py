import re
"""
This page contains generic static functions that are used when grabbing the bluebook value with selenium
"""

def select_condition_button(driver, condition_value):
    """
    This function selects the correct radio condition button
    :param driver: The
    :param condition_value: Either E, G, F, or P based on the condition of the car 
                                see calculate_condition method for more info
    :return: selects the correct radio button with the condition
    """

    button = driver.find_element_by_xpath(f'//input[@value="{condition_value}" and @type="radio" and @id="ConditionType"]')
    driver.execute_script("arguments[0].click();", button)





def grab_price(driver):
    """
    This function must be called on the right page to work as designed.
    This function grabs the price calculated by kelly_blue_books and returns it
    :param driver: The Driver of the page
    :return: either an empty string or an int of the cost
    """
    price = driver.find_element_by_xpath('//*[@id="js-promo-popup"]/div/div[2]/div[1]/div[3]/p').text
    price = price.strip()
    price = re.sub('.*Value [$]', '', price)
    price = price.replace(',', '')
    price = price.strip()
    if price != '':
        price = int(price)
    return price
