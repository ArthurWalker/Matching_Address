import numpy as np
import os
import pandas as pd
import re
import fuzzywuzzy as fuzz
import time
from tqdm import tqdm,tqdm_pandas

def search_fuzzy(address,df):
    return

def func(row,D4_geo_letters_df):
    dwel1 = row['Dwelling AddressLine1'].strip()
    dwel2 = row['Dwelling AddressLine2'].strip()
    dwel3 = row['Dwelling AddressLine3'].strip()
    num = ""
    if bool(re.search(r'\b[0-9]+\b', dwel1)):
        num = re.search(r'\b[0-9]+\b', dwel1).group()
        last_digit = re.search(r'\b[0-9]+\b', dwel1).end()
        letter_part = dwel1[last_digit + 1:]
        if (len(letter_part) == 0):
            letter_part = dwel2
    else:
        letter_part = dwel1
    search_thoroughfare = D4_geo_letters_df[D4_geo_letters_df.loc[:, 'Full_Address'].str.contains(letter_part)]
    if (search_thoroughfare.shape[0] == 0):
        thoroughfare = dwel2
        if bool(re.search(r'\b^[0-9]+\b', dwel2)):
            num = re.search(r'\b^[0-9]+\b', dwel2).group()
            last_digit = re.search(r'\b^[0-9]+\b', num).end()
            thoroughfare = dwel2[last_digit + 1:]  # this thoroughfare can be the Building group name
        search_thoroughfare = D4_geo_letters_df[D4_geo_letters_df.loc[:, 'Full_Address'].str.contains(thoroughfare)]
    if (len(num) > 0):
        search_num = search_thoroughfare[
            (search_thoroughfare.loc[:, 'SUB_BUILDING_NAME'].str.contains(r'\b{0}\b'.format(num), regex=True)) | (search_thoroughfare.loc[:, 'BUILDING_NUMBER'] == num)]
    elif (letter_part == dwel1):
        search_num = search_thoroughfare[search_thoroughfare.loc[:, 'Full_Address'].str.contains(dwel2)]
    if search_num.shape[0] == 1:
        if (search_num.iloc[0], search_num.columns.get_loc('Status') == ""):
            row['Status'] = 'MATCH'
            row['Geo_Address'] = search_num.iloc[0]['Full_Address'].strip()
            search_num.iloc[0, search_num.columns.get_loc('Status')] = 'FOUND MATCH'
    elif search_num.shape[0] > 1:
        num_match = search_num[search_num.loc[:, 'Status'] != 'FOUND MATCH']
        if (num_match.shape[0] == 1):
            row['Status'] = 'MATCH'
            row['Geo_Address'] = search_num.iloc[0]['Full_Address'].strip()
            search_num.iloc[0, search_num.columns.get_loc('Status')] = 'FOUND MATCH'
        else:
            last_search = search_num[
                search_num.loc[:, 'Full_Address'].str.contains(r'\b{0} {1}\b'.format(dwel1, dwel2))]
            if (last_search.shape[0]):
                row['Status'] = 'MATCH'
                row['Geo_Address'] = search_num.iloc[0]['Full_Address'].strip()
                search_num.iloc[0, search_num.columns.get_loc('Status')] = 'FOUND MATCH'
            else:
                if (len(search_num['SMALL_AREA_REF'].unique()) == 1):
                    row['Status'] = 'SAME_SA'
                else:
                    row['Status'] = list(search_num.ADDRESS_REFERENCE)
    else:
        if (search_thoroughfare.shape[0] > 0 and len(search_thoroughfare['SMALL_AREA_REF'].unique()) == 1):
            row['Status'] = 'SAME_SA_NO_NUMs'
        else:
            row['Status'] = "CANT FIND"
    return row

def main():
    start_time = time.time()
    print "Initializing data"
    path = os.path.join('C:/Users/pphuc/Desktop/Docs/Current Using Docs/')

    dwelling_df = pd.read_csv(path + 'Dwelling_D1.csv', skipinitialspace=True, low_memory=False).fillna('')
    geo_df = pd.read_csv(path + 'Geo_D1.csv', skipinitialspace=True, low_memory=False).fillna('')

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
    geo_df['Full_Address'] = geo_df['ADDR_LINE_1'] + " " + geo_df['ADDR_LINE_2'] + " " + geo_df['ADDR_LINE_3'] + " " + \
                             geo_df['ADDR_LINE_4'] + " " + geo_df['ADDR_LINE_5'] + " " + geo_df['ADDR_LINE_6'] + " " + \
                             geo_df['ADDR_LINE_7'] + " " + geo_df['ADDR_LINE_8'] + " " + geo_df['ADDR_LINE_9'] + " " + \
                             geo_df['ADDR_LINE_10']
    dwelling_df['Status'] = ""
    dwelling_df['Geo_Address'] = ""
    dwelling_df_counties_replace = dwelling_df.replace({'MPRN county': dict_strange_county}, regex=True)

    print "Start searching"
    # dwelling_df_counties_replace = dwelling_df_counties_replace.rename(columns={'Dwelling AddressLine1':'Dwelling_AddressLine1','Dwelling AddressLine2':'Dwelling_AddressLine2','Dwelling AddressLine3':'Dwelling_AddressLine3'})
    D4_dwelling_df = dwelling_df_counties_replace
    D4_geo_df = geo_df

    D4_dwelling_letters_only_df = D4_dwelling_df[(D4_dwelling_df.loc[:, 'Dwelling AddressLine1'].str.contains(r'^[A-Z]+\b', na=False,regex=True))]
    D4_geo_letters_df = D4_geo_df[D4_geo_df.loc[:, 'Full_Address'].str.contains(r'\b^\w+\b', regex=True)]
    tqdm.pandas()
    D4_dwelling_letters_only_df=   D4_dwelling_letters_only_df.progress_apply(func,args=(D4_geo_letters_df,),axis=1)

    print 'Write to CSV'
    D4_dwelling_letters_only_df.to_csv(path_or_buf='Reformat_new4.csv', index=None, header=True)
    print 'Done! from ', time.asctime(time.localtime(start_time)), ' to ', time.asctime(time.localtime(time.time()))

if __name__ == '__main__':
    main()
