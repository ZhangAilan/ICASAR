#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/05/07
# Function:
#   不同bootstrapping参数下ICASAR的对比
#   绘图，横轴为参数100、150、...、400，纵轴为RMSE
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

ica_100_file='example_spatial_03_APS_par01/deformation_velocity_ica_r2.pkl'
ica_150_file='example_spatial_03_APS_par02/deformation_velocity_ica_r2.pkl'
ica_200_file='example_spatial_03_APS_par03/deformation_velocity_ica_r2.pkl'
ica_250_file='example_spatial_03_APS_par04/deformation_velocity_ica_r2.pkl'
ica_300_file='example_spatial_03_APS_par05/deformation_velocity_ica_r2.pkl'
ica_350_file='example_spatial_03_APS_par06/deformation_velocity_ica_r2.pkl'
ica_400_file='example_spatial_03_APS_par07/deformation_velocity_ica_r2.pkl'

fig_title='Bootstrapping_param & ICA'
with open(deformation_flie,'rb') as f:
    deformation=pickle.load(f)
with open(mask,'rb') as f:
    mask=pickle.load(f)
deformation_mask=np.where(mask,np.nan,deformation)

with open(ica_100_file,'rb') as f:
    ica_100=pickle.load(f)
with open(ica_150_file,'rb') as f:
    ica_150=pickle.load(f)
with open(ica_200_file,'rb') as f:
    ica_200=pickle.load(f)
with open(ica_250_file,'rb') as f:
    ica_250=pickle.load(f)
with open(ica_300_file,'rb') as f:
    ica_300=pickle.load(f)
with open(ica_350_file,'rb') as f:
    ica_350=pickle.load(f)
with open(ica_400_file,'rb') as f:
    ica_400=pickle.load(f)

RMSE_100=RMSE(deformation_mask,ica_100)
RMSE_150=RMSE(deformation_mask,ica_150)
RMSE_200=RMSE(deformation_mask,ica_200)
RMSE_250=RMSE(deformation_mask,ica_250)
RMSE_300=RMSE(deformation_mask,ica_300)
RMSE_350=RMSE(deformation_mask,ica_350)
RMSE_400=RMSE(deformation_mask,ica_400)
print(f'RMSE_100:{RMSE_100}')
print(f'RMSE_150:{RMSE_150}')
print(f'RMSE_200:{RMSE_200}')
print(f'RMSE_250:{RMSE_250}')
print(f'RMSE_300:{RMSE_300}')
print(f'RMSE_350:{RMSE_350}')
print(f'RMSE_400:{RMSE_400}')

#plot
plt.figure()
plt.plot([100,150,200,250,300,350,400],[RMSE_100,RMSE_150,RMSE_200,RMSE_250,RMSE_300,RMSE_350,RMSE_400])
plt.scatter([100,150,200,250,300,350,400],[RMSE_100,RMSE_150,RMSE_200,RMSE_250,RMSE_300,RMSE_350,RMSE_400])
plt.xlabel('Bootstrapping')
plt.ylabel('RMSE')
plt.title('Bootstrapping Compare')
plt.savefig(f'{save_path}/Bootstrapping.png')

print('Done!')