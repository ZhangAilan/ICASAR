#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/03/19
# Function:
#   read the Alytn Fault results (the article results)
#-------------------------------------------------------------------
import pickle
import h5py
import numpy as np

aps_phase_file = 'data/Altyn_Tagh_Fault/aps_data_real/aps_phase.mat'
save_displacemet_r2_path='data/Altyn_Tagh_Fault/aps_data_real/real_correct/displacement_r2.pkl'
save_tbaseline_info_path='data/Altyn_Tagh_Fault/aps_data_real/real_correct/tbaseline_info.pkl'

with h5py.File(aps_phase_file, 'r') as file:
    # get the variable names
    for var_name in file.keys():
        print(var_name)
    ifg_all_corrected_all = file['ifg_all_corrected'][:]
    master= file['master'][:]
    slave= file['slave'][:]
    sar_epoch = file['sar_epoch'][:].astype(int)
# print("\nifg_all_corrected_all:\n",ifg_all_corrected_all.shape)

#master_slave dates
master=np.array(master).astype(int).astype(str)
slave=np.array(slave).astype(int).astype(str)
master_slave=np.core.defchararray.add(master,'_')
master_slave=np.core.defchararray.add(master_slave,slave)
master_slave=master_slave[0]

# get the epoch dates
sar_epoch_rolled=np.roll(sar_epoch,-1)
sar_epoch=np.array(sar_epoch).astype(str)
sar_epoch_rolled=np.array(sar_epoch_rolled).astype(str)
sar_epoch_dates=np.core.defchararray.add(sar_epoch,'_')
sar_epoch_dates=np.core.defchararray.add(sar_epoch_dates,sar_epoch_rolled)
sar_epoch_dates=sar_epoch_dates[0][:-1]
# print("\nSAR epoch dates:\n",sar_epoch_dates)
# print("\nMaster_slave dates:\n",master_slave)

#check if all the elements of sar_epoch_dates are in master_slave
are_all_in=np.all(np.isin(sar_epoch_dates,master_slave))
print("\nThe ifgs dates are continously.-->",are_all_in)

#get the index of the ifgs dates
indices=np.where(np.isin(master_slave,sar_epoch_dates))[0]
indices=np.array(indices)
# print("\nIndices of the ifgs dates:\n",indices)
ifg_all_corrected=ifg_all_corrected_all[indices,:,:]
print("\nifg_all_corrected:\n",ifg_all_corrected.shape)


#save the data for ICASAR use
WIDTH=  235
FILE_LENGTH=  207
X_FIRST=   93.4352
X_STEP=    0.0154
Y_FIRST=   41.0972
Y_STEP=   -0.0154

displacement_r3={}
displacement_r3_inc=[]
for i in range(ifg_all_corrected.shape[0]):
    ifg_data=ifg_all_corrected[i,:,:]
    ifg_data[ifg_data == 0] = np.nan
    displacement_r3_inc.append(ifg_data)
displacement_r3['incremental'] = np.array(displacement_r3_inc)

#mask
mask_nan_r3=np.where(np.isnan(displacement_r3['incremental']),True,False)
mask_r2=np.any(mask_nan_r3,axis=0)

#dem
dem_path='data/Altyn_Tagh_Fault/raw_data/unw-coh0.5-decimated-withUECorrectedAuto/EQA.dem'
with open(dem_path,'rb') as f:
    dem=np.fromfile(f,dtype='>f4').reshape(FILE_LENGTH,WIDTH)
displacement_r3['dem']=dem

#将displacement_r3转换为displacement_r2
displacement_r2={}
n_ifgs=displacement_r3['incremental'].shape[0]
ifgs_r3_masked=np.ma.array(displacement_r3['incremental'],mask=np.ma.repeat(mask_r2[np.newaxis,],n_ifgs,axis=0))
n_pixs=np.ma.compressed(ifgs_r3_masked[0,]).shape[0]
ifgs_r2=np.zeros((n_ifgs,n_pixs))
for ifg_n,ifg in enumerate(ifgs_r3_masked):
    ifgs_r2[ifg_n,:]=np.ma.compressed(ifg)
displacement_r2['incremental']=ifgs_r2
displacement_r2['mask']=mask_r2
displacement_r2['dem']=displacement_r3['dem']
displacement_r2['cumulative']=np.cumsum(displacement_r2['incremental'],axis=0)

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

converted_dates=[]
for item in sar_epoch_dates:
    converted_dates.append(item)
tbaseline_info={}
tbaseline_info['ifg_dates']=converted_dates
tbaseline_info['baselines']=baseline_from_names(tbaseline_info['ifg_dates'])
tbaseline_info['baselines_cumulative']=np.cumsum(tbaseline_info['baselines'])

print("\ntbaseline_info['ifg_dates']:\n",tbaseline_info['ifg_dates'])
print(len(tbaseline_info['ifg_dates']))
print("\ntbaseline_info['baselines']:\n",tbaseline_info['baselines'])

#存储为pkl文件
with open(save_displacemet_r2_path,'wb') as f:
    pickle.dump(displacement_r2,f)
with open(save_tbaseline_info_path,'wb') as f:
    pickle.dump(tbaseline_info,f)

print("Done!!!")