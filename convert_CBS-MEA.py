# Code to convert datasets from 2017-2019 in Amundsen Gulf from CBS-MEA cruises 18DN20170803, 18DN20180803, 18DN20190802

import gsw
from datetime import datetime
import datetime as dt # for date handling
import netCDF4 as nc
import numpy as np
import xarray as xr
import pandas as pd
import dateutil.parser as parser
import os
import glob
from data_conversion_functions import write_to_netcdf

save_dir = '/home/fid000/WORK7/ANALYSIS/model_evaluation/DATA/Michel/CTD/'

df17 = pd.read_excel('/home/fid000/WORK7/ANALYSIS/model_evaluation/DATA/Michel/2017-DIC-NSteiner.xlsx', sheet_name = '2017-DIC', nrows = 254)
df18 = pd.read_excel('/home/fid000/WORK7/ANALYSIS/model_evaluation/DATA/Michel/2018-DIC-NSteiner.xlsx', sheet_name = 'CBS-MEA 2018 DIC')
df19 = pd.read_excel('/home/fid000/WORK7/ANALYSIS/model_evaluation/DATA/Michel/2019-DIC-NSteiner.xls', sheet_name = 'CBS-MEA 2019 DIC')

# Have to edit df19 to change salinity column name from Sal (CTD) to match df17 and df18 salinity column called Sal (CTD-btl)
# Also temp is different across years... 2018 and 2019 'Temp in situ (ºC) (CTD)' 
# Bottom depth, in 2017 its called Bottom, in 2018 and 19 its called Btm
df17 = df17.rename(columns={'Sal (CTD-btl)': 'Sal (CTD)', 'Temp in situ (ºC) (CTD-btl)': 'Temp in situ (ºC) (CTD)'})


# export these as files to put into the flist
df17.to_excel("/home/fid000/WORK7/ANALYSIS/model_evaluation/DATA/Michel/DF/2017.xlsx")
df18.to_excel("/home/fid000/WORK7/ANALYSIS/model_evaluation/DATA/Michel/DF/2018.xlsx")
df19.to_excel("/home/fid000/WORK7/ANALYSIS/model_evaluation/DATA/Michel/DF/2019.xlsx")


working_directory = '/home/fid000/WORK7/ANALYSIS/model_evaluation/DATA/Michel/DF'
os.chdir(working_directory)
flist = glob.glob(os.path.join(working_directory, '*.xlsx'))
flist.sort
#print(type(flist))

for f in flist:
    ds = pd.read_excel(f)
    ds['Station'] = ds['Station'].astype("string").replace(" ", "")
    test = pd.to_datetime(ds['Date']).dt.date
    #print(test, "test")
    
    # Change lat long format from degrees into decimals using regex
    pattern = r'(?P<d>[\d\.]+).*?(?P<m>[\d\.]+).*?(?P<s>[\d\.]+)'
    print("Latitude", ds['Latitude'])
    dms = ds['Latitude'].str.extract(pattern).astype(float)
    ds['LATITUDE'] = dms['d'] + dms['m'].div(60) + dms['s'].div(3600)
    dms = ds['Longitude'].str.extract(pattern).astype(float)
    ds['LONGITUDE'] = dms['d'] + dms['m'].div(60) + dms['s'].div(3600)
  
    # For loop to extract profiles based on previously created StationID
    Station = ds.Station.values
    station0 = Station[0]
    TEMP=[]
    SAL=[]
    D=[]
    PRES=[]
    lat = ds.LATITUDE.values
    print("lat", lat)
    lon = ds.LONGITUDE.values
    SR = ds['Sal (CTD)'].values
    T = ds['Temp in situ (ºC) (CTD)'].values
    depth = ds['Depth [m]'].values[np.where((ds['Target property'] == 'Btm') | (ds['Target property'] == 'Bottom'))]
   # print("depth", np.shape(depth), depth)
    P = ds['Pressure (db)'].values
    count=0 
    for i in range(0,len(Station)):
        station1 = Station[i]
        time = test[i]
        #print(time, station1, i, station0)
        if station1==station0:
            TEMP.append(T[i])
            SAL.append(SR[i])
            D.append(depth[count])
            #print(D)
            PRES.append(P[i])
        else:
            #save the previos profile and initialize arrays for the next one 
            TEMP=np.array(TEMP)
            SAL=np.array(SAL)
            D=depth[count]
            count=count+1
            PRES=np.array(PRES)
            #print(TEMP,station1, station0)
            #print(SAL,station1,station0)
            
            SP = gsw.conversions.SP_from_SR(SAL)
            absSal = gsw.conversions.SA_from_SP(SP, PRES, lon[i], lat[i])
            consTemp = gsw.conversions.CT_from_t(absSal, TEMP, PRES)
            pDen = gsw.rho(absSal, consTemp, PRES)
            #print(station0) 
            #print(np.shape(consTemp), np.shape(PRES))
            outfile = write_to_netcdf().CTD_Cast(save_dir, station0, time, PRES, TEMP, consTemp, SAL, absSal, pDen, D, lat[i], lon[i])
            TEMP=[]
            SAL=[]
            D=[]
            PRES=[]
            station0=station1


        #print(np.shape(Station), np.shape(T), np.shape(P))
        #outfile = write_to_netcdf().CTD_Cast(save_dir, Station, time, P, T, consTemp, SR, absSal, pDen, depth, lat, lon)
