#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/06/24
# Function:
#   比较all/cum/inc的平均速率
#-------------------------------------------------------------------
import numpy as np
import pickle
from matplotlib import pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
import matplotlib.font_manager as font_manager
from matplotlib.ticker import MaxNLocator
font_manager._rebuild()

save_path='data/Synthetic_Fault/结果/compare_results'
deformation_flie='data/Synthetic_Fault/结果/deformation_data/velocity.pkl'
mask='data/Synthetic_Fault/mask.pkl'

all_ICA_file='example_spatial_03_APS_all/deformation_velocity_ica_r2.pkl'
cum_ICA_file='example_spatial_03_APS_cum/deformation_velocity_ica_r2.pkl'
inc_ICA_file='example_spatial_03_APS_inc/deformation_velocity_ica_r2.pkl'

with open(all_ICA_file,'rb') as f:
    all_ICA=pickle.load(f)
with open(cum_ICA_file,'rb') as f:
    cum_ICA=pickle.load(f)
with open(inc_ICA_file,'rb') as f:
    inc_ICA=pickle.load(f)
with open(deformation_flie,'rb') as f:
    deformation_true=pickle.load(f)
with open(mask,'rb') as f:
    mask=pickle.load(f)

deformation_true=np.where(mask,np.nan,deformation_true)

#RMSE
def RMSE(x,y):
    return np.sqrt(np.nanmean((x-y)**2))
RMSE_all=RMSE(deformation_true,all_ICA)
RMSE_cum=RMSE(deformation_true,cum_ICA)
RMSE_inc=RMSE(deformation_true,inc_ICA)

#plot
# 颜色范围
min_val = -1
max_val = 4
cmap_use='jet'

# 设置更大的图像和字体大小
fig, ax = plt.subplots(2, 4, figsize=(20, 10), gridspec_kw={'width_ratios': [1, 1, 1, 1]})
plt.subplots_adjust(wspace=0.3, hspace=0.3)

font_path='Helvetica.ttf'
prop_title = font_manager.FontProperties(fname=font_path, size=20)
prop_label = font_manager.FontProperties(fname=font_path, size=16)
prop_text = font_manager.FontProperties(fname=font_path, size=14)
tick_fontsize = 14

im1=ax[0,0].imshow(deformation_true, cmap=cmap_use, vmin=min_val, vmax=max_val, aspect='auto')
ax[0,0].set_title('Synthetic defo rate', fontproperties=prop_title)
im3=ax[0,1].imshow(cum_ICA, cmap=cmap_use, vmin=min_val, vmax=max_val, aspect='auto')
ax[0,1].set_title('Format:Cum', fontproperties=prop_title)
im2=ax[0,2].imshow(all_ICA, cmap=cmap_use, vmin=min_val, vmax=max_val, aspect='auto')
ax[0,2].set_title('Format:All', fontproperties=prop_title)
im4=ax[0,3].imshow(inc_ICA, cmap=cmap_use, vmin=min_val, vmax=max_val, aspect='auto')
ax[0,3].set_title('Format:Inc', fontproperties=prop_title)

for i in range(4):
    ax[0, i].set_xticks([])
    ax[0, i].set_yticks([])

scatter_color = (11/255, 35/255, 204/255)
scatter_size = 0.01
xaxis_bin=5
yaxis_bin=5
ax[1, 0].axis('off')
ax[1,1].scatter(deformation_true.flatten(), cum_ICA.flatten(), s=scatter_size, c=scatter_color, alpha=0.7)
ax[1,2].scatter(deformation_true.flatten(), all_ICA.flatten(), s=scatter_size, c=scatter_color, alpha=0.7)
ax[1,3].scatter(deformation_true.flatten(), inc_ICA.flatten(), s=scatter_size, c=scatter_color, alpha=0.7)
ax[1, 1].xaxis.set_major_locator(MaxNLocator(integer=True,nbins=xaxis_bin))
ax[1, 1].yaxis.set_major_locator(MaxNLocator(integer=True,nbins=yaxis_bin))
ax[1, 2].xaxis.set_major_locator(MaxNLocator(integer=True,nbins=xaxis_bin))
ax[1, 2].yaxis.set_major_locator(MaxNLocator(integer=True,nbins=yaxis_bin))
ax[1, 3].xaxis.set_major_locator(MaxNLocator(integer=True,nbins=xaxis_bin))
ax[1, 3].yaxis.set_major_locator(MaxNLocator(integer=True,nbins=yaxis_bin))

x_position=0.6
y_position=0.05
ax[1,1].text(x_position, y_position, f'RMSE:{RMSE_cum:.3f}', fontproperties=prop_text, transform=ax[1,1].transAxes)
ax[1,2].text(x_position, y_position, f'RMSE:{RMSE_all:.3f}', fontproperties=prop_text, transform=ax[1,2].transAxes)
ax[1,3].text(x_position, y_position, f'RMSE:{RMSE_inc:.3f}', fontproperties=prop_text, transform=ax[1,3].transAxes)

for i in range(1,4):
    ax[1, i].set_xlim(min_val, max_val)
    ax[1, i].set_ylim(min_val, max_val)
    ax[1, i].plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=1)
    ax[1, i].set_aspect('equal')
    ax[1, i].tick_params(axis='both', which='major', labelsize=tick_fontsize)

for i in range(1,4):
    ax[1, i].set_xlabel('Synthetic rate.(rad/yr)', fontproperties=prop_label)
ax[1, 1].set_ylabel('Recovered rate.(rad/yr)', fontproperties=prop_label)

cbar_ax = inset_axes(ax[1,0], width="5%", height="80%", loc='center')
fig.colorbar(im1, cax=cbar_ax)
cbar_ax.yaxis.set_ticks_position('right')
cbar_ax.yaxis.set_label_position('right')
cbar_ax.tick_params(labelsize=tick_fontsize)
cbar_ax.set_xlabel('rad/yr',labelpad=15, fontproperties=prop_label)

plt.savefig(f'{save_path}/compare_all_cum_inc_velocity.png')
plt.savefig(f'{save_path}/compare_all_cum_inc_velocity.pdf',format='pdf')
plt.close()

# #计算cum、all、inc与模拟值的插值，并绘制直方图
# diff_cum=deformation_true-cum_ICA
# diff_all=deformation_true-all_ICA
# diff_inc=deformation_true-inc_ICA
# #绘制三个直方图在一副图中
# fig1,ax1=plt.subplots(1,3,figsize=(10,5))
# ax1[0].hist(diff_cum.flatten(),bins=10,range=(-1,1),color='blue',alpha=0.7,density=True)
# ax1[1].hist(diff_all.flatten(),bins=10,range=(-1,1),color='green',alpha=0.7,density=True)
# ax1[2].hist(diff_inc.flatten(),bins=10,range=(-1,1),color='red',alpha=0.7,density=True)
# plt.savefig(f'{save_path}/histogram_all_cum_inc_velocity.png')
# plt.savefig(f'{save_path}/histogram_all_cum_inc_velocity.pdf',format='pdf')

print("Done!!!")