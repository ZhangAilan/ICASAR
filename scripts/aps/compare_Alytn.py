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
import matplotlib.font_manager as font_manager
from matplotlib.ticker import MaxNLocator
font_manager._rebuild()

#file path
save_path='data/Altyn_Tagh_Fault/结果/compare_results'
GNSS_flie='data/Altyn_Tagh_Fault/raw_data/GNSS_LOS/Altyn_GNSS_LOS.txt'
aps_phase_file='data/Altyn_Tagh_Fault/结果/aps_corrected_stacking/velocity.pkl'
stacking_PCA_file='example_spatial_05_APS_cum/deformation_velocity_pca_r2.pkl'
stacking_ICA_file='example_spatial_05_APS_cum/deformation_velocity_ica_r2.pkl'
fig_title='GNSS & stacking(cum)'
GNSS_error_file='data/Altyn_Tagh_Fault/raw_data/GNSS_LOS/Wang_2020_JGR_altyn_2DGNSS2LOSErrorBar.txt'

with open(aps_phase_file, 'rb') as f:
    aps_phase= pickle.load(f)
with open(stacking_PCA_file,'rb') as f:
    stacking_PCA=pickle.load(f)
with open(stacking_ICA_file,'rb') as f:
    stacking_ICA=pickle.load(f)
GNSS=np.loadtxt(GNSS_flie)
GNSS_error_all=np.loadtxt(GNSS_error_file)
GNSS_error=GNSS_error_all[:,1]



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
print(GNSS_loss) 

# aps_phase 
aps_phase_loss=[]
for index in indices:
    i, j = index[0], index[1]
    array=np.copy(aps_phase[i-4:i+5, j-4:j+5])
    loss = np.nanmean(array)
    aps_phase_loss.append(loss)
aps_phase_loss = np.array(aps_phase_loss)
print("\naps_phase_loss:",aps_phase_loss)

#Wang的数据
# aps_phase_error=GNSS_error_all[:,5]

#stacking_PCA
stacking_PCA_loss=[]
for index in indices:
    i, j = index[0], index[1]
    array=np.copy(stacking_PCA[i-4:i+5, j-4:j+5])
    loss = np.nanmean(array)
    stacking_PCA_loss.append(loss)
stacking_PCA_loss = np.array(stacking_PCA_loss)
print("\nstacking_PCA_loss:",stacking_PCA_loss)

#stacking_ICA
stacking_ICA_loss=[]
for index in indices:
    i, j = index[0], index[1]
    array=np.copy(stacking_ICA[i-4:i+5, j-4:j+5])
    loss = np.nanmean(array)
    stacking_ICA_loss.append(loss)
stacking_ICA_loss = np.array(stacking_ICA_loss)
print("\nstacking_ICA_loss:",stacking_ICA_loss)

#error
aps_phase_error=aps_phase_loss-GNSS_loss
stacking_PCA_error=stacking_PCA_loss-GNSS_loss
stacking_ICA_error=stacking_ICA_loss-GNSS_loss
print("\naps_phase_error:",aps_phase_error)
print("\nstacking_PCA_error:",stacking_PCA_error)
print("\nstacking_ICA_error:",stacking_ICA_error)

#RMSE
def RMSE(x,y):
    return np.sqrt(np.nanmean((x-y)**2))
RMSE_aps=RMSE(GNSS_loss,aps_phase_loss)
RMSE_PCA=RMSE(GNSS_loss,stacking_PCA_loss)
RMSE_ICA=RMSE(GNSS_loss,stacking_ICA_loss)
print(f'RMSE_aps:{RMSE_aps}')
print(f'RMSE_PCA:{RMSE_PCA}')
print(f'RMSE_ICA:{RMSE_ICA}')


#------------------------------------PLOT-------------------------------------
min_val = -15
max_val = 5
min_scatter = -15
max_scatter = 5
scatter_size = 20  
c_scatter = 'black'
alpha_scatter=1
xaxis_bin=5
yaxis_bin=5 
x_position=0.55
y_position=0.05
cmap_use='hot'

font_path='Helvetica.ttf'
prop_title = font_manager.FontProperties(fname=font_path, size=20)
prop_label = font_manager.FontProperties(fname=font_path, size=16)
prop_text = font_manager.FontProperties(fname=font_path, size=14)
tick_fontsize = 14

fig,ax=plt.subplots(2,3,figsize=(18,12))
im1=ax[0,0].imshow(aps_phase,cmap=cmap_use, vmin=min_val, vmax=max_val, aspect='auto')
ax[0,0].set_title('APS_phase', fontproperties=prop_title)
im2=ax[0,1].imshow(stacking_PCA,cmap=cmap_use, vmin=min_val, vmax=max_val, aspect='auto')
ax[0,1].set_title('PhasePCA', fontproperties=prop_title)
im3=ax[0,2].imshow(stacking_ICA,cmap=cmap_use, vmin=min_val, vmax=max_val, aspect='auto')
ax[0,2].set_title('PhaseICA', fontproperties=prop_title)

for i in range(3):
    ax[0, i].set_xticks([])
    ax[0, i].set_yticks([])

# scatter
ax[1,0].scatter(GNSS_loss, aps_phase_loss, c=c_scatter, alpha=alpha_scatter, s=scatter_size)
ax[1,1].scatter(GNSS_loss, stacking_PCA_loss, c=c_scatter, alpha=alpha_scatter, s=scatter_size)
ax[1,2].scatter(GNSS_loss, stacking_ICA_loss, c=c_scatter, alpha=alpha_scatter, s=scatter_size)
ax[1,0].xaxis.set_major_locator(MaxNLocator(nbins=xaxis_bin))
ax[1,0].yaxis.set_major_locator(MaxNLocator(nbins=yaxis_bin))
ax[1,1].xaxis.set_major_locator(MaxNLocator(nbins=xaxis_bin))
ax[1,1].yaxis.set_major_locator(MaxNLocator(nbins=yaxis_bin))
ax[1,2].xaxis.set_major_locator(MaxNLocator(nbins=xaxis_bin))
ax[1,2].yaxis.set_major_locator(MaxNLocator(nbins=yaxis_bin))

#errorbar
ax[1,0].errorbar(GNSS_loss, aps_phase_loss, xerr=GNSS_error,yerr=aps_phase_error, fmt='o', color='black', ecolor='black', capsize=5, elinewidth=0.5)
ax[1,1].errorbar(GNSS_loss, stacking_PCA_loss, xerr=GNSS_error,yerr=stacking_PCA_error, fmt='o', color='black', ecolor='black', capsize=5, elinewidth=0.5)
ax[1,2].errorbar(GNSS_loss, stacking_ICA_loss, xerr=GNSS_error,yerr=stacking_ICA_error, fmt='o', color='black', ecolor='black', capsize=5, elinewidth=0.5)


for i in range(3):
    ax[1, i].set_xlim(min_scatter, max_scatter)
    ax[1, i].set_ylim(min_scatter, max_scatter)
    ax[1, i].plot([min_scatter, max_scatter], [min_scatter, max_scatter], 'r--', linewidth=1)
    ax[1, i].set_aspect('equal')
    ax[1, i].tick_params(axis='both', which='major', labelsize=tick_fontsize)

ax[1, 1].set_xlabel('GNSS LOS (mm/yr)', fontproperties=prop_label)  
ax[1, 0].set_ylabel('InSAR LOS (mm/yr)', fontproperties=prop_label)

#rmse
ax[1,0].text(x_position,y_position,f'RMSE={round(RMSE_aps, 3)}', fontproperties=prop_text, transform=ax[1,0].transAxes)
ax[1,1].text(x_position,y_position,f'RMSE={round(RMSE_PCA, 3)}', fontproperties=prop_text, transform=ax[1,1].transAxes)
ax[1,2].text(x_position,y_position,f'RMSE={round(RMSE_ICA, 3)}', fontproperties=prop_text, transform=ax[1,2].transAxes)

# lat and lon
x_offsets = []
y_offsets = []
for i in range(len(GNSS)):
    x_offset = (GNSS[i][0] - X_FIRST) / X_STEP
    y_offset = (GNSS[i][1] - Y_FIRST) / Y_STEP
    x_offsets.append(x_offset)
    y_offsets.append(y_offset)

im4=ax[0, 0].scatter(x_offsets, y_offsets, s=50,vmin=min_val,vmax=max_val, c=GNSS_loss, cmap=cmap_use, edgecolors='black')
ax[0, 1].scatter(x_offsets, y_offsets, s=50, vmin=min_val,vmax=max_val,c=GNSS_loss, cmap=cmap_use, edgecolors='black')
ax[0, 2].scatter(x_offsets, y_offsets, s=50,vmin=min_val,vmax=max_val, c=GNSS_loss, cmap=cmap_use, edgecolors='black')

#colorbar
cbar = fig.colorbar(im1, ax=ax.ravel().tolist(), orientation='vertical', shrink=0.4, aspect=10)
cbar.ax.yaxis.set_ticks_position('right')
cbar.ax.set_position([0.78, 0.55, 0.03, 0.3])
cbar.ax.set_xlabel('mm/yr', labelpad=15, fontproperties=prop_label)
cbar.ax.yaxis.set_major_locator(MaxNLocator(nbins=4))

# plt.tight_layout()
plt.savefig(f'{save_path}/{fig_title}.png')
plt.savefig(f'{save_path}/{fig_title}.pdf',format='pdf')
print("Done!!!")