def match(row,df):
    row['New_Geo_Address'] = df.iloc[0]['Full_Address']
    row['New_ADDRESS_REFENENCE'] = df.iloc[0]['ADDRESS_REFERENCE']
    row['New_EIRCODE'] = df.iloc[0]['EIRCODE']
    row['New_SMALL_AREA_REF'] = df.iloc[0]['SMALL_AREA_REF']
    return row

def fix(row,dict,geo_df):
    if (row['DwellingData_id'] in dict):
        df_geo_add_ref = geo_df[geo_df['ADDRESS_REFERENCE'].isin(dict[float(row['DwellingData_id'])])]
        search_city = df_geo_add_ref[df_geo_add_ref.loc[:,'PRINCIPAL_POST_TOWN']==row['MPRN city']]
        if (search_city.shape[0]>0):
            if (search_city.shape[0]==1):
                if search_city.iloc[0]['ADDRESS_REFERENCE']==row['ADDRESS_REFERENCE']:
                    row['New_Change']=False
                else:
                    row['New_Change']=True
                    row=match(row,search_city)
            else:
                search_thoroughfare = search_city[search_city.loc[:,'THOROUGHFARE'].str.contains(row['MPRN street']) | search_city.loc[:,'THOROUGHFARE'].str.contains(row['MPRN address4'])]
                if (search_thoroughfare.shape[0]>0):
                    if (search_thoroughfare.shape[0]==1):
                        if search_thoroughfare.iloc[0]['ADDRESS_REFERENCE'] == row['ADDRESS_REFERENCE']:
                            row['New_Change'] = False
                        else:
                            row['New_Change'] = True
                            row = match(row, search_thoroughfare)
                    else:
                        row['New_Change'] = True
                        row = match(row, search_thoroughfare)
                        #row['List_results']=list(search_thoroughfare.ADDRESS_REFERENCE)
                else:
                    row['New_Change'] = False
                    #row['List_results'] = list(search_city.ADDRESS_REFERENCE)
        else:
            row['New_Change'] = False
    else:
        row['New_Change']=False
    return row


def dealing_with_MANY_RESULTS(dwelling_df,geo_df,dict):
    dwelling_df['New_Change'] = ""
    dwelling_df['New_EIRCODE']=""
    dwelling_df['New_SMALL_AREA_REF']=""
    dwelling_df['New_Geo_Address']=""
    dwelling_df['List_results']=""
    dwelling_df['New_ADDRESS_REFENENCE']=""
    geo_df['Full_Address'] = (geo_df['ADDR_LINE_1'] + " " + geo_df['ADDR_LINE_2'] + " " + geo_df['ADDR_LINE_3'] + " " + \
                             geo_df['ADDR_LINE_4'] + " " + geo_df['ADDR_LINE_5'] + " " + geo_df['ADDR_LINE_6'] + " " + \
                             geo_df['ADDR_LINE_7'] + " " + geo_df['ADDR_LINE_8'] + " " + geo_df['ADDR_LINE_9'] + " " + \
                             geo_df['ADDR_LINE_10'])
    dwelling_df = dwelling_df.apply(fix,args=(dict,geo_df,),axis=1)

    return dwelling_df

