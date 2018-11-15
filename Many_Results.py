def match(row,df):
    row['Geo_Address'] = df.iloc[0]['Full_Address']
    row['ADDRESS_REFERENCE'] = df.iloc[0]['ADDRESS_REFERENCE']
    row['BUILDING_ID'] = df.iloc[0]['BUILDING_ID']
    row['EIRCODE'] = df.iloc[0]['EIRCODE']
    row['SMALL_AREA_REF'] = df.iloc[0]['SMALL_AREA_REF']
    row['LATITUDE'] = df.iloc[0]['LATITUDE']
    row['LONGITUDE'] = df.iloc[0]['LONGITUDE']
    return row

def fix(row,dict,geo_df):
    df_geo_add_ref = geo_df[geo_df['ADDRESS_REFERENCE'].isin(dict[float(row['DwellingData_id'])])]
    search_city = df_geo_add_ref[df_geo_add_ref.loc[:,'PRINCIPAL_POST_TOWN']==row['MPRN city']|df_geo_add_ref.loc[:,'SECONDARY_LOCALITY']==row['MPRN city']|df_geo_add_ref.loc[:,'LOCALITY']==row['MPRN city']]
    if (search_city.shape[0]>0):
        if (search_city.shape[0]==1):
            if search_city.iloc[0]['ADDRESS_REFERENCE']==row['ADDRESS_REFERENCE']:
                row['New_Change']=False
            else:
                row['New_Change']=True
                row=match(row,search_city)
        else:
            search_thoroughfare = search_city[search_city.loc[:,'THOROUGHFARE']==row['MPRN street'] |search_city.loc[:,'THOROUGHFARE']==row['MPRN MPRN address4']]
            if (search_thoroughfare.shape[0]>0):
                if (search_thoroughfare.shape[0]==1):
                    if search_thoroughfare.iloc[0]['ADDRESS_REFERENCE'] == row['ADDRESS_REFERENCE']:
                        row['New_Change'] = False
                    else:
                        row['New_Change'] = True
                        row = match(row, search_thoroughfare)
                else:
                    row['List_results']=list(search_thoroughfare.Full_Address)
            else:
                row['List_results'] = list(search_city.Full_Address)
    else:
        row['New_Change']=False
    return row


def dealing_with_MANY_RESULTS(dwelling_df,geo_df,dict):
    dwelling_df['New_Change'] = ""
    dwelling_df['List_results']=""
    dwelling_df = dwelling_df.apply(fix,args=(dict,geo_df))

    return dwelling_df