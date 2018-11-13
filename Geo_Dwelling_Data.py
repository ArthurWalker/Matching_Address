#coding=utf-8
import numpy as np
import os
import pandas as pd
import re
from fuzzywuzzy import fuzz
import time
from tqdm import tqdm
import pickle
import multiprocessing
from numba import jit
import pyximport; pyximport.install()
from Finding_Match import fix_misspell,reformat,process_each_category,dict

def main():
    start_time = time.time()
    print "Initializing data"
    #C:/Users/MBohacek/AAA_PROJECTS/Pham_geocoding/data_PhamMatching/
    #C:/Users/pphuc/Desktop/Docs/Current Using Docs/Sample Data/
    #S:/Low Carbon Technologies/Behavioural Economics/01. Current Projects/01.08.2018 Geocoding Project/Files to put on servers  - Phuc/
    path = os.path.join('C:/Users/pphuc/Desktop/Docs/Current Using Docs/Sample Data/')
    #dwelling_df = pd.read_csv(path+'Results_Blank_Fields_4000_MANY_RESULTS.csv',skipinitialspace=True,low_memory=False).fillna('')
    dwelling_df = pd.read_csv(path+'Result_Blank.csv', skipinitialspace=True, low_memory=False).fillna('')

    geo_df = pd.read_csv(path + 'GeoDirectoryData.csv', skipinitialspace=True, low_memory=False).fillna('')
    dwelling_df = dwelling_df.replace(r'[!@#$%&*\_+\-=|\\:\";\<\>\,\.\(\)\[\]{}]', '', inplace=False, regex=True)
    dwelling_df = dwelling_df.replace(r'[\,\.-\/]', ' ', inplace=False, regex=True)
    dwelling_df = dwelling_df.replace(r'\s{2,}', ' ', inplace=False, regex=True)
    dwelling_df['Dwelling AddressLine1'] = dwelling_df['Dwelling AddressLine1'].apply(lambda x: x.strip())
    dwelling_df = fix_misspell(dwelling_df)

    counties = ['CARLOW', 'CAVAN', 'CLARE', 'CORK', 'DONEGAL','DUBLIN',
                'GALWAY', 'KERRY', 'KILDARE', 'KILKENNY', 'LAOIS', 'LEITRIM', 'LIMERICK', 'LONGFORD',
                'LOUTH', 'MAYO', 'MEATH', 'MONAGHAN', 'OFFALY', 'ROSCOMMON', 'SLIGO', 'TIPPERARY',
                'WATERFORD', 'WESTMEATH', 'WEXFORD', 'WICKLOW']
    dublin_cities = ['DUBLIN 1', 'DUBLIN 2', 'DUBLIN 3', 'DUBLIN 4', 'DUBLIN 5', 'DUBLIN 6', 'DUBLIN 7', 'DUBLIN 8',
                     'DUBLIN 9', 'DUBLIN 10', 'DUBLIN 11', 'DUBLIN 12', 'DUBLIN 13', 'DUBLIN 14', 'DUBLIN 15',
                     'DUBLIN 16', 'DUBLIN 17', 'DUBLIN 18', 'DUBLIN 20', 'DUBLIN 22','DUBLIN 24',
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

    geo_df['Fuzzy'] = ""
    geo_df['Status'] = ""
    geo_df['Full_Address'] = (geo_df['ADDR_LINE_1'] + " " + geo_df['ADDR_LINE_2'] + " " + geo_df['ADDR_LINE_3'] + " " + \
                             geo_df['ADDR_LINE_4'] + " " + geo_df['ADDR_LINE_5'] + " " + geo_df['ADDR_LINE_6'] + " " + \
                             geo_df['ADDR_LINE_7'] + " " + geo_df['ADDR_LINE_8'] + " " + geo_df['ADDR_LINE_9'] + " " + \
                             geo_df['ADDR_LINE_10'])
    geo_df['Full_Address'] = geo_df['Full_Address'].apply(reformat)
    dwelling_df['Status'] = ""
    dwelling_df['Percent_Match']=""
    dwelling_df['BUILDING_ID'] = ""
    dwelling_df['ADDRESS_REFERENCE'] = ""
    dwelling_df['EIRCODE'] = ""
    dwelling_df['SMALL_AREA_REF'] = ""
    dwelling_df['EIRCODE'] = ""
    dwelling_df['Geo_Address'] = ""
    dwelling_df['LATITUDE'] = ""
    dwelling_df['LONGITUDE'] = ""
    dwelling_df['UNIQUE_SMALL_AREA_REF']=""
    dwelling_df['UNIQUE_EIRCODE']=""
    dwelling_df['UNIQUE_LATITUDE']=""
    dwelling_df['UNIQUE_LONGITUDE']=""
    dwelling_df['DwellingData_id']=""
    dwelling_df_counties_replace = dwelling_df.replace({'MPRN county': dict_strange_county}, regex=True)
    dwelling_dublin = dwelling_df_counties_replace.groupby('MPRN city')
    geo_dublin =  geo_df.groupby('PRINCIPAL_POST_TOWN')
    dwelling_county= dwelling_df_counties_replace.groupby('MPRN county')
    geo_county =  geo_df.groupby('COUNTY')
    #no_mprn_county_df = dwelling_county.get_group("")
    #Extract no mprn info data
    #no_mprn_county_df_results = looking_for_matching_for_no_mprn_county(no_mprn_county_df)
    #dwelling_df_counties_replace.update(no_mprn_county_df_results)
    #dwelling_dublin = dwelling_df_counties_replace.groupby('MPRN city')
    #dwelling_county = dwelling_df_counties_replace.groupby('MPRN county')

    global dict

    # for i in dublin_cities:
    #     print i
    #     # if i =='DUBLIN 2':
    #     #     break
    #     # if (i == 'DUBLIN 3'):
    #     if i in dwelling_dublin.groups.keys():
    #         each_type_dublin = process_each_category(dwelling_dublin.get_group(i),geo_dublin.get_group(i),dict)
    #         dwelling_df_counties_replace.update(each_type_dublin)

    # dwelling_df_counties_replace = dwelling_df_counties_replace[['Dwelling Address','Dwelling AddressLine1','Dwelling AddressLine2','Dwelling AddressLine3','MPRN Address','MPRN unit no','MPRN house no','MPRN street','MPRN address4','MPRN city','MPRN county','Status','Percent_Match','Geo_Address','EIRCODE','SMALL_AREA_REF']]

    #each_type_dublin.to_csv(path_or_buf='Dwelling_D1_results.csv', index=None, header=True)


    for j in counties:
        print j
        # if (j == 'WICKLOW'):
        # #    break
        if j=='CORK' and j in dwelling_county.groups.keys():
            if (j=='DUBLIN'):
                geo_outside_DUBLIN = geo_county.get_group(j)
                dwelling_DUBLIN =dwelling_county.get_group(j)
                dwelling_outside_DUBLIN = dwelling_DUBLIN[~dwelling_DUBLIN['MPRN city'].isin(dublin_cities)]
                each_type_county = process_each_category(dwelling_outside_DUBLIN, geo_outside_DUBLIN)
            else:
                each_type_county = process_each_category(dwelling_county.get_group(j), geo_county.get_group(j))
            dwelling_df_counties_replace.update(each_type_county)

    #each_type_county.to_csv(path_or_buf='Result_Outside_Dublin.csv', index=None, header=True)

    # Saving the dictionary:
    with open('dict_ADDRESS_REFERENCE.pkl', 'w') as f:  # Python 3: open(..., 'wb')
        pickle.dump(dict, f)

    dwelling_df_counties_replace.to_csv(path_or_buf='Results_Blank_Fields_Cork.csv', index=None, header=True)
    print 'Done! from ', time.asctime( time.localtime(start_time)),' to ',time.asctime( time.localtime(time.time()))

if __name__ == '__main__':
    main()


