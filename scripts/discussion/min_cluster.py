#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/05/07
# Function:
#   不同min_cluster参数下ICASAR的对比
#   绘图，横轴为参数50、100、150、200，纵轴为RMSE
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

ica_50_file='example_spatial_03_APS_mincluster_1/deformation_velocity_ica_r2.pkl'
ica_100_file='example_spatial_03_APS_mincluster_2/deformation_velocity_ica_r2.pkl'
ica_150_file='example_spatial_03_APS_mincluster_3/deformation_velocity_ica_r2.pkl'
ica_200_file='example_spatial_03_APS_mincluster_4/deformation_velocity_ica_r2.pkl'

fig_title='Min_cluster_param & ICA'
with open(deformation_flie,'rb') as f:
    deformation=pickle.load(f)
with open(mask,'rb') as f:
    mask=pickle.load(f)
deformation_mask=np.where(mask,np.nan,deformation)  

with open(ica_50_file,'rb') as f:
    ica_50=pickle.load(f)
with open(ica_100_file,'rb') as f:
    ica_100=pickle.load(f)
with open(ica_150_file,'rb') as f:
    ica_150=pickle.load(f)
with open(ica_200_file,'rb') as f:
    ica_200=pickle.load(f)

RMSE_50=RMSE(deformation_mask,ica_50)
RMSE_100=RMSE(deformation_mask,ica_100)
RMSE_150=RMSE(deformation_mask,ica_150)
RMSE_200=RMSE(deformation_mask,ica_200)

plt.figure()
plt.plot([50,100,150,200],[RMSE_50,RMSE_100,RMSE_150,RMSE_200])
plt.scatter([50,100,150,200],[RMSE_50,RMSE_100,RMSE_150,RMSE_200])
plt.xlabel('min_cluster')
plt.ylabel('RMSE')
plt.title(fig_title)
plt.savefig(save_path+'/min_cluster.png')
print("Done!!!")