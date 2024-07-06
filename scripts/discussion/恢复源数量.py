#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/05/06
# Function:
#   讨论设置不同恢复源信号数量时对ICASAR分离信号的影响
#   统计n_component=2,3,4,5,6时的PCA与ICA的stacking与deformation的均方根误差（format全部为cum）
#-------------------------------------------------------------------
import numpy as np
import pickle
from matplotlib import pyplot as plt
import matplotlib.font_manager as font_manager
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.ticker import MaxNLocator
font_manager._rebuild()

def RMSE(x,y):
    return np.sqrt(np.nanmean((x-y)**2))
n_components=[2,3,4,5,6]
n_components = [int(x) for x in n_components]
save_path='data/Synthetic_Fault/结果/disscussion/恢复源数量'
deformation_flie='data/Synthetic_Fault/结果/deformation_data/velocity.pkl'
aps_phase_file='data/Synthetic_Fault/结果/aps_corrected_stacking/velocity.pkl'
with open(deformation_flie,'rb') as f:
    deformation=pickle.load(f)
with open(aps_phase_file,'rb') as f:
    aps_phase=pickle.load(f)

RMSE_PCA=[]
RMSE_ICA=[]
RMSE_aps=[]
for i in range(len(n_components)):
    stacking_PCA_file='example_spatial_03_APS_n{}_cum\deformation_velocity_pca_r2.pkl'.format(n_components[i])
    stacking_ICA_file='example_spatial_03_APS_n{}_cum\deformation_velocity_ica_r2.pkl'.format(n_components[i])
    with open(stacking_PCA_file,'rb') as f:
        stacking_PCA=pickle.load(f)
    with open(stacking_ICA_file,'rb') as f:
        stacking_ICA=pickle.load(f)
    
    RMSE_PCA.append(RMSE(deformation,stacking_PCA))
    RMSE_ICA.append(RMSE(deformation,stacking_ICA))
    RMSE_aps.append(RMSE(deformation,aps_phase))
print(f'RMSE_PCA:{RMSE_PCA}')
print(f'RMSE_ICA:{RMSE_ICA}')
print(f'RMSE_aps:{RMSE_aps}')

# Plotting the data
plt.figure(figsize=(6, 6))
font_path='Helvetica.ttf'
tick_size = 16
prop_title = font_manager.FontProperties(fname=font_path, size=20)
prop_label = font_manager.FontProperties(fname=font_path, size=25)

#rgb color
#rgb(214,65,65)
#rgb(78,77,77)
c_ica=(214/255,65/255,65/255)
plt.plot(n_components, RMSE_ICA, marker='o', color=c_ica, label='ICA')
plt.legend(prop=prop_label)

plt.xlabel('Number of Components', fontproperties=prop_label, fontsize=16)
plt.ylabel('RMSE of corrected velocity', fontproperties=prop_label, fontsize=16)

# Modify the tick size
plt.xticks(fontsize=14)
plt.yticks(fontsize=14)
ax = plt.gca()
ax.xaxis.set_major_locator(MaxNLocator(integer=True, nbins=5))
ax.yaxis.set_major_locator(MaxNLocator(nbins=5))
plt.tight_layout()
plt.savefig(f'{save_path}/恢复源信号数量.png')
plt.savefig(f'{save_path}/恢复源信号数量.pdf',format='pdf')
print('Done!!!')