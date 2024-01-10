#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/01/06
# Function:
#    select interferograms from all interferograms
#    ensure the total number is fit for the matlab code
#-------------------------------------------------------------------
import datetime
import os
import shutil
from scipy.io import loadmat

file_path="data/Synthetic_Fault/raw_data/simDatasetsConsiderDefHydroWet"
epoch_master_slave_dates_info_path=os.path.join(file_path,"simSAR.mat")
epoch_master_slave_dates_info=loadmat(epoch_master_slave_dates_info_path)

sar_epoch=epoch_master_slave_dates_info['sar_epoch']
date_format="%Y%m%d"
converted_dates=[]

for i in range(len(sar_epoch)-1):
    start_date=datetime.datetime.strptime(str(sar_epoch[i][0]),date_format).strftime(date_format)
    end_date=datetime.datetime.strptime(str(sar_epoch[i + 1][0]), date_format).strftime(date_format)
    converted_dates.append(f"{start_date}_{end_date}")

unw_names=[]
for date_range in converted_dates:
    start_date,end_date=date_range.split('_')   
    unw_name=f"geo_{start_date}-{end_date}.unw.rsc"
    unw_names.append(unw_name)
print(unw_names)

directory='data/Synthetic_Fault/raw_data_select'

for filename in os.listdir(directory):
    path=os.path.join(directory,filename)
    if filename not in unw_names:
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)

print("Done!")