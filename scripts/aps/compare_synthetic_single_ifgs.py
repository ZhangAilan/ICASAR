#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/03/28
# Function:
#   The single interferogram is compared with the synthetic deformation(all)
#-------------------------------------------------------------------
def col_to_ma(col, pixel_mask):
    """ A function to take a column vector and a 2d pixel mask and reshape the column into a masked array.  
    Useful when converting between vectors used by BSS methods results that are to be plotted
    Inputs:
        col | rank 1 array | 
        pixel_mask | array mask (rank 2)
    Outputs:
        source | rank 2 masked array | colun as a masked 2d array
    """
    import numpy.ma as ma 
    import numpy as np
    
    source = ma.array(np.zeros(pixel_mask.shape), mask = pixel_mask )
    source.unshare_mask()
    source[~source.mask] = col.ravel()   
    return source
#------------------------------------------------------------------------------------------------------------
import numpy as np
import pickle
import os
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.ticker import MaxNLocator
font_manager._rebuild()

icasar_format='cum'  #here can change the 'all/cum/inc'
synthetic_deformation_path='data/Synthetic_Fault/结果/deformation_data/ifg_defo_subtract_reference.pkl'
aps_deformation_file_path='data/Synthetic_Fault/aps_data/CorrectedIfgs-model6-defoFlag1-wetFlag1-hydroFlag2-iteraNum1-solver2-ueFixMethod0-weightScheme1-shortBt60-shortBtRelax500'
ifgs_ica_path='example_spatial_03_APS_{}/deformation_ifgs_ICA_series.pkl'.format(icasar_format)
ifgs_pca_path='example_spatial_03_APS_{}/deformation_ifgs_PCA_series.pkl'.format(icasar_format)
mask_path='example_spatial_03_APS_{}/mask.pkl'.format(icasar_format)
raw_ifgs_path='data/Synthetic_Fault/raw_data/simDatasetsConsiderDefHydroWet'
ifg_filelist_path='data/Synthetic_Fault/raw_data/simDatasetsConsiderDefHydroWet/ifg_filelist.txt'
dates_path='data/Synthetic_Fault/temp_corrected/tbaseline_info.pkl'
save_path='data/Synthetic_Fault/结果/compare_results/single_compare_{}'.format(icasar_format)


#load the dates 
with open(dates_path, 'rb') as f:
    dates_all = pickle.load(f)
converted_dates = dates_all['ifg_dates']
# print("\nconverted_dates:",converted_dates)

#load the synthetic deformation
with open(synthetic_deformation_path, 'rb') as f:
    synthetic_deformation_data = pickle.load(f)
# print("\nsynthetic_deformation.shape:",synthetic_deformation_data.shape)

#load the icasar results
with open(ifgs_ica_path, 'rb') as f:
    ifgs_ica = pickle.load(f)
with open(ifgs_pca_path, 'rb') as f:
    ifgs_pca = pickle.load(f)
with open(mask_path, 'rb') as f:
    mask = pickle.load(f)
# print("\nifgs_ica.shape:",ifgs_ica.shape)
# print("\nifgs_pca.shape:",ifgs_pca.shape)
# print("\nmask.shape:",mask.shape)


unw_names=[]
for date_range in converted_dates:
    start_date,end_date=date_range.split('_')  
    unw_name=f"geo_{start_date}-{end_date}.unw"
    unw_names.append(unw_name)
# print("\nunw_names:",unw_names)
line_numbers=[]  #save the line number of the unw_names
with open(ifg_filelist_path,'r') as f:
    for i,line in enumerate(f,start=1):
        if any(name in line for name in unw_names):
            line_numbers.append(i)
# print("\nline_numbers:",line_numbers)
# print("\nlen(line_numbers):",len(line_numbers))

aps_corrected_ifgs=[]
for date_range in converted_dates:
    start_date,end_date=date_range.split('_')  
    aps_corrected_ifg=f"geo_{start_date}-{end_date}.unw.APScorrected"
    aps_corrected_ifgs.append(aps_corrected_ifg)
# print("\naps_corrected_ifgs:",aps_corrected_ifgs)

#begin loop to plot the compare results
for i in range(len(line_numbers)):
    #load the data
    index=line_numbers[i]-1
    synthetic_deformation=synthetic_deformation_data[:, :, index].T #synthetic deformation
    deformation_mask=np.where(mask,np.nan,synthetic_deformation)

    ica_deformation=col_to_ma(ifgs_ica[i,:],mask) #ica deformation
    pca_deformation=col_to_ma(ifgs_pca[i,:],mask) #pca deformation
    # print("\nica_deformation.shape:",ica_deformation.shape)
    # plt.imshow(ica_deformation)
    # plt.show()

    with open(os.path.join(raw_ifgs_path,unw_names[i]), 'rb') as f: #raw ifg
        raw_ifg=np.fromfile(f, dtype='>f4').reshape(207, 235)
    raw_ifg = np.ma.array(raw_ifg, mask=mask)

    with open(os.path.join(aps_deformation_file_path,aps_corrected_ifgs[i]), 'rb') as f: #aps deformation
        aps_deformation=np.fromfile(f, dtype='>f4').reshape(207, 235)
    aps_deformation = np.ma.array(aps_deformation, mask=mask)


    #----------------------------PLOT-----------------------------------
    # 设置更大的图像和字体大小
    fig, axes = plt.subplots(2, 4, figsize=(20, 10), gridspec_kw={'width_ratios': [1, 1, 1, 1]})
    cmap_use = 'jet'

    tick_fontsize = 14
    xaxis_bin=4
    yaxis_bin=4
    scatter_color = (11/255, 35/255, 204/255)
    font_path='Helvetica.ttf'
    prop_title = font_manager.FontProperties(fname=font_path, size=20)
    prop_label = font_manager.FontProperties(fname=font_path, size=16)

    min_val = -0.02
    max_val = 0.08
    im1 = axes[0, 0].imshow(deformation_mask, cmap=cmap_use, vmin=min_val, vmax=max_val, aspect='auto')
    axes[0, 0].set_title('Synthetic defo', fontproperties=prop_title)
    im2=axes[0, 1].imshow(aps_deformation, cmap=cmap_use, vmin=min_val, vmax=max_val, aspect='auto')
    axes[0, 1].set_title('APS_phase', fontproperties=prop_title)
    im3=axes[0, 2].imshow(pca_deformation, cmap=cmap_use, vmin=min_val, vmax=max_val, aspect='auto')
    axes[0, 2].set_title('PhasePCA', fontproperties=prop_title)
    im4=axes[0, 3].imshow(ica_deformation, cmap=cmap_use, vmin=min_val, vmax=max_val, aspect='auto')
    axes[0, 3].set_title('PhaseICA', fontproperties=prop_title)
    for j in range(4):
        axes[0, j].set_xticks([])
        axes[0, j].set_yticks([])

    cbar_ax = inset_axes(axes[1,0], width="5%", height="80%", loc='center')
    fig.colorbar(im1, cax=cbar_ax)
    cbar_ax.yaxis.set_ticks_position('right')
    cbar_ax.yaxis.set_label_position('right')
    cbar_ax.tick_params(labelsize=tick_fontsize)
    cbar_ax.set_xlabel('rad',labelpad=15, fontproperties=prop_label)
    #设置颜色条的刻度数量
    cbar_ax.yaxis.set_major_locator(MaxNLocator(nbins=4))

    # scatter
    xlim = (-0.02, 0.08)
    ylim = (-0.02, 0.08)


    # 绘制 1:1 线
    for ax_row in axes[1:]:
        for ax in ax_row[1:]:
            ax.plot(xlim, ylim, 'k--', c='r', linewidth=1)

    # 设置限制
    for ax_row in axes[1:]:
        for ax in ax_row[1:]:
            ax.set_xlim(xlim)
            ax.set_ylim(ylim)

    scatter_size = 0.01
    axes[1, 0].axis('off')
    axes[1, 1].scatter(synthetic_deformation.ravel(), aps_deformation.ravel(),c=scatter_color, s=scatter_size, alpha=0.7)
    axes[1, 1].set_xlabel('Synthetic defo.(rad)',fontproperties=prop_label)
    axes[1, 1].set_ylabel('Recovered defo.(rad)',fontproperties=prop_label)
    axes[1, 1].set_aspect('equal')
    axes[1, 1].tick_params(axis='both', which='major', labelsize=tick_fontsize)
    axes[1, 1].xaxis.set_major_locator(MaxNLocator(integer=True,nbins=xaxis_bin))
    axes[1, 1].yaxis.set_major_locator(MaxNLocator(integer=True,nbins=yaxis_bin))

    axes[1, 2].scatter(synthetic_deformation.ravel(), pca_deformation.ravel(),c=scatter_color, s=scatter_size, alpha=0.7)
    axes[1, 2].set_xlabel('Synthetic defo.(rad)', fontproperties=prop_label)
    axes[1, 2].set_ylabel('Recovered defo.(rad)',  fontproperties=prop_label)
    axes[1, 2].set_aspect('equal')
    axes[1, 2].tick_params(axis='both', which='major', labelsize=tick_fontsize)
    axes[1, 2].xaxis.set_major_locator(MaxNLocator(integer=True,nbins=xaxis_bin))
    axes[1, 2].yaxis.set_major_locator(MaxNLocator(integer=True,nbins=yaxis_bin))

    axes[1, 3].scatter(synthetic_deformation.ravel(), ica_deformation.ravel(),c=scatter_color,s=scatter_size, alpha=0.7)
    axes[1, 3].set_xlabel('Synthetic defo.(rad)',fontproperties=prop_label)
    axes[1, 3].set_ylabel('Recovered defo.(rad)',fontproperties=prop_label)
    axes[1, 3].set_aspect('equal')
    axes[1, 3].tick_params(axis='both', which='major', labelsize=tick_fontsize)
    axes[1, 3].xaxis.set_major_locator(MaxNLocator(integer=True,nbins=xaxis_bin))
    axes[1, 3].yaxis.set_major_locator(MaxNLocator(integer=True,nbins=yaxis_bin))

    plt.tight_layout()
    plt.savefig(os.path.join(save_path, '{}.png'.format(converted_dates[i])))
    plt.savefig(os.path.join(save_path, '{}.pdf'.format(converted_dates[i])), format='pdf')
    plt.close()
    print("\nsave the compare results of {} successfully!\n".format(converted_dates[i]))
    # break

print("\nAll the compare results have been saved successfully!")