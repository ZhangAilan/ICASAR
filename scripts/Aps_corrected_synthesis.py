#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/01/10
# Function:
#   use the Aps corrected data to synthesis the data
#-------------------------------------------------------------------
import datetime
import numpy as np
import os
import pickle
from scipy.io import loadmat
import numpy.ma as ma

file_path_raw="data/Synthetic_Fault/raw_data/simDatasetsConsiderDefHydroWet"
save_displacemet_r2_path="data/Synthetic_Fault/temp_corrected/displacement_r2.pkl"
save_tbaseline_info_path="data/Synthetic_Fault/temp_corrected/tbaseline_info.pkl"
dem_rsc_path=os.path.join(file_path_raw,"EQA.dem.rsc")
dem_path=os.path.join(file_path_raw,"EQA.dem")
file_path="data/Synthetic_Fault/aps_data/CorrectedIfgs-model6-defoFlag1-wetFlag1-hydroFlag1-iteraNum1-solver2-ueFixMethod0-weightScheme1-shortBt60-shortBtRelax500"

#get the date information
epoch_master_slave_dates_info=loadmat(os.path.join(file_path_raw,"simSAR.mat"))
sar_epoch=epoch_master_slave_dates_info['sar_epoch']
date_format="%Y%m%d"
converted_dates=[]
for i in range(len(sar_epoch)-1):
    start_date=datetime.datetime.strptime(str(sar_epoch[i][0]),date_format).strftime(date_format)
    end_date=datetime.datetime.strptime(str(sar_epoch[i + 1][0]), date_format).strftime(date_format)
    converted_dates.append(f"{start_date}_{end_date}")

#access the data fit the date condition
unw_names=[]
for date_range in converted_dates:
    start_date,end_date=date_range.split('_') 
    unw_name=f"geo_{start_date}-{end_date}.unw.APScorrected"
    unw_names.append(unw_name)
print(unw_names)
print(len(unw_names))

WIDTH=  235
FILE_LENGTH=  207
X_FIRST=   93.4352
X_STEP=    0.0154
Y_FIRST=   41.0972
Y_STEP=   -0.0154

#ifgs数据
displacement_r3={}
displacement_r3_inc=[]
for unw_name in unw_names:
    fullpath=os.path.join(file_path,unw_name)
    with open(fullpath,'rb') as f:
        ifg_data=np.fromfile(f,dtype='>f4').reshape(FILE_LENGTH,WIDTH)
        ifg_data[ifg_data == 0] = np.nan
        displacement_r3_inc.append(ifg_data)
displacement_r3['incremental']=np.array(displacement_r3_inc)


#mask
mask_nan_r3=np.where(np.isnan(displacement_r3['incremental']),True,False)
mask_r2=np.any(mask_nan_r3,axis=0)


#dem
with open(dem_path,'rb') as f:
    dem=np.fromfile(f,dtype='>f4').reshape(FILE_LENGTH,WIDTH)
displacement_r3['dem']=dem


#将displacement_r3转换为displacement_r2
displacement_r2={}
n_ifgs=displacement_r3['incremental'].shape[0]
ifgs_r3_masked=ma.array(displacement_r3['incremental'],mask=ma.repeat(mask_r2[np.newaxis,],n_ifgs,axis=0))
n_pixs=ma.compressed(ifgs_r3_masked[0,]).shape[0]
ifgs_r2=np.zeros((n_ifgs,n_pixs))
for ifg_n,ifg in enumerate(ifgs_r3_masked):
    ifgs_r2[ifg_n,:]=ma.compressed(ifg)

displacement_r2['incremental']=ifgs_r2
displacement_r2['mask']=mask_r2
displacement_r2['dem']=displacement_r3['dem']
displacement_r2['cumulative']=np.cumsum(displacement_r2['incremental'],axis=0)
print(displacement_r2['cumulative'].shape)


#lons && lats
corner_lon=X_FIRST  #经度
corner_lat=Y_FIRST  #纬度
post_lon=X_STEP
post_lat=Y_STEP

def create_lon_lat_meshgrids(corner_lon,corner_lat,post_lon,post_lat,ifg):
    ny,nx=ifg.shape
    x=corner_lon+(post_lon*np.arange(nx))
    y=corner_lat+(post_lat*np.arange(ny))
    xx,yy=np.meshgrid(x,y)
    geocode_info={'lons_mg':xx,
                  'lats_mg':yy}
    return geocode_info

geocode_info=create_lon_lat_meshgrids(corner_lon,corner_lat,post_lon,post_lat,displacement_r2['dem'])
displacement_r2['lons']=geocode_info['lons_mg']
displacement_r2['lats']=geocode_info['lats_mg']


#日期数据
def baseline_from_names(names_list):
    from datetime import datetime
    baselines=[]
    for file in names_list:
        master=datetime.strptime(file.split('_')[-2],'%Y%m%d')
        slave=datetime.strptime(file.split('_')[-1][:8],'%Y%m%d')
        baselines.append(-1*(master-slave).days)
    return baselines

tbaseline_info={}
tbaseline_info['ifg_dates']=converted_dates
tbaseline_info['baselines']=baseline_from_names(tbaseline_info['ifg_dates'])
tbaseline_info['baselines_cumulative']=np.cumsum(tbaseline_info['baselines'])
print("\ntbaseline_info['ifg_dates']:\n",tbaseline_info['ifg_dates'])
print("\ntbaseline_info['baselines']:\n",tbaseline_info['baselines'])
print(len(tbaseline_info['baselines']))


#存储为pkl数据格式
with open(save_displacemet_r2_path,'wb') as f:
    pickle.dump(displacement_r2,f)
with open(save_tbaseline_info_path,'wb') as f:
    pickle.dump(tbaseline_info,f)


print("Done!!!")