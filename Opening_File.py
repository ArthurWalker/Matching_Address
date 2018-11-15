import pandas as pd
import os
import numpy as np
import pickle
from Many_Results import dealing_with_MANY_RESULTS

def main():
    path = os.path.join('C:/Users/pphuc/Desktop/Docs/Current Using Docs/')

    dwelling = pd.read_csv(path+'File 15-11/Results_14_11.csv', skipinitialspace=True, low_memory=False).fillna('')

    geo= pd.read_csv(path+'Sample Data/GeoDirectoryData.csv', skipinitialspace=True, low_memory=False).fillna('')

    #dublin_cities = ['DUBLIN 1', 'DUBLIN 2', 'DUBLIN 3', 'DUBLIN 4', 'DUBLIN 5', 'DUBLIN 6', 'DUBLIN 7', 'DUBLIN 8',
    #                  'DUBLIN 9', 'DUBLIN 10', 'DUBLIN 11', 'DUBLIN 12', 'DUBLIN 13', 'DUBLIN 14', 'DUBLIN 15',
    #                  'DUBLIN 16', 'DUBLIN 17', 'DUBLIN 18', 'DUBLIN 20', 'DUBLIN 22','DUBLIN 24',
    #                  'DUBLIN 6W']

    #dwelling.shape[0]
    # list_county = ['DUBLIN ']*13
    # for i in range(len(list_county)):
    #     list_county[i]+=str(i+1)
    #
    # result = geo_df[(geo_df['MPRN city'].isin(list_county))]
    # total = result.shape[0]
    #
    # result_perf_match = result.loc[result['Status']==('MATCH')]
    # total_match = result_perf_match.shape[0]
    #
    # result_almost_match = result[result['Status'].isin(['SAME_SA','MATCH_Fuzzy','SAME_SA_NO_NUMs'])]
    # total_result_almost_match = result_almost_match.shape[0]
    #
    # result_fuzzy_match=result[result['Status']=='MATCH_Fuzzy']
    # total_fuzzy = result_fuzzy_match.shape[0]
    #
    #
    # result_not_match = result[result['Status']=='CANT FIND']
    # total_not_match = result_not_match.shape[0]
    #
    #
    #
    # hi = result_fuzzy_match[['Dwelling AddressLine1','Dwelling AddressLine2','Dwelling AddressLine3','Geo_Address']]
    # hi_filter = hi[hi.loc[:,'Dwelling AddressLine1'].str.contains(r'^[0-9]')]
    # hi_filter_total = hi_filter.shape[0]
    #
    # perc_perf_matche = float(total_match)/(total)*100
    # perc_almost_matche = float(total_result_almost_match)/(total)*100

    #dwelling_df = dwelling[~dwelling.loc[:,'Status'].str.contains(r'MATCH|MATCH_Fuzzy|MATCH_not100%|SAME_SA|SAME_SA_not100%|MANY RESULTS|SAME_SA_NO_NUMs|Worst_Fuzzy_Case',regex=True)]
    #dwelling_df = dwelling_df[dwelling_df.loc[:, 'Status'].str.contains(r'CANT FIND', regex=True)]
    #dwelling_df = dwelling[dwelling.loc[:, 'Status'].str.contains(r'SAME SA|SAME SA Worst Fuzzy Case|MANY RESULTS|SAME SA NO NUM', regex=True)]
    #dwelling_df = dwelling[dwelling['MPRN city'].isin(['DUBLIN 1'])]
    dwelling_df = dwelling[dwelling['Status']== 'MANY RESULTS']
    #dwelling_df = dwelling_df[~dwelling_df['UNIQUE_SMALL_AREA_REF'].isin([''])]
    #sample_df = dwelling_df.sample(n=4000)
    #sample_df = sample_df.apply(pick_rand)


    # dwelling_df = dwelling[dwelling.loc[:,'MPRN house no']==pick_rand'']
    # dwelling_df = dwelling_df[dwelling_df.loc[:,'MPRN unit no']=='']

    #dwelling_df = dwelling[dwelling['COUNTY']=='DUBLIN']
    #dwelling.shape[0]
    #dwelling_df.shape[0]
    sample_df = dwelling_df.sample(n=1000)
    #dwelling_df.to_csv(path_or_buf='Results_Blank_Fields_False_MANY_RESULTS.csv', index=None, header=True)
    with open(path+'File 15-11/dict_ADDRESS_REFERENCE.pkl') as f:  # Python 3: open(..., 'rb')
        dict = pickle.load(f)

    new_df = (dealing_with_MANY_RESULTS(sample_df,geo,dict))
    new_df.to_csv(path_or_buf='Fixing_Many_results_flag.csv', index=None, header=True)


if __name__=='__main__':
    main()