#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/01/25
# Function:
#   read the Synthetic_Fault simSAR.mat file
#   get the deformation data and plot the velocity image
#-------------------------------------------------------------------
import scipy.io
import datetime
import os
import numpy as np
import matplotlib.pyplot as plt
import pickle

file_path='data/Synthetic_Fault/raw_data/simDatasetsConsiderDefHydroWet'
epoch_master_slave_dates_info_path=os.path.join(file_path,"simSAR.mat")
ifg_filelist_path=os.path.join(file_path,"ifg_filelist.txt")
data=scipy.io.loadmat(epoch_master_slave_dates_info_path)
save_path='data/Synthetic_Fault/raw_data/deformation_data'

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
print(ref_index)

# # get the variable names
# for var_name in data.keys():
#     print(var_name)
ifg_defo=data['ifg_defo']
print(ifg_defo.shape)


#get the epoch dates
sar_epoch=data['sar_epoch']
date_format="%Y%m%d"
converted_dates=[]
for i in range(len(sar_epoch)-1):
    start_date=datetime.datetime.strptime(str(sar_epoch[i][0]),date_format).strftime(date_format)
    end_date=datetime.datetime.strptime(str(sar_epoch[i + 1][0]), date_format).strftime(date_format)
    converted_dates.append(f"{start_date}_{end_date}")
print(converted_dates)

# #indices:20170826--[12];20181101--[45]
# converted_dates_search=np.array(converted_dates)
# indice_start=np.where(converted_dates_search=='20170826_20170907')
# indice_end=np.where(converted_dates_search=='20181101_20181113')
# print(indice_start)
# print(indice_end)


#time baselines
time_baselines=[]
for date in converted_dates:
    start_date,end_date=date.split('_')
    start_date=datetime.datetime.strptime(start_date,date_format)
    end_date=datetime.datetime.strptime(end_date,date_format)
    time_baselines.append((end_date-start_date).days)
print(time_baselines)


#to get the index
unw_names=[]
for date_range in converted_dates:
    start_date,end_date=date_range.split('_')  
    unw_name=f"geo_{start_date}-{end_date}.unw"
    unw_names.append(unw_name)
print(unw_names)
line_numbers=[]  #save the line number of the unw_names
with open(ifg_filelist_path,'r') as f:
    for i,line in enumerate(f,start=1):
        if any(name in line for name in unw_names):
            line_numbers.append(i)
print(line_numbers)
print(len(line_numbers))


#get the 20170826-20181101 deformation ifg line numbers
line_numbers_search=line_numbers[12:45]
print("line_numbers_search:",line_numbers_search)
print(len(line_numbers_search))


#read the ifg_defo data
defo_data=[]
for index in line_numbers:
    defo_data.append(ifg_defo[:,:,index-1])
defo_data=np.array(defo_data)
print(defo_data.shape)


#stacking
ph_sum=np.zeros((235,207))
t_sum=0
for i in range(len(time_baselines)):
    time_baseline=time_baselines[i]
    time_baseline=time_baseline/365.25
    t_sum+=time_baseline**2
    for j in range(defo_data[i].shape[0]):
        for k in range(defo_data[i].shape[1]):
            ph_sum[j][k]+=time_baseline*defo_data[i][j][k]
ph_rate=ph_sum/t_sum
# velocity=ph_rate*(-0.056/(4*np.pi))*1000
velocity=ph_rate

#remove the average value of the reference region
ref_index=np.array(ref_index)
ref_value=[]
for index in ref_index:
    ref_value.append(velocity[index[0],index[1]])
ref_value=np.array(ref_value)
velocity=velocity-ref_value.mean()
velocity=velocity.T

#plot the velocity image
plt.imshow(velocity,cmap='jet',aspect='auto')
plt.colorbar()
plt.savefig(os.path.join(save_path,'velocity-rad.png'))
with open(os.path.join(save_path,'velocity.pkl'),'wb') as f:
    pickle.dump(velocity,f)


# #plot the 20170826-20181101 deformation ifg
# defo_ifg_20170826_20181101=[]
# for index in line_numbers_search:
#     defo_ifg_20170826_20181101.append(ifg_defo[:,:,index-1])
# defo_ifg_20170826_20181101=np.array(defo_ifg_20170826_20181101)
# defo_ifg_20170826_20181101=np.cumsum(defo_ifg_20170826_20181101,axis=0)
# plt.imshow(defo_ifg_20170826_20181101[-1].T, cmap='jet', aspect='auto', vmin=-2, vmax=2)
# plt.colorbar()
# plt.savefig(os.path.join(save_path,'defo_ifg_20170826_20181101.png'))


print("Done!!!")