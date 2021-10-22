# -*- coding: utf-8 -*-
"""
Created on Tue Feb 20 12:17:22 2018

@author: eemeg

An example of the ICASAR software with synthetic data

"""
#%% Imports

import numpy as np
import matplotlib.pyplot as plt 
import pickle                                    # used for opening synthetic data
from pathlib import Path

import icasar
from icasar.icasar_funcs import ICASAR
from icasar.aux import col_to_ma, r2_to_r3


#%% Things to set

ICASAR_settings = {"n_comp" : 5,                                        # number of components to recover with ICA (ie the number of PCA sources to keep)
                    "bootstrapping_param" : (200, 0),                   # (number of runs with bootstrapping, number of runs without bootstrapping)                    "hdbscan_param" : (35, 10),                        # (min_cluster_size, min_samples)
                    "tsne_param" : (30, 12),                            # (perplexity, early_exaggeration)
                    "ica_param" : (1e-2, 150),                          # (tolerance, max iterations)
                    "hdbscan_param" : (35,10),                          # (min_cluster_size, min_samples) Discussed in more detail in Mcinnes et al. (2017). min_cluster_size sets the smallest collection of points that can be considered a cluster. min_samples sets how conservative the clustering is. With larger values, more points will be considered noise. 
                    "out_folder" : Path('example_spatial_01_outputs'),  # outputs will be saved here
                    "figures" : "png+window"}                           # if png, saved in a folder as .png.  If window, open as interactive matplotlib figures,
                                                                        # if 'png+window', both.  
                                                                        # default is "window" as 03_clustering_and_manifold is interactive.  
#%% Import the data 

with open('synthetic_data.pkl', 'rb') as f:
    A_dc = pickle.load(f)                                           # these are the time courses and  are column vectors.  They control the strength through time of each of the synthetic sources.  
    S_synth = pickle.load(f)                                        # these are the synthetic (spatial) sources and are row vectors.  
    N_dc = pickle.load(f)                                           # these are the noise for each interferogarm.  
    pixel_mask = pickle.load(f)                                     # this is the same shape as an interferogram, True for pixels that are masked
    lons = pickle.load(f)                                           # the longitudes of the lower left corner of each pixel (i.e. a rank 2 array)
    lats = pickle.load(f)                                           # the latitues of the lower left corner of each pixel.  
   


#%% Make synthetic time series and view it
    
X_dc = A_dc @ S_synth + N_dc                                                  # do the mixing 
phUnw = X_dc                                                                    # mixtures are the unwrapped phase


fig1, axes = plt.subplots(2,3)                                                  # plot the synthetic sources
for i in range(3):
    axes[0,i].imshow(col_to_ma(S_synth[i,:], pixel_mask))
    axes[1,i].plot(range(A_dc.shape[0]), A_dc[:,i])
    axes[1,i].axhline(0)
fig1.suptitle('Synthetic sources and time courses')
fig1.canvas.set_window_title("Synthetic sources and time courses")


fig2, axes = plt.subplots(2,5)                                                        # plot the synthetic interferograms
for i, ax in enumerate(np.ravel(axes[:])):
    ax.imshow(col_to_ma(phUnw[i,:], pixel_mask))
fig2.suptitle('Mixtures (intererograms)')
fig2.canvas.set_window_title("Mixtures (intererograms)")

fig3, axes = plt.subplots(1,3, figsize = (11,4))                                # plot a schematic of how the data are organised
axes[0].imshow(X_dc, aspect = 500)
axes[0].set_title('Data matix')
axes[1].imshow(pixel_mask)
axes[1].set_title('Mask')
axes[2].imshow(col_to_ma(X_dc[0,:], pixel_mask))
axes[2].set_title('Interferogram 1')
fig3.canvas.set_window_title("Interferograms as row vectors and a mask")

#%% do ICA with ICSAR function

spatial_data = {'mixtures_r2' : phUnw,
                'mask'        : pixel_mask,
                'lons'        : lons,                                           # for the simplest case, these aren't needed
                'lats'        : lats}                                           # for the simplest case, these aren't needed

S_best, time_courses, x_train_residual_ts, Iq, n_clusters, S_all_info, phUnw_mean  = ICASAR(spatial_data = spatial_data, **ICASAR_settings) 
      

#%% We can reconstruct the data using the sources and timecourses, but don't forget that ICA returns mean centered sources 

X_dc_reconstructed = (time_courses @ S_best) + phUnw_mean                                           # here we add the mean back
X_dc_reconstructed_source0 = (time_courses[:,0:1] @ S_best[0:1,:]) + phUnw_mean                     # and remake the entire time series using only IC0

ifg_n = 0                                                                                           # choose an ifg to plot

fig4, axes = plt.subplots(1,3, figsize = (11,4))                                # plot a schematic of how the data are organised
im1 = axes[0].imshow(col_to_ma(X_dc[ifg_n,], pixel_mask))
axes[0].set_title('Original Ifg.')
fig4.colorbar(im1, ax = axes[0])
im2 = axes[1].imshow(col_to_ma(X_dc_reconstructed[ifg_n,], pixel_mask))
axes[1].set_title('Reconstructed Ifg.')
fig4.colorbar(im2, ax = axes[1])

im3 = axes[2].imshow(col_to_ma(X_dc_reconstructed_source0[ifg_n,], pixel_mask))
axes[2].set_title('Reconstructed Ifg. \n (IC0 only)')
fig4.colorbar(im2, ax = axes[2])

fig4.canvas.set_window_title("Reconstructed Data")


#%% Note that the amount of bootstrapping done by ICASAR can also be controlled, and seen in the clustering and 2d manifold plot:
    
ICASAR_settings["bootstrapping_param"] = (100, 100)               # (number of runs with bootstrapping, number of runs without bootstrapping)                  
ICASAR_settings['out_folder'] = 'example_spatial_01_outputs_part2'

spatial_data = {'mixtures_r2' : phUnw,
                'mask'        : pixel_mask,
                'lons'        : lons,
                'lats'        : lats}  
                   
S_best, time_courses, x_train_residual_ts, Iq, n_clusters, S_all_info, phUnw_mean  = ICASAR(spatial_data = spatial_data, **ICASAR_settings) 

