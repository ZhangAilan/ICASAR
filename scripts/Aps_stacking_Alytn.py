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
#   this script can be used in Alytn data.
#-------------------------------------------------------------------
import datetime
import numpy as np
import os
import pickle
from scipy.io import loadmat
from matplotlib import pyplot as plt
import re

file_path="D:\\ICASAR\\data\\Altyn_Tagh_Fault\\aps_data\\CorrectedIfgs-model6-defoFlag1-wetFlag1-hydroFlag1-iteraNum1-solver2-ueFixMethod0-weightScheme1-shortBt60-shortBtRelax500"
save_path='data/Altyn_Tagh_Fault/raw_data/aps_corrected_stacking'
ifg_filelist_path=os.path.join(file_path,"ifg_filelist_shortBt.txt")

#读取ifgs_file中的日期信息
with open(ifg_filelist_path,'r') as f:
    ifg_filelist=f.read()
epoch_master_slave_dates_info = re.findall(r'\b\d{8}\b', ifg_filelist)
#去重并排序
epoch_master_slave_dates_info=sorted(list(set(epoch_master_slave_dates_info)))
epoch_master_slave_dates_info.insert(0,'20170404')
elements_to_remove=['20170615','20170802','20170814','20171212','20171224','20180117','20180129','20180306','20180610','20180622','20180704','20180902','20180914','20181008','20181101','20181207','20181231','20190313','20190325','20190524','20190804','20191108','20191120','20191202','20200119','20200212','20200307','20200319','20200412','20200506','20200518','20200611','20200705','20200915','20210101']
epoch_master_slave_dates_info=[i for i in epoch_master_slave_dates_info if i not in elements_to_remove]
epoch_master_slave_dates_info=np.array(epoch_master_slave_dates_info).reshape(-1,1).astype(int)

#转换日期格式
sar_epoch=epoch_master_slave_dates_info
date_format="%Y%m%d"
converted_dates=[]
time_baselines=[]

for i in range(len(sar_epoch)-1):
    start_date=datetime.datetime.strptime(str(sar_epoch[i][0]),date_format)
    end_date=datetime.datetime.strptime(str(sar_epoch[i + 1][0]), date_format)
    converted_dates.append(f"{start_date.strftime(date_format)}_{end_date.strftime(date_format)}")
    time_baselines.append((end_date-start_date).days)


#读取满足日期条件的文件并保存数据
unw_names=[]
for date_range in converted_dates:
    start_date,end_date=date_range.split('_')   #提取日期范围的起始日期和结束日期
    unw_name=f"geo_{start_date}-{end_date}.UEcorrected.APScorrected"
    unw_names.append(unw_name)
print(unw_names)
print(len(unw_names))
print(time_baselines)

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
deformation_velocity=ph_rate*(-0.056/(4*np.pi))*1000

plt.imshow(deformation_velocity,cmap='jet',aspect='auto')
plt.colorbar()
plt.clim(-5, 5)
plt.savefig(os.path.join(save_path,'velocity.png'))

with open(os.path.join(save_path,'velocity.pkl'),'wb') as f:
    pickle.dump(deformation_velocity,f)
with open(os.path.join(save_path,'mask.pkl'),'wb') as f:
    pickle.dump(mask_r2,f)

print("Done!!!")