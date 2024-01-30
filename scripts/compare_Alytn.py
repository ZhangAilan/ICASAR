#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/01/26
# Function:
#   Compare the Alytn data with the Aps_phase data.
#                                       PCA
#                                       ICA
#-------------------------------------------------------------------
import numpy as np
import pickle
from matplotlib import pyplot as plt

#file path
save_path='data/Altyn_Tagh_Fault/compare_results'
GNSS_flie='data/Altyn_Tagh_Fault/raw_data/GNSS_LOS/Altyn_GNSS_LOS.txt'
aps_phase_file='data/Altyn_Tagh_Fault/raw_data/aps_corrected_stacking/velocity.pkl'

#all
stacking_PCA_file='example_spatial_05_APS_all/deformation_velocity_pca_r2.pkl'
stacking_ICA_file='example_spatial_05_APS_all/deformation_velocity_ica_r2.pkl'
fig_title='GNSS & stacking(all)'

# #cum
# stacking_PCA_file='example_spatial_05_APS_cum/deformation_velocity_pca_r2.pkl'
# stacking_ICA_file='example_spatial_05_APS_cum/deformation_velocity_ica_r2.pkl'
# fig_title='GNSS & stacking(cum)'

# #inc
# stacking_PCA_file='example_spatial_05_APS_inc/deformation_velocity_pca_r2.pkl'
# stacking_ICA_file='example_spatial_05_APS_inc/deformation_velocity_ica_r2.pkl'
# fig_title='GNSS & stacking(inc)'


with open(aps_phase_file, 'rb') as f:
    aps_phase= pickle.load(f)
with open(stacking_PCA_file,'rb') as f:
    stacking_PCA=pickle.load(f)
with open(stacking_ICA_file,'rb') as f:
    stacking_ICA=pickle.load(f)
GNSS=np.loadtxt(GNSS_flie)

X_FIRST= 93.4351852
X_STEP = 1.5432099e-02
Y_FIRST= 41.0972222
Y_STEP = -1.5432099e-02
WIDTH=  235
FILE_LENGTH=  207

indices=[]
GNSS_loss=[]
for coord in GNSS:
    loss=coord[2]
    GNSS_loss.append(loss)
    x,y=coord[0],coord[1]
    # i=int(np.floor((x-X_FIRST)/X_STEP))
    # j=int(np.floor((y-Y_FIRST)/Y_STEP))
    i=int((x-X_FIRST)/X_STEP)
    j=int((y-Y_FIRST)/Y_STEP)
    indices.append([i,j])
   

#aps_phase 
aps_phase_loss=[]
for index in indices:
    aps_phase_loss.append(aps_phase[index[0]-1,index[1]-1])
aps_phase_loss=np.array(aps_phase_loss)
print(aps_phase_loss)

#stacking_PCA
stacking_PCA_loss=[]
for index in indices:
    stacking_PCA_loss.append(stacking_PCA[index[0]-1,index[1]-1])
stacking_PCA_loss=np.array(stacking_PCA_loss)
print(stacking_PCA_loss)

#stacking_ICA
stacking_ICA_loss=[]
for index in indices:
    stacking_ICA_loss.append(stacking_ICA[index[0]-1,index[1]-1])
stacking_ICA_loss=np.array(stacking_ICA_loss)
print(stacking_ICA_loss)

#RMSE
def RMSE(x,y):
    return np.sqrt(np.nanmean((x-y)**2))
RMSE_aps=RMSE(GNSS_loss,aps_phase_loss)
RMSE_PCA=RMSE(GNSS_loss,stacking_PCA_loss)
RMSE_ICA=RMSE(GNSS_loss,stacking_ICA_loss)
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
ax[1,0].scatter(GNSS_loss,aps_phase_loss)
ax[1,1].scatter(GNSS_loss,stacking_PCA_loss)
ax[1,2].scatter(GNSS_loss,stacking_ICA_loss)
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
ax[1,1].set_xlabel('GNSS LOS(mm/yr)', fontsize=14)
ax[1,0].set_ylabel('InSAR LOS(mm/yr)', fontsize=14)
fig.suptitle(f'{fig_title}', fontsize=14)
#lat and lon
for i in range(3):
    for j in range(len(GNSS)):
        x_offset = (GNSS[j][0] - X_FIRST) / X_STEP
        y_offset = (GNSS[j][1] - Y_FIRST) / Y_STEP
        ax[0,i].scatter(x_offset, y_offset, s=10, c='k')

plt.savefig(f'{save_path}/{fig_title}.png')
print("Done!!!")