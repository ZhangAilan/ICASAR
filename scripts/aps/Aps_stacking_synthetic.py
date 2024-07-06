    #------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/01/25
# Function:
#   Use the corrected interferogram of the aps_phase method to 
#   calculate the deformation.
#   this script can be used in Altyn and synthetic fault data.
#-------------------------------------------------------------------
import datetime
import numpy as np
import os
import pickle
from scipy.io import loadmat
from matplotlib import pyplot as plt

file_path_raw="data/Synthetic_Fault/raw_data/simDatasetsConsiderDefHydroWet"
file_path="data/Synthetic_Fault/aps_data/CorrectedIfgs-model6-defoFlag1-wetFlag1-hydroFlag2-iteraNum1-solver2-ueFixMethod0-weightScheme1-shortBt60-shortBtRelax500"
save_path='data/Synthetic_Fault/raw_data/aps_corrected_stacking'

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

#time baselines
time_baselines=[]
for date in converted_dates:
    start_date,end_date=date.split('_')
    start_date=datetime.datetime.strptime(start_date,date_format)
    end_date=datetime.datetime.strptime(end_date,date_format)
    time_baselines.append((end_date-start_date).days)
print("\nTime baselines:",time_baselines)

WIDTH=  235
FILE_LENGTH=  207
X_FIRST=   93.4352
X_STEP=    0.0154
Y_FIRST=   41.0972
Y_STEP=   -0.0154

displacement_r3_inc=[]
for unw_name in unw_names:
    fullpath=os.path.join(file_path,unw_name)
    with open(fullpath,'rb') as f:
        ifg_data=np.fromfile(f,dtype='>f4').reshape(FILE_LENGTH,WIDTH)
        ifg_data[ifg_data == 0] = np.nan
        displacement_r3_inc.append(ifg_data)
displacement_r3_inc=np.array(displacement_r3_inc)

#mask
mask_nan_r3=np.where(np.isnan(displacement_r3_inc),True,False)
mask_r2=np.any(mask_nan_r3,axis=0)

#stacking
ph_sum=np.zeros((207,235))
t_sum=0
for i in range(len(time_baselines)):
    time_baseline=time_baselines[i]
    time_baseline=time_baseline/365.25
    t_sum+=time_baseline**2
    for j in range(displacement_r3_inc[i].shape[0]):
        for k in range(displacement_r3_inc[i].shape[1]):
            ph_sum[j][k]+=time_baseline*displacement_r3_inc[i][j][k]
ph_rate=ph_sum/t_sum
# deformation_velocity=ph_rate*(-0.056/(4*np.pi))*1000
deformation_velocity=ph_rate

plt.imshow(deformation_velocity, cmap='jet', aspect='auto')
plt.colorbar()
plt.savefig(os.path.join(save_path,'velocity-rad.png'))

with open(os.path.join(save_path,'velocity.pkl'),'wb') as f:
    pickle.dump(deformation_velocity,f)
with open(os.path.join(save_path,'mask.pkl'),'wb') as f:
    pickle.dump(mask_r2,f)
with open(os.path.join(save_path,'time_baselines.pkl'),'wb') as f:
    pickle.dump(time_baselines,f)


# #plot the 20170826-20181101 deformation ifg  index:12-45
# ifg_20170826_20181101=displacement_r3_inc[12:45]
# ifg_20170826_20181101=np.array(ifg_20170826_20181101)
# deformation_20170826_20181101=np.cumsum(ifg_20170826_20181101,axis=0)
# plt.imshow(deformation_20170826_20181101[-1], cmap='jet', aspect='auto',vmin=-2,vmax=2)
# plt.colorbar()
# plt.savefig(os.path.join(save_path,'deformation_20170826_20181101.png'))

print("Done!!!")