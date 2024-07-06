#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/05/06
# Function:
#   比较单独ICA、APS+ICA、APS+PCA
#-------------------------------------------------------------------
import numpy as np
import pickle
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import matplotlib.font_manager as font_manager
from matplotlib.ticker import MaxNLocator
font_manager._rebuild()
from matplotlib.ticker import PercentFormatter

#file path
save_path='data/Synthetic_Fault/结果/disscussion/单独ICA比较'
deformation_flie='data/Synthetic_Fault/结果/deformation_data/velocity.pkl'
only_ICA_file='example_spatial_03_cum/deformation_velocity_ica_r2.pkl'
mask='data/Synthetic_Fault/mask.pkl'

#cum
stacking_PCA_file='example_spatial_03_APS_cum/deformation_velocity_pca_r2.pkl'
stacking_ICA_file='example_spatial_03_APS_cum/deformation_velocity_ica_r2.pkl'
fig_title='单独ICA比较'


with open(stacking_PCA_file,'rb') as f:
    stacking_PCA=pickle.load(f)
with open(stacking_ICA_file,'rb') as f:
    stacking_ICA=pickle.load(f)
with open(only_ICA_file,'rb') as f:
    only_ICA=pickle.load(f)

with open(deformation_flie,'rb') as f:
    deformation_true=pickle.load(f)
with open(mask,'rb') as f:
    mask=pickle.load(f)
deformation_mask=np.where(mask,np.nan,deformation_true)

#RMSE
def RMSE(x,y):
    return np.sqrt(np.nanmean((x-y)**2))
RMSE_aps=RMSE(deformation_mask,only_ICA)
RMSE_PCA=RMSE(deformation_mask,stacking_PCA)
RMSE_ICA=RMSE(deformation_mask,stacking_ICA)
print(f'RMSE_aps:{RMSE_aps}')
print(f'RMSE_PCA:{RMSE_PCA}')
print(f'RMSE_ICA:{RMSE_ICA}')

#color range
min_val = -1
max_val = 7


font_path='Helvetica.ttf'
prop_title = font_manager.FontProperties(fname=font_path, size=20)
prop_label = font_manager.FontProperties(fname=font_path, size=16)
prop_text = font_manager.FontProperties(fname=font_path, size=14)
tick_fontsize = 14

#stacking ifgs
fig,ax=plt.subplots(2,3,figsize=(18,10))
im1=ax[0,0].imshow(only_ICA,cmap='jet', vmin=min_val, vmax=max_val, aspect='auto')
ax[0,0].set_title('ICA', fontproperties=prop_title)
im2=ax[0,1].imshow(stacking_PCA,cmap='jet', vmin=min_val, vmax=max_val, aspect='auto')
ax[0,1].set_title('PhasePCA', fontproperties=prop_title)
im3=ax[0,2].imshow(stacking_ICA,cmap='jet', vmin=min_val, vmax=max_val, aspect='auto')
ax[0,2].set_title('PhaseICA', fontproperties=prop_title)

for i in range(3):
    ax[0, i].set_xticks([])
    ax[0, i].set_yticks([])


#colorbar
cbar = fig.colorbar(im1, ax=ax.ravel().tolist(), orientation='vertical', shrink=0.4, aspect=10)
cbar.ax.yaxis.set_ticks_position('right')
cbar.ax.set_position([0.78, 0.55, 0.03, 0.3])
cbar.ax.set_xlabel('rad/yr', labelpad=15, fontproperties=prop_label)

#scatter
scatter_color = (11/255, 35/255, 204/255)
scatter_size = 0.01
xaxis_bin=5
yaxis_bin=5 
ax[1,0].scatter(deformation_mask.flatten(), only_ICA.flatten(), s=scatter_size, c=scatter_color, alpha=0.7)
ax[1,1].scatter(deformation_mask.flatten(), stacking_PCA.flatten(), s=scatter_size, c=scatter_color, alpha=0.7)
ax[1,2].scatter(deformation_mask.flatten(), stacking_ICA.flatten(), s=scatter_size, c=scatter_color, alpha=0.7)
ax[1,0].xaxis.set_major_locator(MaxNLocator(nbins=xaxis_bin))
ax[1,0].yaxis.set_major_locator(MaxNLocator(nbins=yaxis_bin))
ax[1,1].xaxis.set_major_locator(MaxNLocator(nbins=xaxis_bin))
ax[1,1].yaxis.set_major_locator(MaxNLocator(nbins=yaxis_bin))
ax[1,2].xaxis.set_major_locator(MaxNLocator(nbins=xaxis_bin))
ax[1,2].yaxis.set_major_locator(MaxNLocator(nbins=yaxis_bin))

#rmse
x_position=0.55
y_position=0.05
ax[1,0].text(x_position,y_position,f'RMSE={round(RMSE_aps, 3)}', fontproperties=prop_text, transform=ax[1,0].transAxes)
ax[1,1].text(x_position,y_position,f'RMSE={round(RMSE_PCA, 3)}', fontproperties=prop_text, transform=ax[1,1].transAxes)
ax[1,2].text(x_position,y_position,f'RMSE={round(RMSE_ICA, 3)}', fontproperties=prop_text, transform=ax[1,2].transAxes)

for i in range(3):
    ax[1, i].set_xlim(min_val, max_val)
    ax[1, i].set_ylim(min_val, max_val)
    ax[1, i].plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=1)
    ax[1, i].set_aspect('equal')
    ax[1, i].tick_params(axis='both', which='major', labelsize=tick_fontsize)

for i in range(3):
    ax[1, i].set_xlabel('Synthetic rate.(rad/yr)', fontproperties=prop_label)
ax[1, 0].set_ylabel('Recovered rate.(rad/yr)', fontproperties=prop_label)

plt.savefig(f'{save_path}/{fig_title}.png')
plt.savefig(f'{save_path}/{fig_title}.pdf',format='pdf')
plt.close()

#计算各个与模拟值的差值，并绘制直方图
diff_OnlyICA=deformation_mask-only_ICA  
diff_PCA=deformation_mask-stacking_PCA
diff_ICA=deformation_mask-stacking_ICA

fig1,ax1=plt.subplots(1,3,figsize=(18,5))
ax1[0].hist(diff_OnlyICA.flatten(), bins=10, edgecolor='black')
ax1[1].hist(diff_PCA.flatten(), bins=10, edgecolor='black')
ax1[2].hist(diff_ICA.flatten(), bins=10, edgecolor='black')

# Set y-axis as percentage
ax1[0].yaxis.set_major_formatter(PercentFormatter(xmax=len(diff_OnlyICA.flatten())))
ax1[1].yaxis.set_major_formatter(PercentFormatter(xmax=len(diff_PCA.flatten())))
ax1[2].yaxis.set_major_formatter(PercentFormatter(xmax=len(diff_ICA.flatten())))

# Reduce the number of y-axis ticks
ax1[0].yaxis.set_major_locator(MaxNLocator(nbins=1))
ax1[1].yaxis.set_major_locator(MaxNLocator(nbins=1))
ax1[2].yaxis.set_major_locator(MaxNLocator(nbins=1))
ax1[0].xaxis.set_major_locator(MaxNLocator(nbins=1))
ax1[1].xaxis.set_major_locator(MaxNLocator(nbins=1))
ax1[2].xaxis.set_major_locator(MaxNLocator(nbins=1))
plt.tight_layout()
plt.savefig(f'{save_path}/{fig_title}_hist.png')
plt.savefig(f'{save_path}/{fig_title}_hist.pdf',format='pdf')
plt.savefig(f'{save_path}/{fig_title}_hist.svg',format='svg')


print("Done!!!")