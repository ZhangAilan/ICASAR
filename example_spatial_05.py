#--------------------------------阿尔金断裂带---------------------------------------------
#读取数据
import pickle
import matplotlib.pyplot as plt
import numpy as np

filepath_displacement='D:\\ML_InSAR\\data\\阿尔金断裂带\\temp_date\\displacement_r2.pkl'
filepath_tbaselines='D:\\ML_InSAR\\data\\阿尔金断裂带\\temp_date\\tbaseline_info.pkl'
with open(filepath_displacement, 'rb') as f:
    displacement_r2 = pickle.load(f)
with open(filepath_tbaselines,'rb') as f:
    tbaseline_info=pickle.load(f)
#print("\ntbaseline_info['baselines_cumulative']:\n",tbaseline_info['baselines_cumulative'])
time_baselines_cum=tbaseline_info['baselines_cumulative']
mask=displacement_r2['mask']

#ICASAR部分
from pathlib import Path
from icasar.icasar_main import ICASAR


                         #%% Example 1: sICA after creating all interferograms
spatial_data = {'ifgs_dc': displacement_r2['incremental'],
                'mask': displacement_r2['mask'],
                'ifg_dates_dc': tbaseline_info['ifg_dates'],
                'dem': displacement_r2['dem'],
                'lons': displacement_r2['lons'],
                'lats': displacement_r2['lats']}
# print('\nifg_dates_dc:\n',spatial_data['ifg_dates_dc'])
# print()

ICASAR_settings = {"n_comp": 5,  # number of components to recover with ICA (ie the number of PCA sources to keep)
                   "bootstrapping_param": (200, 0), # (number of runs with bootstrapping, number of runs without bootstrapping)                    "hdbscan_param" : (35, 10),                        # (min_cluster_size, min_samples)
                   "tsne_param": (30, 12),  # (perplexity, early_exaggeration)
                   "ica_param": (1e-2, 150),  # (tolerance, max iterations)
                   "hdbscan_param": (100, 10), # (min_cluster_size, min_samples) Discussed in more detail in Mcinnes et al. (2017). min_cluster_size sets the smallest collection of points that can be considered a cluster. min_samples sets how conservative the clustering is. With larger values, more points will be considered noise.
                   "out_folder": Path('example_spatial_05_outputs_sICA_inc'),  # outputs will be saved here
                   "load_fastICA_results": True, # If all the FastICA runs already exisit, setting this to True speeds up ICASAR as they don't need to be recomputed.
                   "ifgs_format": 'inc', # small signals are hard for ICA to extact from time series, so make it easier by creating all possible long temporal baseline ifgs from the incremental data.
                   'sica_tica': 'sica',  # controls whether spatial sources or time courses are independent.
                   'max_n_all_ifgs': 1000,
                   'label_sources': True, # ICASAR will try to identify which sources are deformation / topo. correlated APS / turbulent Aps.
                   "figures": "png+window"}  # if png, saved in a folder as .png.  If window, open as interactive matplotlib figures,if 'png+window', both.default is "window" as 03_clustering_and_manifold is interactive.
S_ica, A_ica, x_train_residual_ts, Iq, n_clusters, S_all_info, phUnw_mean, sources_labels = ICASAR(spatial_data=spatial_data, **ICASAR_settings)
#print("\nS_ica:\n",S_ica)
#print("\nA_ica:\n",A_ica)

phUnw_mean = phUnw_mean[:, np.newaxis]
print("\n",ICASAR_settings["ifgs_format"])
print('重建干涉图与原始干涉图之间的RMSE:',x_train_residual_ts)


                                              #%%% 结果判读部分
from icasar.icasar_aux import visualise_ICASAR_inversion
from icasar.icasar_aux3 import recover_signal_timeseries_plot,plot_mixtures_ifgs,stacking_insar
file_path=ICASAR_settings['out_folder']

#原始干涉图与恢复的干涉图进行对比 We can also visualise how interferograms are fit using the learned components (ICs, contained in S_best)
figures='png+window'
fig_title='BSS reconstruction'
visualise_ICASAR_inversion(spatial_data['ifgs_dc'],S_ica,A_ica,displacement_r2['mask'],n_data=10,png_path=file_path,figures=figures,fig_title=fig_title)

#绘制原始干涉图
plot_mixtures_ifgs(displacement_r2['incremental'],displacement_r2['mask'],file_path)


#绘制恢复源信号的干涉图序列
#需指定对应源信号的编号
fig_title_01='deformation_ifgs'
fig_title_02='topo_cor_APS_ifgs'
recover_signal_timeseries_plot(S_ica,A_ica,2,mask,file_path,fig_title_01,phUnw_mean)
recover_signal_timeseries_plot(S_ica,A_ica,0,mask,file_path,fig_title_02,phUnw_mean)

#使用stacking_insar计算并绘制地表形变平均速率图
deformation_velocity=stacking_insar(S_ica,A_ica,2,mask,file_path,time_baselines_cum,phUnw_mean)