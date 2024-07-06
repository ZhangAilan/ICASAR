#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/05/13
# Function:
#   读取单一干涉图比较后所得的RMSE，STD，CORRELATION
#   绘制三幅图像，横轴为raw干涉图的RMSE，STD，CORRELATION，纵轴分别为APS、PCA、ICA干涉图的RMSE，STD，CORRELATION
#-------------------------------------------------------------------
import numpy as np
import os
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import matplotlib.font_manager as font_manager
font_manager._rebuild()

RMSE_results_file='scripts/计算单一干涉图的slope、correlation/rmse_results.txt'
STD_results_file='scripts/计算单一干涉图的slope、correlation/std_results.txt'
CORRELATION_results_file='scripts/计算单一干涉图的slope、correlation/corr_results.txt'
slope_results_file='scripts/计算单一干涉图的slope、correlation/slope_results.txt'
RMSE_reduction_results_file='scripts/计算单一干涉图的slope、correlation/rmse_reduction_results.txt'
std_reduction_results_file='scripts/计算单一干涉图的slope、correlation/std_reduction_results.txt'
save_path='data/Synthetic_Fault/结果/compare_results/single_compare_cum'


# 读取RMSE，STD，CORRELATION
# 每列数据分别为raw、APS、PCA、ICA
RMSE_results=np.loadtxt(RMSE_results_file)
STD_results=np.loadtxt(STD_results_file)
CORRELATION_results=np.loadtxt(CORRELATION_results_file)
slope_results=np.loadtxt(slope_results_file)
RMSE_reduction_results=np.loadtxt(RMSE_reduction_results_file)
std_reduction_results=np.loadtxt(std_reduction_results_file)

#分别获取每一列
raw_RMSE=RMSE_results[:,0]
raw_STD=STD_results[:,0]
raw_CORRELATION=CORRELATION_results[:,0]
raw_slope=slope_results[:,0]

APS_RMSE=RMSE_results[:,1]
APS_STD=STD_results[:,1]
APS_CORRELATION=CORRELATION_results[:,1]
APS_slope=slope_results[:,1]
APS_RMSE_reduction=RMSE_reduction_results[:,0]
APS_std_reduction=std_reduction_results[:,0]

PCA_RMSE=RMSE_results[:,2]
PCA_STD=STD_results[:,2]
PCA_CORRELATION=CORRELATION_results[:,2]
PCA_slope=slope_results[:,2]
PCA_RMSE_reduction=RMSE_reduction_results[:,1]
PCA_std_reduction=std_reduction_results[:,1]

ICA_RMSE=RMSE_results[:,3]
ICA_STD=STD_results[:,3]
ICA_CORRELATION=CORRELATION_results[:,3]
ICA_slope=slope_results[:,3]
ICA_RMSE_reduction=RMSE_reduction_results[:,2]
ICA_std_reduction=std_reduction_results[:,2]

#-----------------------------------------PLOT-----------------------------------------
c_APS_phase=(141/255,169/255,186/255,1)
c_PhasePCA=(73/255,84/255,132/255,1)
c_PhaseICA=(204/255,54/255,53/255,1)
alpha_set=0.5
s_set = 30
bin = 10
xaxis_bin=5
yaxis_bin=5
font_path='Helvetica.ttf'
prop = font_manager.FontProperties(fname=font_path, size=15)  # 设置字体
prop_lengend = font_manager.FontProperties(fname=font_path, size=10)  # 设置标注字体



# Create a figure with 2 rows and 3 columns of subplots
fig, ax = plt.subplots(2, 3, figsize=(13, 6))

# Scatter plots
ax[0, 0].scatter(raw_RMSE, APS_RMSE, label='APS_phase', color=c_APS_phase, s=s_set, alpha=alpha_set)
ax[0, 0].scatter(raw_RMSE, PCA_RMSE, label='PhasePCA', color=c_PhasePCA, s=s_set, alpha=alpha_set)
ax[0, 0].scatter(raw_RMSE, ICA_RMSE, label='PhaseICA', color=c_PhaseICA, s=s_set, alpha=alpha_set)
ax[0, 0].set_xlabel('RMSE of original ifgs', fontproperties=prop)
ax[0, 0].set_ylabel('RMSE of corrected ifgs', fontproperties=prop)
ax[0, 0].legend(prop=prop_lengend)
ax[0, 0].set_ylim(bottom=0)
ax[0, 0].xaxis.set_major_locator(MaxNLocator(nbins=xaxis_bin)) 
ax[0, 0].yaxis.set_major_locator(MaxNLocator(nbins=yaxis_bin))

ax[0, 1].scatter(raw_STD, APS_STD, label='APS_phase', color=c_APS_phase, s=s_set, alpha=alpha_set)
ax[0, 1].scatter(raw_STD, PCA_STD, label='PhasePCA', color=c_PhasePCA, s=s_set, alpha=alpha_set)
ax[0, 1].scatter(raw_STD, ICA_STD, label='PhaseICA', color=c_PhaseICA, s=s_set, alpha=alpha_set)
ax[0, 1].set_xlabel('STD of original ifgs',fontproperties=prop)
ax[0, 1].set_ylabel('STD of corrected ifgs',fontproperties=prop)
ax[0,1].xaxis.set_major_locator(MaxNLocator(nbins=xaxis_bin))
ax[0,1].yaxis.set_major_locator(MaxNLocator(nbins=yaxis_bin))

ax[0, 2].scatter(raw_CORRELATION, APS_CORRELATION, label='APS_phase', color=c_APS_phase, s=s_set, alpha=alpha_set)
ax[0, 2].scatter(raw_CORRELATION, PCA_CORRELATION, label='PhasePCA', color=c_PhasePCA, s=s_set, alpha=alpha_set)
ax[0, 2].scatter(raw_CORRELATION, ICA_CORRELATION, label='PhaseICA', color=c_PhaseICA, s=s_set, alpha=alpha_set)
ax[0, 2].set_xlabel('Correlation of original ifgs ', fontsize=14, fontproperties=prop)
ax[0, 2].set_ylabel('Correlation of corrected ifgs', fontsize=14, fontproperties=prop)
ax[0, 2].xaxis.set_major_locator(MaxNLocator(nbins=xaxis_bin))
ax[0, 2].yaxis.set_major_locator(MaxNLocator(nbins=yaxis_bin))

# Histograms
ax[1, 0].hist(APS_RMSE, bins=bin, label='APS_phase', color=c_APS_phase, alpha=alpha_set, edgecolor='black')
ax[1, 0].hist(PCA_RMSE, bins=bin, label='PhasePCA', color=c_PhasePCA, alpha=alpha_set, edgecolor='black')
ax[1, 0].hist(ICA_RMSE, bins=bin, label='PhaseICA', color=c_PhaseICA, alpha=alpha_set, edgecolor='black')
ax[1, 0].set_xlabel('RMSE of corrected ifgs', fontproperties=prop)
ax[1, 0].set_ylabel('Frequency',  fontproperties=prop)
ax[1, 0].legend(prop=prop_lengend)
ax[1, 0].xaxis.set_major_locator(MaxNLocator(nbins=xaxis_bin))
ax[1, 0].yaxis.set_major_locator(MaxNLocator(nbins=yaxis_bin))

ax[1, 1].hist(APS_STD, bins=bin, label='APS_phase', color=c_APS_phase, alpha=alpha_set, edgecolor='black')
ax[1, 1].hist(PCA_STD, bins=bin, label='PhasePCA', color=c_PhasePCA, alpha=alpha_set, edgecolor='black')
ax[1, 1].hist(ICA_STD, bins=bin, label='PhaseICA', color=c_PhaseICA, alpha=alpha_set, edgecolor='black')
ax[1, 1].set_xlabel('STD of corrected ifgs', fontproperties=prop)
ax[1, 1].set_ylabel('Frequency', fontproperties=prop)
ax[1, 1].xaxis.set_major_locator(MaxNLocator(nbins=xaxis_bin))
ax[1, 1].yaxis.set_major_locator(MaxNLocator(nbins=yaxis_bin))


# 绘制APS_CORRELATION直方图
counts_APS, bins_APS = np.histogram(APS_CORRELATION, bins=5)
percentages_APS = (counts_APS / counts_APS.sum()) * 100
ax[1, 2].bar(bins_APS[:-1], percentages_APS, width=np.diff(bins_APS), color=c_APS_phase, alpha=alpha_set, edgecolor='black', label='APS_phase')

# 绘制PCA_CORRELATION直方图
counts_PCA, bins_PCA = np.histogram(PCA_CORRELATION, bins=50)
percentages_PCA = (counts_PCA / counts_PCA.sum()) * 100
ax[1, 2].bar(bins_PCA[:-1], percentages_PCA, width=0.25*np.diff(bins_PCA), color=c_PhasePCA, alpha=alpha_set, edgecolor='black', label='PhasePCA')

# 绘制ICA_CORRELATION直方图
counts_ICA, bins_ICA = np.histogram(ICA_CORRELATION, bins=50)
percentages_ICA = (counts_ICA / counts_ICA.sum()) * 100
ax[1, 2].bar(bins_ICA[:-1], percentages_ICA, width=0.25*np.diff(bins_ICA), color=c_PhaseICA, alpha=alpha_set, edgecolor='black', label='PhaseICA')
ax[1, 2].set_xlim(0.92, 1)

ax[1, 2].set_xlabel('Correlation of corrected ifgs', fontproperties=prop)
ax[1, 2].set_ylabel('Frequency', fontproperties=prop)
ax[1, 2].xaxis.set_major_locator(MaxNLocator(nbins=xaxis_bin))
ax[1, 2].yaxis.set_major_locator(MaxNLocator(nbins=yaxis_bin))

plt.tight_layout()
plt.savefig(os.path.join(save_path, 'RMSE_STD_CORRELATION.pdf'), format='pdf')
plt.savefig(os.path.join(save_path, 'RMSE_STD_CORRELATION.png'))
print("Finish the RMSE_STD_CORRELATION plot!!!")

plt.close()

#plot slope, RMSE reduction, STD reduction
fig, ax = plt.subplots(2, 3, figsize=(13, 6))

# Scatter plots
ax[0, 0].scatter(raw_slope, APS_slope, label='APS_phase', color=c_APS_phase, s=s_set, alpha=alpha_set)
ax[0, 0].scatter(raw_slope, PCA_slope, label='PhasePCA', color=c_PhasePCA, s=s_set, alpha=alpha_set)
ax[0, 0].scatter(raw_slope, ICA_slope, label='PhaseICA', color=c_PhaseICA, s=s_set, alpha=alpha_set)
ax[0, 0].set_xlabel('Slope of original ifgs',fontproperties=prop)
ax[0, 0].set_ylabel('Slope of corrected ifgs',fontproperties=prop)
ax[0, 0].legend(prop=prop_lengend)
ax[0,0].xaxis.set_major_locator(MaxNLocator(nbins=xaxis_bin))
ax[0,0].yaxis.set_major_locator(MaxNLocator(nbins=yaxis_bin))

ax[0, 1].scatter(raw_RMSE, APS_RMSE_reduction, label='APS_phase', color=c_APS_phase, s=s_set, alpha=alpha_set)
ax[0, 1].scatter(raw_RMSE, PCA_RMSE_reduction, label='PhasePCA', color=c_PhasePCA, s=s_set, alpha=alpha_set)
ax[0, 1].scatter(raw_RMSE, ICA_RMSE_reduction, label='PhaseICA', color=c_PhaseICA, s=s_set, alpha=alpha_set)
ax[0, 1].set_xlabel('RMSE of original ifgs',fontproperties=prop)
ax[0, 1].set_ylabel('RMSE reduction',fontproperties=prop)
ax[0, 1].xaxis.set_major_locator(MaxNLocator(nbins=xaxis_bin))
ax[0, 1].yaxis.set_major_locator(MaxNLocator(nbins=yaxis_bin))

ax[0, 2].scatter(raw_STD, APS_std_reduction, label='APS_phase', color=c_APS_phase, s=s_set, alpha=alpha_set)
ax[0, 2].scatter(raw_STD, PCA_std_reduction, label='PhasePCA', color=c_PhasePCA, s=s_set, alpha=alpha_set)
ax[0, 2].scatter(raw_STD, ICA_std_reduction, label='PhaseICA', color=c_PhaseICA, s=s_set, alpha=alpha_set)
ax[0, 2].set_xlabel('STD of original ifgs',fontproperties=prop)
ax[0, 2].set_ylabel('STD reduction',fontproperties=prop)
ax[0, 2].xaxis.set_major_locator(MaxNLocator(nbins=xaxis_bin))
ax[0, 2].yaxis.set_major_locator(MaxNLocator(nbins=yaxis_bin))

#histogram
ax[1, 0].hist(APS_slope, bins=bin, label='APS_phase', color=c_APS_phase, alpha=alpha_set, edgecolor='black')
ax[1, 0].hist(PCA_slope, bins=bin, label='PhasePCA', color=c_PhasePCA, alpha=alpha_set, edgecolor='black')
ax[1, 0].hist(ICA_slope, bins=bin, label='PhaseICA', color=c_PhaseICA, alpha=alpha_set, edgecolor='black')
ax[1, 0].set_xlabel('Slope of corrected ifgs',fontproperties=prop)
ax[1, 0].set_ylabel('Frequency',fontproperties=prop)
ax[1, 0].legend(prop=prop_lengend)
ax[1, 0].xaxis.set_major_locator(MaxNLocator(nbins=xaxis_bin))
ax[1, 0].yaxis.set_major_locator(MaxNLocator(nbins=yaxis_bin))

ax[1, 1].hist(APS_RMSE_reduction, bins=bin, label='APS_phase', color=c_APS_phase, alpha=alpha_set, edgecolor='black')
ax[1, 1].hist(PCA_RMSE_reduction, bins=bin, label='PhasePCA', color=c_PhasePCA, alpha=alpha_set, edgecolor='black')
ax[1, 1].hist(ICA_RMSE_reduction, bins=bin, label='PhaseICA', color=c_PhaseICA, alpha=alpha_set, edgecolor='black')
ax[1, 1].set_xlabel('RMSE reduction of corrected ifgs',fontproperties=prop)
ax[1, 1].set_ylabel('Frequency',fontproperties=prop)
ax[1, 1].xaxis.set_major_locator(MaxNLocator(nbins=xaxis_bin)) 
ax[1, 1].yaxis.set_major_locator(MaxNLocator(nbins=yaxis_bin))


ax[1, 2].hist(APS_std_reduction, bins=bin, label='APS_phase', color=c_APS_phase, alpha=alpha_set, edgecolor='black')
ax[1, 2].hist(PCA_std_reduction, bins=bin, label='PhasePCA', color=c_PhasePCA, alpha=alpha_set, edgecolor='black')
ax[1, 2].hist(ICA_std_reduction, bins=bin, label='PhaseICA', color=c_PhaseICA, alpha=alpha_set, edgecolor='black')
ax[1, 2].set_xlabel('STD reduction of corrected ifgs', fontproperties=prop)
ax[1, 2].set_ylabel('Frequency',fontproperties=prop)
ax[1, 2].xaxis.set_major_locator(MaxNLocator(nbins=xaxis_bin))
ax[1, 2].yaxis.set_major_locator(MaxNLocator(nbins=yaxis_bin))

plt.tight_layout()
plt.savefig(os.path.join(save_path, 'slope_RMSE_STD_reduction.png'))
plt.savefig(os.path.join(save_path, 'slope_RMSE_STD_reduction.pdf'), format='pdf')
print("Done!!!")