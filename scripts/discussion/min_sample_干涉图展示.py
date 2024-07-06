#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/05/07
# Function:
#   不同min_sample下ICASAR的对比
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

ica_10_file='example_spatial_03_APS_minsample_2/deformation_velocity_ica_r2.pkl'
ica_15_file='example_spatial_03_APS_minsample_3/deformation_velocity_ica_r2.pkl'
ica_20_file='example_spatial_03_APS_minsample_4/deformation_velocity_ica_r2.pkl'


fig_title='Min_sample_param & ICA'
with open(deformation_flie,'rb') as f:
    deformation=pickle.load(f)
with open(mask,'rb') as f:
    mask=pickle.load(f)
deformation_mask=np.where(mask,np.nan,deformation)  

with open(ica_10_file,'rb') as f:
    ica_10=pickle.load(f)
with open(ica_15_file,'rb') as f:
    ica_15=pickle.load(f)
with open(ica_20_file,'rb') as f:
    ica_20=pickle.load(f)

RMSE_10=RMSE(deformation_mask,ica_10)
RMSE_15=RMSE(deformation_mask,ica_15)
RMSE_20=RMSE(deformation_mask,ica_20)


#color range
min=-1
max=4
#stacking ifgs
fig,ax=plt.subplots(2,3,figsize=(15,10))
im1=ax[0,0].imshow(ica_10,cmap='jet', vmin=min, vmax=max)
ax[0,0].set_title('Min_cluster=10')
im2=ax[0,1].imshow(ica_15,cmap='jet', vmin=min, vmax=max)
ax[0,1].set_title('Min_cluster=15')
im3=ax[0,2].imshow(ica_20,cmap='jet', vmin=min, vmax=max)
ax[0,2].set_title('Min_cluster=20')

#colorbar
cbar = fig.colorbar(im1, ax=ax.ravel().tolist(), orientation='vertical', shrink=0.4, aspect=10)
cbar.ax.yaxis.set_ticks_position('right')
# cbar.set_label('mm/yr', fontsize=14)
cbar.ax.set_position([0.78, 0.55, 0.03, 0.3])

#scatter
ax[1,0].scatter(deformation_mask,ica_10)
ax[1,1].scatter(deformation_mask,ica_15)
ax[1,2].scatter(deformation_mask,ica_20)
#set limit and diagonal line
for i in range(3):
    ax[1,i].set_xlim(min,max)
    ax[1,i].set_ylim(min,max)
    ax[1,i].plot([min,max],[min,max],'r--')
#RMSE
locat_x=-0.5
locat_y=4.5
ax[1,0].text(locat_x,locat_y,f'RMSE={round(RMSE_10, 4)}', fontsize=14)
ax[1,1].text(locat_x,locat_y,f'RMSE={round(RMSE_15, 4)}', fontsize=14)
ax[1,2].text(locat_x,locat_y,f'RMSE={round(RMSE_20, 4)}', fontsize=14)
#label and title
ax[1,1].set_xlabel('Deformation LOS(rad/yr)', fontsize=14)
ax[1,0].set_ylabel('InSAR LOS(rad/yr)', fontsize=14)
fig.suptitle(f'{fig_title}', fontsize=14)

plt.savefig(f'{save_path}/{fig_title}.png')
print("Done!!!")