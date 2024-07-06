#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/04/01
# Function:
#   read the synthetic deformation and subtract the reference region
#-------------------------------------------------------------------
import scipy.io
import numpy as np
import pickle
import os

file_path='data/Synthetic_Fault/raw_data/simDatasetsConsiderDefHydroWet'
epoch_master_slave_dates_info_path=os.path.join(file_path,"simSAR.mat")
data=scipy.io.loadmat(epoch_master_slave_dates_info_path)
save_path='data/Synthetic_Fault/raw_data/deformation_data'

#the raw deformation data
ifg_defo=data['ifg_defo']
print("\nifg_defo.shape:",ifg_defo.shape)

#the reference region
reference_region = np.array([[95.15, 40.03],
                             [95.25, 40.03],
                             [95.25, 39.93],
                             [95.15, 39.93],])
X_FIRST= 93.4351852
X_STEP = 1.5432099e-02
Y_FIRST= 41.0972222
Y_STEP = -1.5432099e-02
ref_index=[]
for item in reference_region:
    x,y=item
    i=int(np.floor((x-X_FIRST)/X_STEP))
    j=int(np.floor((y-Y_FIRST)/Y_STEP))
    ref_index.append([i,j])
print("\nref_index:",ref_index)

#subtract the reference region
ref_mean_values=np.zeros(ifg_defo.shape[2])
for i in range(ifg_defo.shape[2]):
    ref_mean_values[i]=np.mean([ifg_defo[index[0], index[1], i] for index in ref_index])
    ifg_defo[:,:,i]-=ref_mean_values[i]
print("\nifg_defo_correct.shape:",ifg_defo.shape)

#save the corrected deformation data
with open(os.path.join(save_path,'ifg_defo_subtract_reference.pkl'),'wb') as f:
    pickle.dump(ifg_defo,f)

print("Done!!!")