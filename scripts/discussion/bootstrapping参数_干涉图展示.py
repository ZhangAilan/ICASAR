#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/05/07
# Function:
#   调整ICASAR不同参数后将PCA、ICA、APS的结果与真实形变场进行比较
#-------------------------------------------------------------------
import numpy as np
import pickle
from matplotlib import pyplot as plt

#RMSE
def RMSE(x,y):
    return np.sqrt(np.nanmean((x-y)**2))

save_path='data/Synthetic_Fault/结果/disscussion/不同参数比较'
deformation_flie='data/Synthetic_Fault/结果/deformation_data/velocity.pkl'
mask='data/Synthetic_Fault/mask.pkl'

ica_100_file='example_spatial_03_APS_par01/deformation_velocity_ica_r2.pkl'
ica_150_file='example_spatial_03_APS_par02/deformation_velocity_ica_r2.pkl'
ica_200_file='example_spatial_03_APS_cum/deformation_velocity_ica_r2.pkl'

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

RMSE_100=RMSE(deformation_mask,ica_100)
RMSE_150=RMSE(deformation_mask,ica_150)
RMSE_200=RMSE(deformation_mask,ica_200)
print(f'RMSE_100:{RMSE_100}')
print(f'RMSE_150:{RMSE_150}')
print(f'RMSE_200:{RMSE_200}')

#color range
min=-1
max=4
#stacking ifgs
fig,ax=plt.subplots(2,3,figsize=(15,10))
im1=ax[0,0].imshow(ica_100,cmap='jet', vmin=min, vmax=max)
ax[0,0].set_title('Bootstrap=100')
im2=ax[0,1].imshow(ica_150,cmap='jet', vmin=min, vmax=max)
ax[0,1].set_title('Bootstrap=150')
im3=ax[0,2].imshow(ica_200,cmap='jet', vmin=min, vmax=max)
ax[0,2].set_title('Bootstrap=200')

#colorbar
cbar = fig.colorbar(im1, ax=ax.ravel().tolist(), orientation='vertical', shrink=0.4, aspect=10)
cbar.ax.yaxis.set_ticks_position('right')
# cbar.set_label('mm/yr', fontsize=14)
cbar.ax.set_position([0.78, 0.55, 0.03, 0.3])

#scatter
ax[1,0].scatter(deformation_mask, ica_100, s=0.5)
ax[1,1].scatter(deformation_mask, ica_150, s=0.5)
ax[1,2].scatter(deformation_mask, ica_200, s=0.5)
#set limit and diagonal line
for i in range(3):
    ax[1,i].set_xlim(min,max)
    ax[1,i].set_ylim(min,max)
    ax[1,i].plot([min,max],[min,max],'r--')
#RMSE
locat_x=-0.5
locat_y=4.5
ax[1,0].text(locat_x,locat_y,f'RMSE={round(RMSE_100, 4)}', fontsize=14)
ax[1,1].text(locat_x,locat_y,f'RMSE={round(RMSE_150, 4)}', fontsize=14)
ax[1,2].text(locat_x,locat_y,f'RMSE={round(RMSE_200, 4)}', fontsize=14)
#label and title
ax[1,1].set_xlabel('Deformation LOS(rad/yr)', fontsize=14)
ax[1,0].set_ylabel('InSAR LOS(rad/yr)', fontsize=14)
fig.suptitle(f'{fig_title}', fontsize=14)

plt.savefig(f'{save_path}/{fig_title}.png')
print("Done!!!")