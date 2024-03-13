# Code for converting Arctic Net Cruise data into pyap usable format

import gsw
import netCDF4 as nc
import numpy as np
import zipfile
from bs4 import BeautifulSoup as bs
import requests
import re
import os
import glob
import pandas as pd
import seawater as sw
import xarray as xr

from data_conversion_functions import write_to_netcdf

# Set wd
working_directory = ('/home/fid000/WORK7/ANALYSIS/model_evaluation/DATA/ArcticNetCruises/') 
os.chdir(working_directory)

# Download zipped files from uVic aeolus folders
URL = "https://aeolus.seos.uvic.ca/~jlanger/Datasets_Observations/Raw/Arctic Net Cruises/WD/"

def get_soup(URL):
    return bs(requests.get(URL).text, 'html.parser')

# Uncomment the following lines if you need to redownload and unzip the files
#for link in get_soup(URL).findAll("a", attrs={"href": re.compile(".zip")}):
#    file_link = link.get('href')
#    print(file_link)

#    with open(link.text, 'wb') as file: 
#        reponse = requests.get(URL + file_link)
#        file.write(reponse.content)

# Unzip each downloaded folder
#for file in os.listdir(working_directory):
#    if zipfile.is_zipfile(file):
#        with zipfile.ZipFile(file) as item:
#            item.extractall()

# Run for loop to extract netcdf vars needed and write to netcdf 

flist = glob.glob(os.path.join(working_directory, '*.int'))
flist.sort()

saveDir = '/home/fid000/WORK7/ANALYSIS/model_evaluation/DATA/ArcticNetCruises/CTD/'

#### trying some of jo's code

def metacleaner(meta):
    mdict = {}
    for i in range(0,len(meta)):
        fu = str(meta.iloc[i,0])
        if len(fu) > 2 :
            fu = fu.split(':',1)
            mdict[fu[0][2:]] = fu[1]
        else:
            pass

    mdict['Latitude'] = float(mdict['Initial_Latitude [deg]'])
    mdict['Longitude'] = float(mdict['Initial_Longitude [deg]'])

    # get the Station identifier: 
    ts = pd.to_datetime(mdict['Start_Date_Time [UTC]'])
    year =ts.strftime('%Y')
    month = ts.strftime('%m')
    day = ts.strftime('%d')
    minutes = ts.strftime('%M')
    seconds = ts.strftime('%S')
    #cruise = str(ts.strip('Cruise_Number'))
    #assign a unique Station identifyier: YYYY-MM_Source_type_filename-or-other
    mdict['Stat_id'] = year+'-'+month+'_AMS_CDT_'+mdict['Cruise_Number'].replace(" ", "")+'_'+ mdict['Cast_Number  '].replace(" ", "")
    mdict['time'] = year+'-'+month+'-'+day+minutes+':'+seconds
    return(mdict)

#### calculate depth from pressure using Seawater 
def depth_calc(ds, dct):
    # convert pressure to depth
    mylist = list(ds)
    # make sure data is numeric/float
    for i in mylist:
        ds[i] = pd.to_numeric(ds[i])
    # use seawater to calculate depth
    depth = sw.dpth(p = ds['Pres'], lat = dct['Latitude'])
    ds['Depth'] = depth

    return(ds)

### wrapper to create individual arrays
def create_array(dat, dct):
    ds = xr.Dataset(dat)
    ds = ds.assign_coords(coords={'Station': dct['Stat_id']})
    ds = ds.assign(Cruise_number=dct['Cruise_Number'], Cruise_Name = dct['Cruise_Name'], Cast_Number= dct['Cast_Number  '], Date_Time= dct['Start_Date_Time [UTC]'],
            original_Latitude= dct['Initial_Latitude [deg]'], original_Longitude= dct['Initial_Longitude [deg]'],Latitude=   dct['Latitude'],Longitude =  dct['Longitude'],
            Stat_id = dct['Stat_id'], time = dct['Start_Date_Time [UTC]'], sounding = dct['Sounding [m]'])
    try: 
        ds = ds.assign(original_Station=  dct['Station '])
    except:
        try:
            ds = ds.assign(original_Station=  dct['Station'])
        except: 
            ds = ds.assign(original_Station = 'No_original_Station')
    return(ds)



def array_cleaner(array):
    ''''renames a bunch of variables to an uniform thing'''''
    fo = list(array)
    if 'PRES' in fo:   array.rename(columns = {'PRES':'Pres' }, inplace = True)
    else: pass
    if 'TE90' in fo: array.rename(columns ={'TE90':'Temp'}, inplace = True)
    else: pass
    if 'FLOR' in fo: array.rename(columns ={'FLOR':'Fluo' }, inplace = True)
    else: pass
    if 'TRAN' in fo: array.rename(columns ={'TRAN':'Trans'}, inplace = True)
    else: pass
    if 'NTRA' in fo: array.rename(columns ={'NTRA':'NO3'}, inplace = True)
    else: pass
    if 'PSAR' in fo: array.rename(columns ={'PSAR':'Par'}, inplace = True)
    else: pass
    if 'SPAR' in fo: array.rename(columns ={'SPAR':'SPar'}, inplace = True)
    else: pass
    if 'PSAL' in fo: array.rename(columns ={'PSAL':'Sal'}, inplace = True)
    else: pass
    if 'OXYM' in fo: array.rename(columns ={'OXYM':'O2'}, inplace = True)
    else: pass
    if 'SIGM' in fo: array.rename(columns ={'SIGM':'Dens'}, inplace = True)
    else: pass
    if 'SPVA' in fo: array.rename(columns ={'SPVA':'Svan'}, inplace = True)            
    else: pass
    if 'svan' in fo: array.rename(columns ={'svan':'Svan'}, inplace = True)
    else: pass
    if 'VAIS' in fo: array.rename(columns ={ 'VAIS':'N2' }, inplace = True)
    else: pass
    if 'SIGT' in fo: array.rename(columns ={ 'SIGT':'Sigt' }, inplace = True)
    else: pass
    if 'POTM' in fo: array.rename(columns ={ 'POTM':'Theta' }, inplace = True)
    else: pass
    if 'SIGP' in fo: array.rename(columns ={ 'SIGP':'Sigthe' }, inplace = True)
    else: pass
    if 'sigthe' in fo: array.rename(columns ={ 'sigthe':'Sigthe' }, inplace = True) 
    else: pass
    if 'FRET' in fo: array.rename(columns ={ 'FRET':'FreezT' }, inplace = True)
    else: pass
    if 'ASAL' in fo: array.rename(columns ={ 'ASAL':'Asal' }, inplace = True)  
    else: pass
    if 'CONT' in fo: array.rename(columns ={ 'CONT':'Cont' }, inplace = True)
    else: pass
    if 'D_CT' in fo: array.rename(columns ={ 'D_CT':'D_ct' }, inplace = True)
    else: pass
    if 'D0CT' in fo: array.rename(columns ={ 'D0CT':'D0ct'}, inplace = True)
    else: pass
    if 'sigt' in fo: array.rename(columns ={'sigt':'Sigt'  }, inplace = True)
    else: pass
    if 'theta' in fo: array.rename(columns ={'theta':'Theta'  }, inplace = True)
    else: pass
    if'CDOM' in fo: array.rename(columns ={'CDOM': 'Cdom' }, inplace = True)
    else: pass 
    if 'FreezT-'in fo: array.rename(columns ={'FreezT-': 'FreezT' }, inplace = True)
    else:pass
    return( array)




#for f in range(0, len(flist)):
 
for f in flist:
    test = pd.read_fwf(f, encoding = 'latin-1')#convert to dataframe
    try:
        #test['Stat_name'] =  float(test['Original_Filename'])
        dead_rows = test['%'].dropna()
        c = len(dead_rows)+1
        data = pd.read_fwf(f, encoding = 'latin-1', skiprows = c)
        lendat = len(data)
        meta = pd.read_table(f, skiprows = list(range(c, lendat+c+1)), header = None, encoding = 'latin-1')
    except Exception as e:
        print(e, 'This dataset needs to be fixed by hand')
        print(f)
     
    mdict = metacleaner(meta)
    data = data.drop(0).reset_index()
    data = data.drop(['index'], axis = 1)
    data = array_cleaner(data)
    
    #data = depth_calc(ds = data, dct = mdict)

    ds = create_array(dat=data, dct = mdict)
    print(ds)
    

    #for i in range(1, len(ds)):
    #time = str(ds.time.values)
    #time = time.strip()
    time = pd.to_datetime(ds.time.values)
    month = time.strftime('%m')
    print(time)
    print(type(time))
    lat = ds.Latitude.values
    lon = ds.Longitude.values
    T = ds.Temp.values
    SR = ds.Sal.values
    depth = ds.sounding.values
    P = ds.Pres.values
    fn_station = str(ds.Stat_id.values)
    fn_station = fn_station.strip()
    print(fn_station)

    SP = gsw.conversions.SP_from_SR(SR)
    absSal = gsw.conversions.SA_from_SP(SP, P, lon, lat)
    consTemp = gsw.conversions.CT_from_t(absSal, T, P)
    pDen = gsw.rho(absSal, consTemp, P)
    #print("fn_station", fn_station)
    #print("saveDir", saveDir, "temp", T)
    print("saveDir", saveDir,"fn_station", fn_station, "time", time, "P", P, "T", T, "consTemp", consTemp, "SR", SR, "absSal", absSal, "pDen", pDen, "depth", depth, "lat",lat,"lon",lon)
    outfile = write_to_netcdf().CTD_Cast(saveDir,fn_station,time,P,T,consTemp,SR,absSal,pDen,depth,lat,lon)
    print("Saved ",outfile) 
















