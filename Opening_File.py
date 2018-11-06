import pandas as pd
import os
import numpy as np


def main():
    path = os.path.join('C:/Users/pphuc/Desktop/Docs/Current Using Docs/')

    #dwelling = pd.read_csv(path+'.csv', skipinitialspace=True, low_memory=False).fillna('')
    dwelling = pd.read_csv(path+'ALL.csv', skipinitialspace=True, low_memory=False).fillna('')
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

    #dwelling_df = dwelling[~dwelling.loc[:,'Status'].str.contains(r'MATCH|MATCH_Fuzzy|MATCH_not100%|SAME_SA|SAME_SA_not100%|CANT FIND|MANY RESULTS|SAME_SA_NO_NUMs',regex=True)]
    dwelling_df = dwelling[dwelling.loc[:, 'Status'].str.contains(r'CANT FIND', regex=True)]
    #dwelling_df = dwelling[dwelling.loc[:, 'Status'].str.contains(r'MATCH|MATCH_Fuzzy|MATCH_not100%|SAME_SA|SAME_SA_not100%|SAME_SA_NO_NUMs', regex=True)]
    #dwelling_df = dwelling[dwelling['MPRN city'].isin(['DUBLIN 3'])]
    #dwelling_df = dwelling[['PRINCIPAL_POST_TOWN']== 'DUBLIN 3']
    #sample_df = dwelling_df.sample(n=4000)
    #sample_df = sample_df.apply(pick_rand)

    # dwelling_df = dwelling[dwelling.loc[:,'MPRN house no']==pick_rand'']
    # dwelling_df = dwelling_df[dwelling_df.loc[:,'MPRN unit no']=='']
    dwelling.shape[0]
    dwelling_df.shape[0]

    dwelling_df.to_csv(path_or_buf='CANT_FIND.csv', index=None, header=True)
    print 'Hi'


if __name__=='__main__':
    main()