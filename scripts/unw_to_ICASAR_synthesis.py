import datetime
import numpy as np
import os
import pickle
from scipy.io import loadmat
import numpy.ma as ma

file_path="data/Synthetic_Fault/raw_data/simDatasetsConsiderDefHydroWet"
save_displacemet_r2_path="data/Synthetic_Fault/temp_data/displacement_r2.pkl"
save_tbaseline_info_path="data/Synthetic_Fault/temp_data/tbaseline_info.pkl"
dem_rsc_path=os.path.join(file_path,"EQA.dem.rsc")
dem_path=os.path.join(file_path,"EQA.dem")
epoch_master_slave_dates_info_path=os.path.join(file_path,"simSAR.mat")
epoch_master_slave_dates_info=loadmat(epoch_master_slave_dates_info_path)


#读取 .mat数据包含的日期信息
# for var_name in epoch_master_slave_dates_info:
#     print(f"Variable:{var_name}")
#     print(f"Data:\n{epoch_master_slave_dates_info[var_name]}\n")


#转换日期格式
sar_epoch=epoch_master_slave_dates_info['sar_epoch']
date_format="%Y%m%d"
converted_dates=[]

for i in range(len(sar_epoch)-1):
    start_date=datetime.datetime.strptime(str(sar_epoch[i][0]),date_format).strftime(date_format)
    end_date=datetime.datetime.strptime(str(sar_epoch[i + 1][0]), date_format).strftime(date_format)
    converted_dates.append(f"{start_date}_{end_date}")


#读取满足日期条件的文件并保存数据
unw_names=[]
for date_range in converted_dates:
    start_date,end_date=date_range.split('_')   #提取日期范围的起始日期和结束日期
    unw_name=f"geo_{start_date}-{end_date}.unw"
    unw_names.append(unw_name)


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