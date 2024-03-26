import os
import glob
import numpy as np
import xarray as xr
from data_conversion_functions import read_from_rawfile, write_to_netcdf

infile = '/home/fid000/WORK7/ANALYSIS/model_evaluation/DATA/CROW/data_from_All_CROW.nc'
save_dir = '/home/fid000/WORK7/ANALYSIS/model_evaluation/DATA/CROW/CTD_nut/'

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
    #print(Station_Name)
    #Station_Name  
    #ds['Stat_id'] = ds['date_time'].dt.strftime('%Y')+'-'+ds['date_time'].dt.strftime('%m') + '_CROW_CTD_' +Station_Name
    ds['Stat_id'] = ds['date_time'].dt.strftime('%Y')+'-'+ds['date_time'].dt.strftime('%m') + '_CROW_CTD_' +Station_Name+ds['date_time'].dt.strftime('%d') 
    print(ds.Stat_id)
    ds.dropna(dim="N_SAMPLES", how="any")
    print(ds)


#collect data based on N_STATIONS, making one .nc file for each Station, each station has a number of samples 'N_SAMPLES' 
for i in range(0,len(ds.Stat_id)):
    startT = ds.date_time[i].values
    print(startT)
    lat = ds.latitude[i].values
    lon = ds.longitude[i].values
    dep = ds.metavar4[i].values
    dep[dep>=999]=np.nan
    P = ds.var1[i].values#where(ds['var1_qc'] == 48)[i,:]
    O2 = ds.var5[i].values
    station = 'CROW' + ds.Stat_id[i].values#ds.Stat_id[i].values
    print("we made it to the loop")
    #fn_station, startT, P, O2, N, CHL,DIC,dep, lat, lon = read_from_rawfile().IOS().CTD_Cast_nutrients(i)
    try:
        if np.all(np.isnan(O2)) and np.all(np.isnan(N)) and np.all(np.isnan(CHL)) and np.all(np.isnan(DIC)):
            print('no o2 or No3 or chl in this file')
        else:
            #print('max values of O2 and Nitrate, CHL', np.nanmax(O2), np.nanmax(N), np.nanmax(CHL), np.nanmax(DIC))
            outfile = write_to_netcdf().CTD_Cast_nutrients(save_dir, station, startT, P, O2,  N, CHL,DIC,dep, lat, lon, i)
    except Exception as err:
        print('bad data', err)
