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

#get the variable names
# for var_name in data.keys():
#     print(var_name)

ifg_defo=data['ifg_defo']
print(ifg_defo.shape)

sar_epoch=data['sar_epoch']
date_format="%Y%m%d"
converted_dates=[]
for i in range(len(sar_epoch)-1):
    start_date=datetime.datetime.strptime(str(sar_epoch[i][0]),date_format).strftime(date_format)
    end_date=datetime.datetime.strptime(str(sar_epoch[i + 1][0]), date_format).strftime(date_format)
    converted_dates.append(f"{start_date}_{end_date}")
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

accumulated_ifg_defo=np.zeros((235,207))
for line_number in line_numbers:
    line_data=ifg_defo[:,:,line_number-1]
    accumulated_ifg_defo+=line_data

# accumulated_ifg_defo=np.zeros((235,207))
# line_numbers=[10,366,732]
# for line_number in line_numbers:
#     line_data=ifg_defo[:,:,line_number-1]
#     accumulated_ifg_defo+=line_data 

# total days
date1=datetime.datetime.strptime(str(sar_epoch[0][0]),date_format)
date2=datetime.datetime.strptime(str(sar_epoch[-1][0]),date_format)
diff=(date2-date1).days

# velocity mm/year
velocity=(accumulated_ifg_defo/diff)*365*(-56/(4*np.pi))
velocity=velocity.T

plt.imshow(velocity,cmap='jet',aspect='auto')
plt.colorbar()
plt.savefig(os.path.join(save_path,'velocity.png'))
with open(os.path.join(save_path,'velocity.pkl'),'wb') as f:
    pickle.dump(velocity,f)

print("Done!!!")