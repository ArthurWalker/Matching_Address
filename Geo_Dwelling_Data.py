#coding=utf-8
import numpy as np
import os
import pandas as pd
import re
from fuzzywuzzy import fuzz
import time
from tqdm import tqdm

def change_position_UPPER_LOWER(row):
    if (row['MPRN street'].split(' ',1)[0] =='UPPER'):
        row['MPRN street'] = row['MPRN street'].split(' ',1)[1]+" UPPER"
    elif (row['MPRN street'].split(' ',1)[0] =='LOWER'):
        row['MPRN street'] = row['MPRN street'].split(' ',1)[1]+" LOWER"
    elif (row['MPRN address4'].split(' ',1)[0] =='UPPER'):
        row['MPRN address4'] = row['MPRN address4'].split(' ',1)[1]+" UPPER"
    elif (row['MPRN address4'].split(' ',1)[0] =='LOWER'):
        row['MPRN address4'] = row['MPRN address4'].split(' ',1)[1]+" LOWER"
    return row

def reformat(row):
    row = row.strip()
    row = row.rsplit(' ',1)[0]
    if (re.search(r'[0-9]+\/[0-9]+', row)):
        word = re.findall(r"[0-9]+\/[0-9]+", row)
        new_word = re.sub("/", " ", word[0])
        row = re.sub(word[0], new_word, row)
    elif (re.search(r'[0-9]+-[0-9]+', row)):
        word = re.findall(r"[0-9]+-[0-9]+", row)
        list_num = re.split("-", word[0])
        list_range_num = [str(num) for num in range(
            int(list_num[0]), int(list_num[1]) + 1)]
        range_num = " ".join(list_range_num)
        row = re.sub(word[0], range_num, row)
    elif (re.search(r'[0-9]+_[0-9]+', row)):
        word = re.findall(r"[0-9]+_[0-9]+", row)
        list_num = re.split("_", word[0])
        list_range_num = [str(num) for num in range(
            int(list_num[0]), int(list_num[1]) + 1, 2)]
        range_num = " ".join(list_range_num)
        row = re.sub(word[0], range_num, row)
    return row

def search_for_misspell(row,df_thoroughfare,col):
    df_thoroughfare['Fuzzy']=""
    term = row[col].strip()
    df_thoroughfare['Fuzzy']=df_thoroughfare['THOROUGHFARE'].apply(search_fuzzy_token, args=(term,))
    if (df_thoroughfare['Fuzzy'].max()>95):
        street = df_thoroughfare[df_thoroughfare['Fuzzy']==df_thoroughfare['Fuzzy'].max()]
        row[col]=street.iloc[0]['THOROUGHFARE']
    return row

def fix_misspell(df):
    misspell= {
        r'\bSQAARE\b':'SQUARE',
        r'\bHOASE\b':'HOUSE',
        r'\bAV\b':'AVENUE',
        r'\bWINTER GARDENS\b':'WINTER GARDEN',
        r'\bKILLARNEY COURT\b':'KILLARNEY AVENUE',
        r'\bGRANVILLE\b':'GRENVILLE'
    }
    df = df.replace(misspell,inplace=False, regex=True)
    return df

def match(row,df,status):
    row['Status'] = status
    row['Geo_Address'] = df.iloc[0]['Full_Address']
    row['ADDRESS_REFERENCE'] = df.iloc[0]['ADDRESS_REFERENCE']
    row['BUILDING_ID'] = df.iloc[0]['BUILDING_ID']
    row['EIRCODE'] = df.iloc[0]['EIRCODE']
    row['SMALL_AREA_REF'] = df.iloc[0]['SMALL_AREA_REF']
    row['LATITUDE'] = df.iloc[0]['LATITUDE']
    row['LONGITUDE'] = df.iloc[0]['LONGITUDE']
    return row

def remove_accents(string):
    if type(string) is not unicode:
        string = unicode(string, encoding='utf-8')
        string = re.sub(r'[u"àáâãäå"]'.upper(), 'A', string)
        string = re.sub(r'[u"èéêë"]'.upper(), 'E', string)
        string = re.sub(r'[u"ìíîï"]'.upper(), 'I', string)
        string = re.sub(r'[u"òóôõö"]'.upper(), 'O', string)
        string = re.sub(r'[ùúûü]', 'U', string)
        string = re.sub(r'[u"ùúûü"]'.upper(), 'U', string)
        string = re.sub(r'[u"ýÿ"]'.upper(), 'Y', string)
    return string

def search_fuzzy_token(row,address):
    return fuzz.token_sort_ratio(row,address)

def search_fuzzy(row,address_to_cp):
    return fuzz.partial_ratio(row,address_to_cp)

def fuzzy_process(search_num,row,dwel):
    search_num['Fuzzy'] = search_num['Full_Address'].apply(search_fuzzy, args=(dwel,))
    if (search_num['Fuzzy'].shape[0] > 0):
        max_rows = search_num[search_num['Fuzzy'] == search_num['Fuzzy'].max()]
        if max_rows.shape[0] > 1:
            df = max_rows[max_rows.loc[:,'Full_Address'].str.contains(dwel,regex=True)]
            if (df.shape[0]==1 and df['Fuzzy']>65):
                row = match(row,df,'MATCH_Fuzzy')
                row['Percent_Match']=df['Fuzzy'].max()
            else:
                row=match(row,search_num,'MANY RESULTS')
        elif max_rows.shape[0]==1:
            if (max_rows['Fuzzy'].unique()>=65):
                row = match(row, max_rows,'MATCH_Fuzzy')
                row['Percent_Match'] = max_rows['Fuzzy'].max()
    else:
        row = match(row, search_num, 'MANY RESULTS')
    return row

def search_MPRN(row,geo_df,df_thoroughfare):
    cant_find=False
    #row = row.replace(r'\b[FLAT|APT|BASEMENT|FLOOR|GROUND|FIRST|SECOND|THIRD|APARTMENT|FL|UNIT|TOP|TP|NO|NUMBER]\b','',inplace=False, regex=True)
    row = row.replace(r'\s{2,}',' ',inplace=False, regex=True)
    row = row.str.strip()
    row = search_for_misspell(row,df_thoroughfare, 'MPRN street')
    search_thoroughfare = geo_df[geo_df.loc[:,'Full_Address'].str.contains(r'\b{0}\b'.format(row['MPRN street']),regex=True)]
    search_num = None
    search_apart = None
    #row = change_position_UPPER_LOWER(row)
    if (search_thoroughfare.shape[0]>0):
        search_num = search_thoroughfare[search_thoroughfare.loc[:,'Full_Address'].str.contains(r'\b{0}\b'.format(row['MPRN house no'].strip()),regex=True)]
    else:
        row = search_for_misspell(row, df_thoroughfare, 'MPRN address4')
        search_thoroughfare = geo_df[geo_df.loc[:, 'Full_Address'].str.contains(r'\b{0}\b'.format(row['MPRN address4']),regex=True)]
        if (search_thoroughfare.shape[0] > 0):
            search_num = search_thoroughfare[search_thoroughfare.loc[:, 'Full_Address'].str.contains(r'\b{0}\b'.format(row['MPRN house no'].strip()),regex=True)]
    if len(row['MPRN unit no'])!=0:
        if ('APARTMENT' in row['MPRN unit no']):
            row['MPRN unit no']= re.sub(r'\bAPARTMENT\b','',row['MPRN unit no'])
        if (search_num is not None and search_num.shape[0]>0):
            search_apart = search_num[search_num.loc[:, 'Full_Address'].str.contains(r'\b{0}\b'.format(row['MPRN unit no'].strip()), regex=True)]
        else:
            search_apart = search_thoroughfare[search_thoroughfare.loc[:,'Full_Address'].str.contains(r'\b{0}\b'.format(row['MPRN unit no'].strip()),regex=True)]
    if (search_apart is not None):
        if (search_apart.shape[0]==1):
            row = match(row, search_apart,'MATCH')
        elif (search_apart.shape[0] > 1 and len(search_apart['SMALL_AREA_REF'].unique()) == 1):
            row = match(row, search_apart, 'SAME_SA')
        elif (search_apart.shape[0] > 1 and len(search_apart['SMALL_AREA_REF'].unique()) != 1):
            row = fuzzy_process(search_apart, row, row['MPRN Address'])
    if search_num is not None:
        if (search_num.shape[0]==1):
            row = match(row, search_num,'MATCH')
        elif (search_num.shape[0] > 1 and len(search_num['SMALL_AREA_REF'].unique()) == 1):
            row = match(row, search_num, 'SAME_SA')
        elif (search_num.shape[0] > 1 and len(search_num['SMALL_AREA_REF'].unique()) != 1):
            row = fuzzy_process(search_num, row, row['MPRN Address'])
        else:
            cant_find=True
    else:
        cant_find = True
    if (cant_find):
        row['Status']='CANT FIND'
    return row

# def search_dwelling(row,geo_df,df_thoroughfare):
#     row_data = row['Dwelling AddressLine1']+" "+row['Dwelling AddressLine2']+" "+row['Dwelling AddressLine3']
#     #row_data = re.sub(r'\bFLAT|APT|BASEMENT|FLOOR|GROUND|1ST|2ND|3RD|FIRST|SECOND|THIRD|APARTMENT|FL|UNIT|TOP|TP|NO|NUMBER\b','',row_data)
#     row_data = re.sub(r'\s{2,}',' ',row_data)
#     row_data = row_data.strip()
#     list_word = row_data.split(' ')
#     search = geo_df
#     for word in list_word:
#         temp = search[search.loc[:,'Full_Address'].str.contains(r'\b{0}\b'.format(word), regex=True)]
#         if (temp is not None or temp.shape[0] >0):
#             search = temp
#     if (search.shape[0]==1):
#         row = match(row, search,'MATCH')
#     elif (search.shape[0] > 1 and len(search['SMALL_AREA_REF'].unique()) == 1):
#         row['Status'] = 'SAME_SA'
#         row['SMALL_AREA_REF'] = search.iloc[0]['SMALL_AREA_REF']
#
#     elif (search.shape[0] > 1 and len(search['SMALL_AREA_REF'].unique()) != 1):
#         row = fuzzy_process(search, row, row_data)
#     else:
#         row = search_MPRN(row,geo_df,df_thoroughfare)
#     return row

def search_num_first(row,D4_geo_num_df,df_thoroughfare):
    try:
        dwel1 = (row['Dwelling AddressLine1'].strip())
        dwel2 = (row['Dwelling AddressLine2'].strip())
        dwel3 = (row['Dwelling AddressLine3'].strip())
        # num part
        if (re.search(r'\b^[0-9]+\b', dwel1)):
            num = re.search(r'\b^[0-9]+\b', dwel1).group()
            last_digit = re.search(r'\b^[0-9]+\b', dwel1).end()
        elif (re.search(r'\b^[0-9]+[A-Z]+\b',dwel1)):
            dit_let =re.search(r'\b^[0-9]+[A-Z]+\b',dwel1).group()
            last_digt = re.search(r'\b^[0-9]+[A-Z]+\b',dwel1).end()
            num = re.search(r'\b^[0-9]+', dit_let).group()
        # later part: it can be digit+letters or letter. But 0 assume that they are letters
        thoroughfare_dwel1 = dwel1[last_digit + 1:]  # this thorough can be the Building group name
        # Search BUILDING_GROUP_NAME/ THOROUGHFARE:
        if (len(thoroughfare_dwel1)==0):
            thoroughfare_dwel1=dwel2
        search_thorougfare = D4_geo_num_df.loc[D4_geo_num_df['Full_Address'].str.contains(thoroughfare_dwel1)]
        if (search_thorougfare.shape[0] == 0):
            thoroughfare = dwel2
            if bool(re.search(r'\b^[0-9]+\b', dwel2)):
                num_dwel = re.search(r'\b^[0-9]+\b', dwel2).group()
                last_digit = re.search(r'\b^[0-9]+\b', num_dwel).end()
                thoroughfare = dwel2[last_digit + 1:]  # this thoroughfare can be the Building group name
            search_thorougfare = D4_geo_num_df[D4_geo_num_df.loc[:, 'Full_Address'].str.contains(thoroughfare)]
        search_num = search_thorougfare[(search_thorougfare.loc[:, 'SUB_BUILDING_NAME'].str.contains(r'\b{0}\b'.format(num), regex=True)) | (search_thorougfare.loc[:, 'BUILDING_NUMBER'] == num)]
        if search_num.shape[0] == 1:
            if (search_num.iloc[0]['Status']==""):
                row = match(row, search_num,'MATCH')
        elif search_num.shape[0] > 1:
            num_match = search_num[search_num.loc[:, 'Status'] != 'FOUND MATCH']
            if (num_match.shape[0] == 1):
                row = match(row,num_match,'MATCH')
            else:
                # Checking if it matches
                last_search = search_num[search_num.loc[:, 'Full_Address'].str.contains(r'\b{0} {1}\b'.format(dwel1, dwel2))]
                if (last_search.shape[0]==1):
                    row = match(row, search_num,'MATCH')
                else:
                    if (len(search_num['SMALL_AREA_REF'].unique())==1):
                        row = match(row, search_num, 'SAME_SA')
                    else:
                        #row['Status'] = list(search_num.BUILDING_ID.map(str) + "/" + search_num.ADDRESS_POINT_ID.map(str))
                        # Search by fuzzy wuzzy
                        # row = fuzzy_process(search_num,row,dwel1+" "+dwel2)
                        row = fuzzy_process(search_num,row,num+" "+thoroughfare_dwel1)
        else:
            if (search_thorougfare.shape[0]>0 and len(search_thorougfare['SMALL_AREA_REF'].unique())==1):
                row = match(row, search_thorougfare, 'SAME_SA_NO_NUMs')
            else:
                row = search_MPRN(row,D4_geo_num_df,df_thoroughfare)
    except Exception as ex:
        print(type(ex))  # the exception instance # arguments stored in .args
        print(ex)
        print row
    return row

def search_letter_first(row,D4_geo_letters_df,df_thoroughfare):#
    other_way = False
    try:
        search_num=None
        dwel1 = row['Dwelling AddressLine1'].strip()
        dwel2 = row['Dwelling AddressLine2'].strip()
        dwel3 = row['Dwelling AddressLine3'].strip()
        num =""
        if bool(re.search(r'\b[0-9]+\b',dwel1)):
            num = re.search(r'\b[0-9]+\b',dwel1).group()
            last_digit = re.search(r'\b[0-9]+\b',dwel1).end()
            thoroughfare = dwel1[last_digit+1:]
            if (len(thoroughfare)==0):
                thoroughfare=dwel2
        else:
            thoroughfare = dwel1
        search_thoroughfare = D4_geo_letters_df[D4_geo_letters_df.loc[:,'Full_Address'].str.contains(thoroughfare)]
        if (search_thoroughfare.shape[0]==0):
            thoroughfare = dwel2
            if bool(re.search(r'\b[0-9]+\b', dwel2)):
                num = re.search(r'\b[0-9]+\b', dwel2).group()
                last_digit = re.search(r'\b[0-9]+\b', num).end()
                thoroughfare = dwel2[last_digit + 1:]  # this thoroughfare can be the Building group name
            if (len(dwel2)==0):
                thoroughfare=dwel3
                if bool(re.search(r'\b[0-9]+\b', dwel3)):
                    num = re.search(r'\b[0-9]+\b', dwel3).group()
                    last_digit = re.search(r'\b[0-9]+\b', num).end()
                    thoroughfare = dwel3[last_digit + 1:]
            search_thoroughfare = D4_geo_letters_df[D4_geo_letters_df.loc[:, 'Full_Address'].str.contains(thoroughfare)]
        if (len(num) > 0):
            search_num = search_thoroughfare[(search_thoroughfare.loc[:, 'SUB_BUILDING_NAME'].str.contains(r'\b{0}\b'.format(num), regex=True)) | (search_thoroughfare.loc[:, 'BUILDING_NUMBER'] == num)]
        elif (thoroughfare==dwel1):
            search_num = search_thoroughfare[search_thoroughfare.loc[:, 'Full_Address'].str.contains(dwel2)]
        if (search_num is not None):
            if search_num.shape[0] == 1:
                if (search_num.iloc[0]['Status']==""):
                    row = match(row,search_num,'MATCH')
            elif search_num.shape[0] > 1:
                num_match = search_num[search_num.loc[:, 'Status'] != 'FOUND MATCH']
                if (num_match.shape[0] == 1):
                    row = match(row, num_match,'MATCH')
                else:
                    # Checking if it matches
                    last_search = search_num[search_num.loc[:,'Full_Address'].str.contains(r'\b{0} {1}\b'.format(dwel1,dwel2))]
                    if (last_search.shape[0]):
                        row = match(row, search_num,'MATCH')
                    else:
                        if (len(search_num['SMALL_AREA_REF'].unique()) == 1):
                            row = match(row, search_num, 'SAME_SA')
                        else:
                            row = fuzzy_process(search_num, row, dwel1 + " " + dwel2)
            else:
                if (search_thoroughfare.shape[0] > 0 and len(search_thoroughfare['SMALL_AREA_REF'].unique()) == 1):
                    row = match(row, search_thoroughfare, 'SAME_SA_NO_NUMs')
                else:
                    other_way = True
        else:
            other_way=True
        if (other_way):
            row = search_MPRN(row, D4_geo_letters_df,df_thoroughfare)
    except Exception as ex:
        print(type(ex))  # the exception instance # arguments stored in .args
        print(ex)
        print row

    #filter = D4_geo_letters_df[D4_geo_letters_df.loc[:,'Full_Address'].str.contains(r'\bCANON\b',regex=True)]
    return row

def search_num_letter(row, D4_geo_num_df,df_thoroughfare):
    other_way=False
    try:
        mprn_house_no = row['MPRN house no'].strip()
        street = row['MPRN street'].strip()
        search_street = D4_geo_num_df[D4_geo_num_df.loc[:,'Full_Address'].str.contains(street)]
        if (search_street.shape[0]>0):
            search_num = search_street[search_street.loc[:,'Full_Address'].str.contains(r'\b{0}\b'.format(mprn_house_no),regex=True)]
            if (search_num.shape[0]==1 or search_street.shape[0]==1):
                row=match(row,search_num,'MATCH')
            elif (len(search_num['SMALL_AREA_REF'].unique()) == 1 or len(search_street['SMALL_AREA_REF'].unique()) == 1):
                if (len(search_num['SMALL_AREA_REF'].unique()) == 1 ):
                    row = match(row, search_num, 'SAME_SA')
                else:
                    row = match(row, search_street, 'SAME_SA')
            elif search_num.shape[0]>0:
                row = match(row, search_num, 'MANY RESULTS')
            else:
                num = re.search(r'[0-9]+',mprn_house_no).group()
                search_num = search_street[search_street.loc[:,'Full_Address'].str.contains(r'\b{0}\b'.format(num),regex=True)]
                if (search_num.shape[0] == 1 or search_street.shape[0] == 1):
                    row = match(row,search_num,'MATCH_not100%')
                elif (len(search_num['SMALL_AREA_REF'].unique()) == 1 or len(search_street['SMALL_AREA_REF'].unique()) == 1):
                    if (len(search_num['SMALL_AREA_REF'].unique()) == 1):
                        row = match(row, search_num, 'SAME_SA_not100')
                    else:
                        row = match(row, search_street, 'SAME_SA_not100')
                elif search_num.shape[0] > 0:
                    num_match = search_num[search_num.loc[:, 'Status'] != 'FOUND MATCH']
                    if (num_match.shape[0] == 1):
                        row = match(row, num_match,'MATCH')
                    else:
                        # Checking if it matches
                        last_search = search_num[search_num.loc[:, 'Full_Address'].str.contains(r'\b{0} {1}\b'.format(num, street))]
                        if (last_search.shape[0]):
                            row = match(row, last_search,'MATCH')
                        else:
                            if (len(search_num['SMALL_AREA_REF'].unique()) == 1):
                                row = match(row, search_num, 'SAME_SA')
                            else:
                                row = fuzzy_process(search_num, row, num + " " + street)
                else:
                    other_way=True
        else:
            other_way=True
        if (other_way):
            row = search_MPRN(row, D4_geo_num_df,df_thoroughfare)
    except Exception as ex:
        print(type(ex))  # the exception instance # arguments stored in .args
        print(ex)
        print row
    return row

def process_each_category(D4_dwelling_df,D4_geo_df):
    # Group starts with numbers execpt
    # Still have <digit><letter>
    D4_dwelling_df = D4_dwelling_df.replace(r'\b[NUMBER|UNIT]\b', '', inplace=False, regex=True)
    D4_dwelling_df['Dwelling AddressLine1'] = D4_dwelling_df['Dwelling AddressLine1'].apply(lambda x: x.strip())
    D4_dwelling_num_only_df = D4_dwelling_df[(D4_dwelling_df.loc[:, 'Dwelling AddressLine1'].str.contains(r'\b^\d+\b',na=False,regex=True)) & ~D4_dwelling_df.loc[:,'Dwelling AddressLine1'].str.contains(
        r'\bAPARTMENT|FLAT|BLOCK\b', na=False, regex=True)]
    D4_geo_num_df = D4_geo_df[D4_geo_df.loc[:, 'SUB_BUILDING_NAME'].str.contains(r'\b[0-9]+', regex=True) | D4_geo_df.loc[:,'BUILDING_NUMBER'].str.contains(r'\b[0-9]+', regex=True)]
    df_thoroughfare_geo_num = pd.DataFrame({'THOROUGHFARE': D4_geo_num_df['THOROUGHFARE'].unique()})

    # Including APARMENT(S)/FLAT
    D4_dwelling_num_withAPART_df = D4_dwelling_df[(D4_dwelling_df.loc[:, 'Dwelling AddressLine1'].str.contains(
        r'\b^\d+\b', na=False, regex=True)) & D4_dwelling_df.loc[:, 'Dwelling AddressLine1'].str.contains(
        r'\bAPARTMENT|FLAT|BLOCK\b', na=False, regex=True)]
    D4_dwelling_numm_withNOAPART_df = D4_dwelling_num_withAPART_df.replace(r'\b[APARTMENTS|FLAT|APARTMENT]\b', '', regex=True)
    D4_dwelling_numm_withNOAPART_df['Dwelling AddressLine1'] = D4_dwelling_numm_withNOAPART_df['Dwelling AddressLine1'].apply(lambda x: x.strip())
    #D4_geo_num_df_withAPART = D4_geo_df[D4_geo_df.loc[:, 'SUB_BUILDING_NAME'].str.contains(r'\b[0-9]+\b', regex=True)]
    D4_geo_num_df_withAPART = D4_geo_df
    df_thoroughfare_geo_APART = pd.DataFrame({'THOROUGHFARE': D4_geo_num_df_withAPART['THOROUGHFARE'].unique()})
    # <Digit><Letter>
    D4_dwelling_num_letter_df = D4_dwelling_df[
        (D4_dwelling_df.loc[:, 'Dwelling AddressLine1'].str.contains(r'\b^[0-9]+[A-Z]+\b', na=False, regex=True))]

    # Letter stands first
    D4_dwelling_letters_only_df = D4_dwelling_df[
        (D4_dwelling_df.loc[:, 'Dwelling AddressLine1'].str.contains(r'^[A-Z]+\b', na=False, regex=True))]
    D4_geo_letters_df = D4_geo_df
    df_thoroughfare_geo_letter = pd.DataFrame({'THOROUGHFARE': D4_geo_letters_df['THOROUGHFARE'].unique()})
    # <Letter><Digit
    D4_dwelling_letters_digit_df = D4_dwelling_df[
        (D4_dwelling_df.loc[:, 'Dwelling AddressLine1'].str.contains(r'^[A-Z]+[0-9]+\b', na=False, regex=True))]


    #filter = D4_dwelling_letters_only_df[D4_dwelling_letters_only_df.loc[:,'Dwelling AddressLine1'].str.contains(r'\bWELLINGTON\b',regex=True)]
   # filter.iloc[0]['Dwelling AddressLine1']

    tqdm.pandas()
    print '     Dealing with only num or building:'
    D4_dwelling_num_only_df = D4_dwelling_num_only_df.progress_apply(search_num_first, args=(D4_geo_num_df,df_thoroughfare_geo_num,), axis=1)
    print '     Dealing with building:'
    D4_dwelling_numm_withNOAPART_df = D4_dwelling_numm_withNOAPART_df.progress_apply(search_num_first, args=(D4_geo_num_df_withAPART,df_thoroughfare_geo_APART,), axis=1)
    print '     Dealing with group contain <num><letter>'
    D4_dwelling_num_letter_df = D4_dwelling_num_letter_df.progress_apply(search_num_letter, args=(D4_geo_num_df,df_thoroughfare_geo_num,), axis=1)
    print '     Dealing with group starting with letters:'
    D4_dwelling_letters_only_df = D4_dwelling_letters_only_df.progress_apply(search_letter_first, args=(D4_geo_letters_df,df_thoroughfare_geo_letter,), axis=1)

    D4_dwelling_df.update(D4_dwelling_num_only_df)
    D4_dwelling_df.update(D4_dwelling_numm_withNOAPART_df)
    D4_dwelling_df.update(D4_dwelling_num_letter_df)
    D4_dwelling_df.update(D4_dwelling_letters_only_df)

    return D4_dwelling_df

def main():
    start_time = time.time()
    print "Initializing data"
    #C:/Users/MBohacek/AAA_PROJECTS/Pham_geocoding/data_PhamMatching/
    #C:/Users/pphuc/Desktop/Docs/Current Using Docs/
    path = os.path.join('C:/Users/pphuc/Desktop/Docs/Current Using Docs/')

    dwelling_df = pd.read_csv('Reformat2.csv',skipinitialspace=True,low_memory=False).fillna('')
    geo_df = pd.read_csv(path + 'GeoDirectoryData.csv', skipinitialspace=True, low_memory=False).fillna('')
    dwelling_df = dwelling_df.replace(r'[!@#$%&*\_+\-=|\\:\";\<\>\,\.\(\)\[\]{}]', '', inplace=False, regex=True)
    dwelling_df = dwelling_df.replace(r'[\,\.-\/]', ' ', inplace=False, regex=True)
    dwelling_df = dwelling_df.replace(r'\s{2,}', ' ', inplace=False, regex=True)
    dwelling_df['Dwelling AddressLine1'] = dwelling_df['Dwelling AddressLine1'].apply(lambda x: x.strip())
    dwelling_df = fix_misspell(dwelling_df)

    counties = ['CARLOW', 'CAVAN', 'CLARE', 'CORK', 'DONEGAL',
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
    dwelling_df_counties_replace = dwelling_df.replace({'MPRN county': dict_strange_county}, regex=True)
    dwelling_dublin = dwelling_df_counties_replace.groupby('MPRN city')
    geo_dublin =  geo_df.groupby('PRINCIPAL_POST_TOWN')
    dwelling_county= dwelling_df_counties_replace.groupby('MPRN county')
    geo_county =  geo_df.groupby('COUNTY')

    for i in dublin_cities:
        print i
        # if i =='DUBLIN 4':
        #     break
        each_type_dublin = process_each_category(dwelling_dublin.get_group(i),geo_dublin.get_group(i))
        dwelling_df_counties_replace.update(each_type_dublin)

    # dwelling_df_counties_replace = dwelling_df_counties_replace[['Dwelling Address','Dwelling AddressLine1','Dwelling AddressLine2','Dwelling AddressLine3','MPRN Address','MPRN unit no','MPRN house no','MPRN street','MPRN address4','MPRN city','MPRN county','Status','Percent_Match','Geo_Address']]
    # dwelling_df_counties_replace.to_csv(path_or_buf='Checking_Dublin_1_to_3.csv', index=None, header=True)

    for j in counties:
        print j
        # if (j == 'CAVAN'):
        #     break
        each_type_county = process_each_category(dwelling_county.get_group(j), geo_county.get_group(j))
        dwelling_df_counties_replace.update(each_type_county)

    dwelling_df_counties_replace.to_csv(path_or_buf='Reformat_new14.csv', index=None, header=True)
    print 'Done! from ', time.asctime( time.localtime(start_time)),' to ',time.asctime( time.localtime(time.time()))

if __name__ == '__main__':
    main()


