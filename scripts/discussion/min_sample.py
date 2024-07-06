#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/05/07
# Function:
#   不同min_sample下ICASAR的对比
#   绘图，横轴为参数10、20、30、40，纵轴为RMSE
#-------------------------------------------------------------------
import numpy as np
import pickle
from matplotlib import pyplot as plt

#RMSE
def RMSE(x,y):
    return np.sqrt(np.nanmean((x-y)**2))

save_path='data/Synthetic_Fault/disscussion/不同参数比较'
deformation_flie='data/Synthetic_Fault/raw_data/deformation_data/velocity.pkl'
mask='data/Synthetic_Fault/mask.pkl'

ica_5_file='example_spatial_03_APS_minsample_1/deformation_velocity_ica_r2.pkl'
ica_10_file='example_spatial_03_APS_minsample_2/deformation_velocity_ica_r2.pkl'
ica_15_file='example_spatial_03_APS_minsample_3/deformation_velocity_ica_r2.pkl'
ica_20_file='example_spatial_03_APS_minsample_4/deformation_velocity_ica_r2.pkl'


fig_title='Min_cluster_param & ICA'
with open(deformation_flie,'rb') as f:
    deformation=pickle.load(f)
with open(mask,'rb') as f:
    mask=pickle.load(f)
deformation_mask=np.where(mask,np.nan,deformation)  

with open(ica_5_file,'rb') as f:
    ica_5=pickle.load(f)
with open(ica_10_file,'rb') as f:
    ica_10=pickle.load(f)
with open(ica_15_file,'rb') as f:
    ica_15=pickle.load(f)
with open(ica_20_file,'rb') as f:
    ica_20=pickle.load(f)

RMSE_50=RMSE(deformation_mask,ica_5)
RMSE_100=RMSE(deformation_mask,ica_10)
RMSE_150=RMSE(deformation_mask,ica_15)
RMSE_200=RMSE(deformation_mask,ica_20)

plt.figure()
plt.plot([5,10,15,20],[RMSE_50,RMSE_100,RMSE_150,RMSE_200])
plt.scatter([5,10,15,20],[RMSE_50,RMSE_100,RMSE_150,RMSE_200])
plt.xlabel('min_sample')
plt.ylabel('RMSE')
plt.title(fig_title)
plt.savefig(save_path+'/min_sample.png')
print("Done!!!")