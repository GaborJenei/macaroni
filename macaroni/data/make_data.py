import pandas as pd
import numpy as np
import requests as re
from bs4 import BeautifulSoup
from google_currency import convert, CODES
import json
import warnings


def decompose_name(name: str, name_titles=None):
    """
    Decompose name into name_title, first_name and last_name by splitting input str at whitespace ' '.

    Parameters
    ----------
    name:str
        name to be split or decomposed

    name_titles: list of str, default None reverts to ['Mr.', 'Miss', 'Dr.', 'Ms.', 'Mrs.']
        titles accepted and extracted to name_title

    Returns
    -------
        pandas series of pd.Series([name_title, first_name, last_name])
    """

    if name_titles is None:
        name_titles = ['Mr.', 'Miss', 'Dr.', 'Ms.', 'Mrs.']
    split_name = name.split(' ')

    if split_name[0] in name_titles:
        name_title = split_name[0]
        first_name = split_name[1]
        last_name = split_name[-1]
    else:
        name_title = np.NaN
        first_name = split_name[0]
        last_name = split_name[-1]

    return pd.Series([name_title, first_name, last_name])


def get_postcode_area(towns):
    """
    Converts the series of towns to postal area codes using values scraped from Wikipedia:
     'https://en.wikipedia.org/wiki/List_of_postcode_areas_in_the_United_Kingdom'

    Parameters
    ----------
    towns: pandas Series
        series of towns to turn into postal area codes

    Returns
    -------
     pandas Series with postal area codes
    """

    # Post areas data on the web
    post_area_url = 'https://en.wikipedia.org/wiki/List_of_postcode_areas_in_the_United_Kingdom'

    table_class = "wikitable"
    response = re.get(post_area_url)

    # parse the html
    soup = BeautifulSoup(response.text, 'html.parser')
    post_area = soup.find('table', {'class': "wikitable"})

    # read up with pandas
    df_wikitables = pd.read_html(str(post_area))
    df_post_areas = df_wikitables[0]

    # clean up table
    df_post_areas = df_post_areas.iloc[:, [0, 1]].copy()
    df_post_areas.columns = ['postcode_area', 'postcode_area_name']
    df_post_areas['postcode_area_name'] = df_post_areas['postcode_area_name'].str.split('[', expand=True).get(0)

    # Convert it to a dictionary
    postcode_areas_dict = df_post_areas.set_index('postcode_area_name')['postcode_area'].to_dict()

    return towns.map(postcode_areas_dict)


def clean_salary_band(salary):
    """
    Convert salary values to a common form by returning a lower, upper bound, a currency and frequency

    Parameters
    ----------
    salary:str
        salary value as a string to harmonise

    Returns
    -------
        pandas series of pd.Series([lower, upper, freq, currency])

    """

    # check first if value is Na
    if pd.isna(salary):
        lower = 0
        upper = 0
        freq = pd.NA
        currency = pd.NA

    # check and remove frequency indicators
    elif any([period in salary for period in ['yearly', 'pw', 'per month']]):
        sal = salary.split(' ', 1)[0][1:]

        lower = sal
        upper = sal
        freq = salary.split(' ', 1)[1]

        if '£' in salary:
            currency = 'GBP'

    elif ' range' in salary:
        sal = salary.split(' ')

        lower = sal[0][1:]
        upper = sal[2]
        freq = 'yearly'

        if '£' in salary:
            currency = 'GBP'

    # lastly process the '12358HUF' formatted values with a 3 letter currency code at the end
    elif len(salary) > 3:
        lower = salary[:-3]
        upper = salary[:-3]
        freq = pd.NA
        currency = salary[-3:]

    else:
        lower = 0
        upper = 0
        freq = pd.NA
        currency = pd.NA

    return pd.Series([lower, upper, freq, currency])


def get_currency_rates(currencies):
    """
    extracts and maps to GBP currency rates from input series of 3 letter currency codes

    Parameters
    ----------
    currencies:Series of str
        currency codes to convert from

    Returns
    -------
      pandas series of currency rates
    """

    conversion_rate = {}

    # get a unique list
    unique_currencies = currencies.unique()

    # drop any Nas
    unique_currencies = unique_currencies[~pd.isna(unique_currencies)]

    # Loop through the currencies and query the rate
    for currency in unique_currencies:

        if currency in list(CODES.keys()):
            rate = json.loads(convert(currency, 'GBP', 1))

            if rate.get("converted"):
                conversion_rate[currency] = rate.get("amount")
            else:
                conversion_rate[currency] = pd.NA

        else:
            conversion_rate[currency] = pd.NA

    return currencies.map(conversion_rate)

# TODO: Add function combining the ETL process end to end.