#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/01/10
# Function:
#   change the text content in the file
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
    unw_name=f"geo_{start_date}-{end_date}.unw"
    unw_names.append(unw_name)

file_txt_path="data/Synthetic_Fault/raw_data_select/ifg_filelist.txt"
with open(file_txt_path,'w') as f:
    for unw_name in unw_names:
        f.write("%s\n" % unw_name)
print("Done!")
