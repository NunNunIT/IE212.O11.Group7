import pandas as pd
import requests


# def get_unique_years(dataframe_input):
#     unique_years = []
#     dataframe_input['year'] = pd.to_datetime(dataframe_input['unixReviewTime'], unit='s')
#     unique_years = dataframe_input['year'].dt.year.unique()
#     return unique_years

# def get_unique_categories(dataframe_input):
#     unique_categories = []
#     unique_categories = dataframe_input['categories'].unique()
#     return unique_categories

def extract_lat_long(coord_str):
    try:
        coordinates = eval(coord_str)
        if len(coordinates) == 2:
            return pd.Series({'latitude': coordinates[0], 'longitude': coordinates[1]})
        else:
            raise ValueError("Invalid coordinate format")
    except (SyntaxError, ValueError):
        return pd.Series({'latitude': None, 'longitude': None})