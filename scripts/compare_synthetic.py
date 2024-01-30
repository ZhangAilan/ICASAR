#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/01/26
# Function:
#   Compare the synthetic data with the Aps_phase data.
#                                       PCA
#                                       ICA
#-------------------------------------------------------------------
import numpy as np
import pickle
from matplotlib import pyplot as plt

#file path
save_path='data/Synthetic_Fault/compare_results'
deformation_flie='data/Synthetic_Fault/raw_data/deformation_data/velocity.pkl'
aps_phase_file='data/Synthetic_Fault/raw_data/aps_corrected_stacking/velocity.pkl'
mask='data/Synthetic_Fault/mask.pkl'

#all
stacking_PCA_file='example_spatial_03_APS_all/deformation_velocity_pca_r2.pkl'
stacking_ICA_file='example_spatial_03_APS_all/deformation_velocity_ica_r2.pkl'
fig_title='deformation & stacking(all)'

# #cum
# stacking_PCA_file='example_spatial_03_APS_cum/deformation_velocity_pca_r2.pkl'
# stacking_ICA_file='example_spatial_03_APS_cum/deformation_velocity_ica_r2.pkl'
# fig_title='deformation & stacking(cum)'

# #inc
# stacking_PCA_file='example_spatial_03_APS_inc/deformation_velocity_pca_r2.pkl'
# stacking_ICA_file='example_spatial_03_APS_inc/deformation_velocity_ica_r2.pkl'
# fig_title='deformation & stacking(inc)'

with open(stacking_PCA_file,'rb') as f:
    stacking_PCA=pickle.load(f)
with open(stacking_ICA_file,'rb') as f:
    stacking_ICA=pickle.load(f)
with open(aps_phase_file,'rb') as f:
    aps_phase=pickle.load(f)

with open(deformation_flie,'rb') as f:
    deformation_true=pickle.load(f)
with open(mask,'rb') as f:
    mask=pickle.load(f)
deformation_mask=np.where(mask,np.nan,deformation_true)

#RMSE
def RMSE(x,y):
    return np.sqrt(np.nanmean((x-y)**2))
RMSE_aps=RMSE(deformation_mask,aps_phase)
RMSE_PCA=RMSE(deformation_mask,stacking_PCA)
RMSE_ICA=RMSE(deformation_mask,stacking_ICA)
print(f'RMSE_aps:{RMSE_aps}')
print(f'RMSE_PCA:{RMSE_PCA}')
print(f'RMSE_ICA:{RMSE_ICA}')

#stacking ifgs
fig,ax=plt.subplots(2,3,figsize=(15,10))
im1=ax[0,0].imshow(aps_phase,cmap='jet', vmin=-8, vmax=4)
ax[0,0].set_title('aps_phase')
im2=ax[0,1].imshow(stacking_PCA,cmap='jet', vmin=-8, vmax=4)
ax[0,1].set_title('stacking_PCA')
im3=ax[0,2].imshow(stacking_ICA,cmap='jet', vmin=-8, vmax=4)
ax[0,2].set_title('stacking_ICA')

#colorbar
cbar = fig.colorbar(im1, ax=ax.ravel().tolist(), orientation='vertical', shrink=0.4, aspect=10)
cbar.ax.yaxis.set_ticks_position('right')
cbar.set_label('mm/yr', fontsize=14)
cbar.ax.set_position([0.78, 0.55, 0.03, 0.3])

#scatter
ax[1,0].scatter(deformation_mask,aps_phase)
ax[1,1].scatter(deformation_mask,stacking_PCA)
ax[1,2].scatter(deformation_mask,stacking_ICA)
#set limit and diagonal line
for i in range(3):
    ax[1,i].set_xlim(-8,4)
    ax[1,i].set_ylim(-8,4)
    ax[1,i].plot([-8,4],[-8,4],'r--')
#RMSE
ax[1,0].text(-7,3,f'RMSE={round(RMSE_aps, 2)}', fontsize=14)
ax[1,1].text(-7,3,f'RMSE={round(RMSE_PCA, 2)}', fontsize=14)
ax[1,2].text(-7,3,f'RMSE={round(RMSE_ICA, 2)}', fontsize=14)
#label and title
ax[1,1].set_xlabel('Deformation LOS(mm/yr)', fontsize=14)
ax[1,0].set_ylabel('InSAR LOS(mm/yr)', fontsize=14)
fig.suptitle(f'{fig_title}', fontsize=14)

plt.savefig(f'{save_path}/{fig_title}.png')
print("Done!!!")