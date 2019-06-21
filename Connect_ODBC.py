import pyodbc
import pandas as pd
conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=S:\GeoDirectory\Q4 2018\SEAII_ACCESS10_M_Q418.accdb;')
conn = pyodbc.connect('DSN=Access;UID=;PWD=')
cursor = conn.cursor()
sql = "select g.BUILDING_ID,g.[ADDRESS_POINT_ID],g.[ADDRESS_REFERENCE],g.[PERSONAL_NAME],g.[ORGANISATION_NAME],g.[DEPARTMENT],g.[SUB_BUILDING_NAME],g.[BUILDING_NAME],g.[BUILDING_NUMBER],g.[BUILDING_GROUP_NAME],g.[THOROUGHFARE],g.[SECONDARY_THOROUGHFARE],g.[LOCALITY],g.[SECONDARY_LOCALITY],g.[PRINCIPAL_POST_TOWN],g.[COUNTY],g.[EIRCODE],g.[ADDR_LINE_1],g.[ADDR_LINE_2],g.[ADDR_LINE_3],g.[ADDR_LINE_4],g.[ADDR_LINE_5],g.[ADDR_LINE_6],g.[ADDR_LINE_7],g.[ADDR_LINE_8],g.[ADDR_LINE_9],g.[ADDR_LINE_10],sa.SMALL_AREA_REF,b.LATITUDE,b.LONGITUDE from (GEOGRAPHIC_FORMAT g left join  BUILDINGS b on g.BUILDING_ID = b.BUILDING_ID) left join SMALL_AREAS sa on b.SMALL_AREA_ID = sa.SMALL_AREA_ID;"
# cursor.execute(sql)
geo_df = pd.read_sql(sql,conn)
cursor.close()