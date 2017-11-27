# import csv

from Messenger_Pigeon.Generic_Funcs import requester as GI

"""
This is a stand alone page that pulled all the bad car models fromm consumerreports.com to be used in determining
value of listings
"""
# def pull_bad_models():
#     """
#     This function pulls all models that have been deemed bad by a national survey taken by cunsumerreports.org
#     :return: None - it creates a csv file with the models that have been deemed bad by consumerreports.org
#     """
#     website = GI.get_website_object('https://www.consumerreports.org/used-cars/used-cars-to-avoid-buying/')
#     bad_models = website.find_all('tr')[1:]
#     models = []
#     for model in bad_models:
#         models.append(process_table(model))
#
#     with open('Info/bad_models.csv', "w") as csv_output:
#         writer = csv.DictWriter(csv_output, fieldnames={"Make", 'Model', 'Year'})
#
#         for model in models:
#             writer.writerow({"Make": model[0], 'Model': model[1], 'Year': model[2]})
#
#     csv_output.close()


def process_table(tag):
    """
    This function is a helper function to pull_bad_models - it parses out all relevant data about the models marked as
    bad
    :param tag: the tag with the model, make, and years associated with the model labled as bad
    :return: 
    """
    childs = tag.contents
    make = GI.grab_attribute('text', childs[0], default_to_string=True)
    model = GI.grab_attribute('text', childs[1], default_to_string=True)
    years = process_years(GI.grab_attribute('text', childs[2], default_to_string=True))
    return make, model, years


def process_years(years):
    """
    Just a helper function to help grab each individual year from lists such as 2012, 1988-2016
    :param years: 
    :return: a list of years explicity stated and contained within ranges.
    """
    years = years.replace(' ', '')
    list_of_years = years.split(',')
    bad_years = []
    for year in list_of_years:
        if year.__contains__('-'):
            start_stop_years = year.split('-')
            range1 = int(start_stop_years[0])
            range2 = int(start_stop_years[1]) + 1
            bad_years += list(range(range1, range2))
        else:
            bad_years.append(int(year))
    return bad_years


# def main():
#     pull_bad_models()

#
# if __name__ == '__main__':
#     main()
