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
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import matplotlib.font_manager as font_manager
from matplotlib.ticker import MaxNLocator
font_manager._rebuild()

#file path
save_path='data/Synthetic_Fault/结果/compare_results'
deformation_flie='data/Synthetic_Fault/结果/deformation_data/velocity.pkl'
aps_phase_file='data/Synthetic_Fault/结果/aps_corrected_stacking/velocity.pkl'
mask='data/Synthetic_Fault/mask.pkl'

stacking_PCA_file='example_spatial_03_APS_cum/deformation_velocity_pca_r2.pkl'
stacking_ICA_file='example_spatial_03_APS_cum/deformation_velocity_ica_r2.pkl'
fig_title='deformation & stacking(cum)'

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
RMSE_defor=RMSE(deformation_mask,deformation_mask)
print(f'RMSE_aps:{RMSE_aps}')
print(f'RMSE_PCA:{RMSE_PCA}')
print(f'RMSE_ICA:{RMSE_ICA}')
print(f'RMSE_defor:{RMSE_defor}')


# 颜色范围
min_val = -1
max_val = 4

# 设置更大的图像和字体大小
fig, ax = plt.subplots(2, 4, figsize=(20, 10), gridspec_kw={'width_ratios': [1, 1, 1, 1]})
plt.subplots_adjust(wspace=0.3, hspace=0.3)

font_path='Helvetica.ttf'
prop_title = font_manager.FontProperties(fname=font_path, size=20)
prop_label = font_manager.FontProperties(fname=font_path, size=16)
prop_text = font_manager.FontProperties(fname=font_path, size=14)
tick_fontsize = 14

im1 = ax[0, 0].imshow(deformation_mask, cmap='jet', vmin=min_val, vmax=max_val, aspect='auto')
ax[0, 0].set_title('Synthetic defo rate',fontproperties=prop_title)
im2 = ax[0, 1].imshow(aps_phase, cmap='jet', vmin=min_val, vmax=max_val, aspect='auto')
ax[0, 1].set_title('APS_phase', fontproperties=prop_title)
im4 = ax[0, 2].imshow(stacking_PCA, cmap='jet', vmin=min_val, vmax=max_val, aspect='auto')
ax[0, 2].set_title('PhasePCA', fontproperties=prop_title)
im3 = ax[0, 3].imshow(stacking_ICA, cmap='jet', vmin=min_val, vmax=max_val, aspect='auto')
ax[0, 3].set_title('PhaseICA', fontproperties=prop_title)

# 移除上排的轴刻度和标签
for i in range(4):
    ax[0, i].set_xticks([])
    ax[0, i].set_yticks([])

# 第二行：散点图
scatter_color = (11/255, 35/255, 204/255)
scatter_size = 0.01
xaxis_bin=5
yaxis_bin=5
ax[1, 0].axis('off')
ax[1, 1].scatter(deformation_mask.flatten(), aps_phase.flatten(), c=scatter_color,s=scatter_size, alpha=0.7)
ax[1, 2].scatter(deformation_mask.flatten(), stacking_PCA.flatten(),c=scatter_color, s=scatter_size, alpha=0.7)
ax[1, 3].scatter(deformation_mask.flatten(), stacking_ICA.flatten(), c=scatter_color,s=scatter_size, alpha=0.7)
ax[1, 1].xaxis.set_major_locator(MaxNLocator(integer=True,nbins=xaxis_bin))
ax[1, 1].yaxis.set_major_locator(MaxNLocator(integer=True,nbins=yaxis_bin))
ax[1, 2].xaxis.set_major_locator(MaxNLocator(integer=True,nbins=xaxis_bin))
ax[1, 2].yaxis.set_major_locator(MaxNLocator(integer=True,nbins=yaxis_bin))
ax[1, 3].xaxis.set_major_locator(MaxNLocator(integer=True,nbins=xaxis_bin))
ax[1, 3].yaxis.set_major_locator(MaxNLocator(integer=True,nbins=yaxis_bin))
#添加rmse文本,设定参数确定位置
x_position=0.6
y_position=0.05
ax[1, 1].text(x_position, y_position, f'RMSE:{RMSE_aps:.4f}', fontproperties=prop_text, transform=ax[1, 1].transAxes)
ax[1, 2].text(x_position, y_position, f'RMSE:{RMSE_PCA:.4f}', fontproperties=prop_text, transform=ax[1, 2].transAxes)
ax[1, 3].text(x_position, y_position, f'RMSE:{RMSE_ICA:.4f}', fontproperties=prop_text, transform=ax[1, 3].transAxes)


# 设置限制和对角线
for i in range(1,4):
    ax[1, i].set_xlim(min_val, max_val)
    ax[1, i].set_ylim(min_val, max_val)
    ax[1, i].plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=1)
    ax[1, i].set_aspect('equal')
    ax[1, i].tick_params(axis='both', which='major', labelsize=tick_fontsize)

# 标签和标题
for i in range(1,4):
    ax[1, i].set_xlabel('Synthetic defo.(rad/yr)', fontproperties=prop_label)
ax[1, 1].set_ylabel('Recovered defo.(rad/yr)', fontproperties=prop_label)

# 添加颜色条
cbar_ax = inset_axes(ax[1,0], width="5%", height="80%", loc='center')
fig.colorbar(im1, cax=cbar_ax)
cbar_ax.yaxis.set_ticks_position('right')
cbar_ax.yaxis.set_label_position('right')
cbar_ax.tick_params(labelsize=tick_fontsize)
cbar_ax.set_xlabel('rad/yr',labelpad=15, fontproperties=prop_label)

# Save figure
plt.savefig(f'{save_path}/{fig_title}.png')
# plt.savefig(f'{save_path}/{fig_title}.svg',format='svg')
plt.savefig(f'{save_path}/{fig_title}.pdf', format='pdf')
print("Done!!!")