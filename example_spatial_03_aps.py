#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/01/19
# Function:
#   ICASAR for the Synthetic data with APS corrected
#-------------------------------------------------------------------
import pickle
import numpy as np

filepath_displacement='data/Synthetic_Fault/temp_corrected/displacement_r2.pkl'
filepath_tbaselines='data/Synthetic_Fault/temp_corrected/tbaseline_info.pkl'
with open(filepath_displacement, 'rb') as f:
    displacement_r2 = pickle.load(f)
with open(filepath_tbaselines,'rb') as f:
    tbaseline_info=pickle.load(f)
#print("\ntbaseline_info['baselines_cumulative']:\n",tbaseline_info['baselines_cumulative'])
time_baselines_cum=tbaseline_info['baselines_cumulative']
mask=displacement_r2['mask']

#ICASAR settings
from pathlib import Path
from icasar.icasar_funcs import ICASAR


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
                   "out_folder": Path('example_spatial_03_APS_inc'),  # outputs will be saved here
                   "load_fastICA_results": True, # If all the FastICA runs already exisit, setting this to True speeds up ICASAR as they don't need to be recomputed.
                   "ifgs_format": 'inc', # small signals are hard for ICA to extact from time series, so make it easier by creating all possible long temporal baseline ifgs from the incremental data.
                   'sica_tica': 'sica',  # controls whether spatial sources or time courses are independent.
                   'max_n_all_ifgs': 1000,
                   'label_sources': True, # ICASAR will try to identify which sources are deformation / topo. correlated APS / turbulent Aps.
                   "figures": "png+window"}  # if png, saved in a folder as .png.  If window, open as interactive matplotlib figures,if 'png+window', both.default is "window" as 03_clustering_and_manifold is interactive.
S_ica, A_ica, x_train_residual_ts, Iq, n_clusters, S_all_info, phUnw_mean, sources_labels,S_pca,A_pca = ICASAR(spatial_data=spatial_data, **ICASAR_settings)
# print("\nS_ica:\n",S_ica)
# print("\nA_ica:\n",A_ica)
# print("\nS_pca:\n",S_pca)
# print("\nA_pca:\n",A_pca)

phUnw_mean = phUnw_mean[:, np.newaxis]
print("\n",ICASAR_settings["ifgs_format"])


                                              #%%% results visualisation
from icasar.aux1 import visualise_ICASAR_inversion
from icasar.aux3 import recover_signal_timeseries_plot,plot_mixtures_ifgs,stacking_insar
from icasar.aux1 import col_to_ma
import os
import pickle
file_path=ICASAR_settings['out_folder']

figures='png+window'
fig_title='BSS reconstruction'
visualise_ICASAR_inversion(spatial_data['ifgs_dc'],S_ica,A_ica,displacement_r2['mask'],n_data=10,png_path=file_path,figures=figures,fig_title=fig_title)

#plot the original ifgs
plot_mixtures_ifgs(displacement_r2['incremental'],displacement_r2['mask'],file_path)


#plot the recovered signal time series
#need to change the figure title
fig_title_01='deformation_ifgs_ICA'
fig_title_02='topo_cor_APS_ifgs'
fig_title_03='deformation_ifgs_PCA'
recover_signal_timeseries_plot(S_ica,A_ica,0,mask,file_path,fig_title_01,phUnw_mean)
#recover_signal_timeseries_plot(S_ica,A_ica,5,mask,file_path,fig_title_02,phUnw_mean)

#use the recovered signal to calculate the deformation velocity by stacking insar
deformation_velocity_ica=stacking_insar(S_ica,A_ica,0,mask,file_path,time_baselines_cum,phUnw_mean,fig_title=fig_title_01)
deformation_velocity_pca=stacking_insar(S_pca,A_pca,0,mask,file_path,time_baselines_cum,phUnw_mean,fig_title=fig_title_03)

#save the deformation velocity as pkl
deformation_velocity_ica_r2=col_to_ma(deformation_velocity_ica,mask)
deformation_velocity_pca_r2=col_to_ma(deformation_velocity_pca,mask)
with open(os.path.join(file_path,'deformation_velocity_ica_r2.pkl'),'wb') as f:
    pickle.dump(deformation_velocity_ica_r2,f)
with open(os.path.join(file_path,'deformation_velocity_pca_r2.pkl'),'wb') as f:
    pickle.dump(deformation_velocity_pca_r2,f)

print("Done!!!")