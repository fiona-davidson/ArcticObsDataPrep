# Converter for CROW dataset from the Canadian Rangers Ocean Watch project, https://data.nwtresearch.com/Scientific/15441
# Code originally taken from python-analysis-package/etc/date_conversion/convert_BCferries.py and other scripts from this folder
# Code for metadata fixing taken largely from Jo Langer's code https://github.com/JohannaLaenger/Data_cleaning_NAA_grid/blob/main/File_generation/CROW.ipynb

import gsw
import netCDF4 as nc
import numpy as np
import xarray as xr
from data_conversion_functions import write_to_netcdf

infile = '/home/fid000/WORK7/ANALYSIS/model_evaluation/DATA/CROW/data_from_All_CROW.nc'
saveDir = '/home/fid000/WORK7/ANALYSIS/model_evaluation/DATA/CROW/CTD_qc_test/'

ds = xr.open_dataset(infile)

# Fix station ID situation, currently there's three metavars that link to N_STATIONS and they are string20 format
# get rid of the byte-coded strings like b'fnkjeshrg'
cr = ds.metavar1.values
st = ds.metavar2.values
ty = ds.metavar3.values
cruise = []
station = []
typs = []
for i in range(0,len(cr)):
      cruise.append(cr[i].decode())
      station.append(st[i].decode())
      typs.append(ty[i].decode())
ds['Cruise'] = ('N_STATIONS' , cruise) 
ds['Station']= ('N_STATIONS' , station)
ds['Type'] =  ('N_STATIONS' ,typs)
# Convert longitude from 0,360 to -180-180
ds['longitude'] = ds['longitude'].astype(float)
ds['longitude'] = ds['longitude'] - 360

# Sort out Metadata
Station_Name = []
for i in range(0,len(ds.N_STATIONS)):
    Stat_name =str(ds.Station[i].values)
    Stat_nr = str(ds.Cruise[i].values)
    mnth = ds.date_time[i].dt.strftime('%m')
    yer = ds.date_time[i].dt.strftime('%Y')
    day = ds.date_time[i].dt.strftime('%D') 
    Station_Name.append(Stat_name+'_')#Stat_nr +'_'+
#Station_Name  
ds['Stat_id'] = ds['date_time'].dt.strftime('%Y')+'-'+ds['date_time'].dt.strftime('%m') + '_CROW_CTD_' +Station_Name+ds['date_time'].dt.strftime('%d') 
ds.dropna(dim="N_SAMPLES", how="any")
#print(ds)

# Collect data based on N_STATIONS, making one .nc file for each Station, each station has a number of samples 'N_SAMPLES' 
for i in range(0,len(ds.Stat_id)):
    time = ds.date_time[i].values
    lat = ds.latitude[i].values
    lon = ds.longitude[i].values
    T = ds.var7.where(ds['var7_qc'] == 48)[i,:]
    print("T", T, np.shape(T))
    SR = ds.var6.where(ds['var6_qc'] == 48)[i,:]
    #print(T, "T", np.shape(T), "Salinity", SR)
    depth = ds.metavar4[i].values
    depth[depth>=999]=np.nan
    P = ds.var1.where(ds['var1_qc'] == 48)[i,:]

    SP = gsw.conversions.SP_from_SR(SR)
    absSal = gsw.conversions.SA_from_SP(SP, P, lon, lat)
    consTemp = gsw.conversions.CT_from_t(absSal, T, P)
    pDen = gsw.rho(absSal, consTemp, P)
    
    # Station modified
    fn_station = 'CROW' + ds.Stat_id[i].values
    #print("SP from SR", SP)
    # add print statment to check variable values
    #print("len(T)", len(T), T)
    SR=SR[~np.isnan(SR)]
    P=P[~np.isnan(P)]
    depth=depth[~np.isnan(depth)]
    SP=SP[~np.isnan(SP)]
    absSal=absSal[~np.isnan(absSal)]
    consTemp=consTemp[~np.isnan(consTemp)]
    pDen=pDen[~np.isnan(pDen)]
    T=T[~np.isnan(T)]

    print("len(T)", len(T), T)
    if len(T)>2:
        #print("saveDir", saveDir,"fn_station", fn_station, "time", time, "P", P, "T", T, "consTemp", consTemp, "SR", SR, "absSal", absSal, "pDen", pDen, "depth", depth, "lat",lat,"lon",lon)
        outfile = write_to_netcdf().CTD_Cast(saveDir,fn_station,time,P,T,consTemp,SR,absSal,pDen,depth,lat,lon)
        #print("Saved ",outfile)
    else:
        print("No data in this file")
