import pandas as pd
import os
import string

def main():
    path = os.path.join('C:/Users/pphuc/Desktop/Docs/Current Using Docs/')
    dwelling_df = pd.read_csv(path + 'Reformat_new10.csv', skipinitialspace=True, low_memory=False).fillna('')

    #geo_df = pd.read_csv(path + 'GeoDirectoryData.csv', skipinitialspace=True, low_memory=False).fillna('')


    # geo_D4 = geo_df.loc[geo_df['PRINCIPAL_POST_TOWN']=='DUBLIN 1']
    # geo_D4.to_csv(path_or_buf='Geo_D.csv',index = None,header=True)
    #
    # dwelling_D4 = dwelling_df.loc[dwelling_df['MPRN city']=='DUBLIN 1']
    # dwelling_D4 = dwelling_D4.replace(r'[\,\.-]', ' ', inplace=False, regex=True)
    # dwelling_D4 = dwelling_D4.replace(r'\s{2,}', ' ', inplace=False, regex=True)
    # dwelling_D4.to_csv(path_or_buf='Dwelling_D.csv',index = None,header=True)

    # Analyzing data
    counties = ['ANTRIM', 'ARGMAGH', 'CARLOW', 'CANVAN', 'CLARE', 'CORK', 'DERRY', 'DONEGAL', 'DOWN',
                'FERMANAGH', 'GALWAY', 'KERRY', 'KILDARE', 'KILKENNY', 'LAOIS', 'LEITRIM', 'LIMERICK', 'LONGFORD',
                'LOUTH', 'MAYO', 'MEATH', 'MONAGHAN', 'OFFALY', 'ROSCOMMON', 'SLIGO', 'TIPPERARY', 'TYRONE',
                'WATERFORD', 'WESTMEATH', 'WEXFORD', 'WICKLOW']  #'DUBLIN' not in

    dublin_cities = ['DUBLIN 1', 'DUBLIN 2', 'DUBLIN 3', 'DUBLIN 4', 'DUBLIN 5', 'DUBLIN 6', 'DUBLIN 7', 'DUBLIN 8',
                     'DUBLIN 9', 'DUBLIN 10', 'DUBLIN 11', 'DUBLIN 12', 'DUBLIN 13', 'DUBLIN 14', 'DUBLIN 15',
                     'DUBLIN 16', 'DUBLIN 17', 'DUBLIN 18', 'DUBLIN 20', 'DUBLIN 22', 'DUBLIN 24',
                     'DUBLIN 6W']
    dict_strange_county = {r'\bZA\b': 'DUBLIN', r'\bZB\b': 'CAVAN', r'\bZC\b': 'CARLOW', r'\bZD\b': 'KERRY',
                           r'\bZG\b': 'WICKLOW', r'\bZH\b': 'CLARE', r'\bZF\b': 'KILDARE', r'\bZI\b': 'CORK',
                           r'\bZJ\b': 'DONEGAL', r'\bZK\b': 'GALWAY', r'\bZL\b': 'WESTMEATH', r'\bZO\b': 'WEXFORD',
                           r'\bZP\b': 'LONGFORD', r'\bZR\b': 'LIMERICK', r'\bZS\b': 'MAYO', r'\bZT\b': 'MEATH',
                           r'\bZU\b': 'MONAGHAN', r'\bZV\b': 'WATERFORD', r'\bZW\b': 'ROSCOMMON', r'\bZX\b': 'SLIGO',
                           r'\bZY\b': 'TIPPERARY', r'\bDB\b': 'DUBLIN', r'\bDL\b': 'DUBLIN', r'\b6 W': '6W',
                           r'\b6 WEST\b': '6W', r'\bKK\b': 'KILKENNY', r'\bCK\b': 'CORK', r'\bKE\b': 'KILDARE',
                           r'\bGW\b': 'GALWAY', r'\bKY\b': 'KERRY', r'\bMO\b': 'MAYO', r'\bCE\b': 'CLARE',
                           r'\bDN\b': 'DOWN', r'\bWX\b': 'WEXFORD', r'\bLK\b': 'LIMERICK', r'\bLM\b': 'LEITRIM',
                           r'\bLS\b': 'LAOIS', r'\bOY\b': 'OFFALY', r'\bMN\b': 'MONAGHAN', r'\bLH\b': 'LOUTH',
                           r'\bMH\b': 'MEATH', r'\bCN\b': 'CAVAN', r'\bWW': 'WICKLOW', r'\bCW\b': 'CARLOW',
                           r'\bWD\b': 'WATERFORD', r'\bLD\b': 'LONGFORD', r'\bSO\b': 'SLIGO', r'\bWH\b': 'WESTMEATH',
                           r'\bAM\b': 'ANTRIM', r'\bRN\b': 'ROSCOMMON', r'\bTE\b': 'TYRONE', r'\bTP\b': 'TIPPERARY',
                           r'\bDE\b': 'DERRY', r'\bZE\b': 'KILKENNY', r'\bZQ\b': 'LOUTH', r'\bZZ\b': 'OFFALY',
                           r'\bZM\b': 'LAOIS'}

    dwelling_df_counties_replace = dwelling_df.replace({'MPRN county': dict_strange_county}, regex=True)
    dublin_geodf_dict = {}
    county_geodf_dict = {}
    dublin_dwellingdf_dict = {}
    county_dwellingdf_dict = {}

    result = dwelling_df_counties_replace[dwelling_df_counties_replace.loc[:,'Dwelling AddressLine1'].str.contains(r'[!@#$%&*\_+\-=|\\:\";\<\>\,\.\/\(\)\[\]{}]',regex=True)]
    #result.shape[0]

    dwelling_dublin = dwelling_df_counties_replace.groupby('MPRN city')
    geo_dublin =  geo_df.groupby('PRINCIPAL_POST_TOWN')
    dwelling_county= dwelling_df_counties_replace.groupby('MPRN county')
    geo_county =  geo_df.groupby('COUNTY')

    # for i in dublin_cities:
    #     dublin_geodf_dict[i]=geo_dublin.get_group(i)
    #     dublin_dwellingdf_dict[i]=dwelling_dublin.get_group(i)
    #     # each_type_dublin = process_each_category(dublin_dwellingdf_dict[i],dublin_geodf_dict[i])
    #     # dwelling_df.update(each_type_dublin)
    # for j in counties:
    #     county_dwellingdf_dict[j] = dwelling_county.get_group(j)
    #     county_geodf_dict[j] = geo_county.get_group(j)
    #     #each_type_county = process_each_category(county_dwellingdf_dict[j], county_dwellingdf_dict[j])
    #     #dwelling_df.update(each_type_county)

    dwelling_D1 = dwelling_dublin.get_group('DUBLIN 1')
    geo_D1 = geo_dublin.get_group('DUBLIN 1')

    #D1_2 = dwelling_df_counties_replace[dwelling_df_counties_replace.loc[:, 'MPRN city'] == 'DUBLIN 4']
    #D1_2.shape[0]

    dwelling_D1.to_csv(path_or_buf='Dwelling_D1.csv', index=None, header=True)
    geo_D1.to_csv(path_or_buf='Geo_D1.csv', index=None, header=True)
if __name__ == '__main__':
    main()