#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 17 18:19:37 2019

@author: matthew
"""

#%%

def two_spatial_signals_plot(images, mask, dem, tcs_dc, tcs_all, t_baselines_dc, t_baselines_all, 
                             title, ifg_dates_dc, fig_kwargs):
    """
    Product the two plots that show spatial sources.  
    Inputs:
        images | n_images x n_pixels | spatial signals as row vectors.  
        mask | boolean rank 2 |         mask to convert row vector to a masked array.  
        dem | rank 2 masked array |         The DEM.  Used to compare spatial signals to it.  
        tcs_dcs | n_times x n_images      | daisy chain time courses.  
        tcs_all | n_all_ifgs x n_images or None  | time courses if we have made all possible ifg pairs.  None if not available.  
        t_baselines_dc | n_times         | temporal baselines for the diasy chain interferograms.  
        t_baselines_all | n_all_ifgs     | temporal baselines for all possible ifg pairs, None if not available.  
        title | string | figure title
        fig_kwargs | dict | see other functions.  
    Returns:
        2 figures
        dem_to_sources_comparisons | dict | results of comparison between spatial sources and DEM.  xyzs: x and y and colours for each point from kernel density estimate, line_xys | list | xy points for line of best fit. corr_coefs | pearson correlation coefficeint for points.  
        tcs_to_tempbaselines_comparisons | dict | as above, but correlations between temporal baselines and time courses (ie if long temrpoal baseline, is component used strongly.  )
       
    History:
        2021_11_23 | MEG | Written
        2022_01_14 | MEG | Add return of comparison dicts.  
        
    """
    
    # 1: First figure is simpler as only use daisy chain time courses
    plot_spatial_signals(images.T, mask, tcs_dc.T, mask.shape, title = f"{title}_time",
                         temporal_baselines = t_baselines_dc, ifg_dates_dc = ifg_dates_dc, **fig_kwargs)                      # the usual plot of the sources and their time courses (ie contributions to each ifg)                              

    # 2: Second figure may have access to all interfergram time courses and temporal baselines, but may also not.          
    if t_baselines_all is not None:
        temporal_data = {'tcs'                : tcs_all,
                         'temporal_baselines' : t_baselines_all}
    else:
        temporal_data = {'tcs'                : tcs_dc,
                         'temporal_baselines' : t_baselines_dc}
        
    dem_to_sources_comparisons, tcs_to_tempbaselines_comparisons = dem_and_temporal_source_figure(images, mask, fig_kwargs, dem, temporal_data, fig_title = f"{title}_correlations")        # also compare the sources to the DEM, and the correlation between their time courses and the temporal baseline of each interferogram.                                                                                                              # 
                                                                                                                                                                                            # also note that it now returns information abou the sources and correlatiosn (comparison to the DEM, and how they're used in time.  )
    return dem_to_sources_comparisons, tcs_to_tempbaselines_comparisons


  
  
#%%
def plot_spatial_signals(spatial_map, pixel_mask, tcs, shape, title, ifg_dates_dc, 
                         temporal_baselines, figures = "window",  png_path = './'):
    """
    Input:
        spatial map | pxc matrix of c component maps (p pixels) (i.e. images are column vectors)
        pixel_mask | mask to turn spaital maps back to regular grided masked arrays
        tcs | cxt matrix of c time courses (t long)   
        shape | tuple | the shape of the grid that the spatial maps are reshaped to
        title | string | figure tite and png filename (nb .png will be added, don't include here)
        temporal_baselines | x axis values for time courses.  Useful if some data are missing (ie the odd 24 day ifgs in a time series of mainly 12 day)
        figures | string,  "window" / "png" / "png+window" | controls if figures are produced (either as a window, saved as a png, or both)
        png_path | string | if a png is to be saved, a path to a folder can be supplied, or left as default to write to current directory.  
        
    Returns:
        Figure, either as a window or saved as a png
        
    2017/02/17 | modified to use masked arrays that are given as vectors by spatial map, but can be converted back to 
                 masked arrays using the pixel mask    
    2017/05/12 | shared scales as decribed in 'shared'
    2017/05/15 | remove shared colorbar for spatial maps
    2017/10/16 | remove limit on the number of componets to plot (was 5)
    2017/12/06 | Add a colorbar if the plots are shared, add an option for the time courses to be done in days
    2017/12/?? | add the option to pass temporal baselines to the function
    2020/03/03 | MEG | Add option to save figure as png and close window
    """
    
    import numpy as np
    import numpy.ma as ma  
    import matplotlib.pyplot as plt
    import matplotlib
    import matplotlib.gridspec as gridspec
    import pdb
    
    from icasar.aux2 import remappedColorMap, truncate_colormap
    
    def linegraph(sig, ax, temporal_baselines = None):
        """ signal is a 1xt row vector """
        
        if temporal_baselines is None:
            times = sig.size
            a = np.arange(times)
        else:
            a = np.cumsum(temporal_baselines)                                        # cumulative baselines from temporal baselines.  
        ax.scatter(a,sig,marker='.', color='k', alpha = 0.5)
        ax.plot(a,sig, linestyle = '-', color='k',)
        ax.axhline(y=0, color='k', alpha=0.4) 
        
    def xticks_every_3months(ax_to_update, day0_date, time_values, include_tick_labels):
        """Given an axes, update the xticks so the major ones are the 1st of jan/april/july/october, and the minor ones are the first of the 
        other months.  
        Inputs:
            ax_to_update | matplotlib axes | the axes to update.  
            day0_date | string | in form yyyymmdd
            time_values | rank 1 array | cumulative temporal baselines, e.g. np.array([6,18, 30, 36, 48])
        Returns:
            updates axes
        History:
            2021_09_27 | MEG | Written
        """
        import datetime as dt
        from dateutil.relativedelta import relativedelta                                                    # add 3 months and check not after end
        from matplotlib.ticker import AutoMinorLocator      
        
       
        xtick_label_angle = 315
        
        tick_labels_days = ax_to_update.get_xticks().tolist()                                                # get the current tick labels
        day0_date_dt = dt.datetime.strptime(day0_date, "%Y%m%d")                                            
        dayend_date_dt = day0_date_dt +  dt.timedelta(int(time_values[-1]))                                 # the last time value is the number of days we have, so add this to day0 to get the end.  
    
        # 1: find first tick date (the first of the jan/ april/jul /oct)                        
        date_tick0 = day0_date_dt                                                                           
        while not ( (date_tick0.day) == 1 and (date_tick0.month == 1  or date_tick0.month == 4 or date_tick0.month == 7 or date_tick0.month == 10 )):
            date_tick0 +=  dt.timedelta(1)
            
        # 2: get all the other first of the quarters
        ticks = {'datetimes' : [date_tick0],
                 'yyyymmdd'   : [],
                 'n_day'     : []}
       
        while ticks['datetimes'][-1] < (dayend_date_dt - relativedelta(months=+3)):                         # subtract 3 months to make sure we don't go one 3 month jump too far. 
            ticks['datetimes'].append(ticks['datetimes'][-1] + relativedelta(months=+3))
        
        # 3: work out what day number each first of the quarter is.  
        for tick_dt in ticks['datetimes']:                                                                   # find the day nubmers from this.             
            ticks['yyyymmdd'].append(dt.datetime.strftime(tick_dt, "%Y/%m/%d"))
            ticks['n_day'].append((tick_dt - day0_date_dt).days)
            
        # 4: Update the figure.  
        ax_to_update.set_xticks(ticks['n_day'])                                                                   # apply major tick labels to the figure
        minor_locator = AutoMinorLocator(3)                                                                       # there are three months in each quarter, so a minor tick every month
        ax_to_update.xaxis.set_minor_locator(minor_locator)                                                       # add to figure.  
        if include_tick_labels:
            ax_to_update.set_xticklabels(ticks['yyyymmdd'], rotation = xtick_label_angle, ha = 'left')            # update tick labels, and rotate
            plt.subplots_adjust(bottom=0.15)
            ax_to_update.set_xlabel('Date')
        else:
            ax_to_update.set_xticklabels([])                                                                    # remove any tick lables if they aren't to be used.  
        
        # add vertical lines every year.  
        for major_tick_n, datetime_majortick in enumerate(ticks['datetimes']):
            if datetime_majortick.month == 1:
                ax_to_update.axvline(x = ticks['n_day'][major_tick_n], color='k', alpha=0.1, linestyle='--')           
        
 
    
    # colour map stuff
    ifg_colours = plt.get_cmap('coolwarm')
    cmap_mid = 1 - np.max(spatial_map)/(np.max(spatial_map) + abs(np.min(spatial_map)))          # get the ratio of the data that 0 lies at (eg if data is -15 to 5, ratio is 0.75)
    if cmap_mid < (1/257):                                                                       # this is a fudge so that if plot starts at 0 doesn't include the negative colorus for the smallest values
        ifg_colours_cent = remappedColorMap(ifg_colours, start=0.5, midpoint=0.5, stop=1.0, name='shiftedcmap')
    else:
        ifg_colours_cent = remappedColorMap(ifg_colours, start=0.0, midpoint=cmap_mid, stop=1.0, name='shiftedcmap')
    
    #make a list of ifgs as masked arrays (and not column vectors)
    spatial_maps_ma = []
    for i in range(np.size(spatial_map,1)):
        spatial_maps_ma.append(ma.array(np.zeros(pixel_mask.shape), mask = pixel_mask ))
        spatial_maps_ma[i].unshare_mask()
        spatial_maps_ma[i][~spatial_maps_ma[i].mask] = spatial_map[:,i].ravel()
    tmp, n_sources = spatial_map.shape
#    if n_sources > 5:
#        n_sources = 5
    del tmp
    
    day0_date = ifg_dates_dc[0][:8]
    
    #import pdb; pdb.set_trace()
    
    fig1 = plt.figure(figsize=(14,8))
    #f.suptitle(title, fontsize=14)
    grid = gridspec.GridSpec(n_sources, 6, wspace=0.3, hspace=0.3)                        # divide into 2 sections, 1/5 for ifgs and 4/5 for components
    fig1.canvas.manager.set_window_title(title)
    for i in range(n_sources):    
        # 0: define axes
        ax_source = plt.Subplot(fig1, grid[i,0])                                                                                        # spatial pattern
        ax_ctc = plt.Subplot(fig1, grid[i,1:])                                                                                          # ctc = cumulative time course
        # 1: plot the images (sources)
        im = ax_source.matshow(spatial_maps_ma[i], cmap = ifg_colours_cent, vmin = np.min(spatial_map), vmax = np.max(spatial_map))
        ax_source.set_xticks([])
        ax_source.set_yticks([])

        linegraph(np.cumsum(tcs[i,:]), ax_ctc, temporal_baselines)
        if i != (n_sources-1):
            xticks_every_3months(ax_ctc, day0_date, np.cumsum(temporal_baselines), include_tick_labels = False)                     # no tick labels
        else:
            xticks_every_3months(ax_ctc, day0_date, np.cumsum(temporal_baselines), include_tick_labels = True)                      # unles the last one.  
            
        # if shared ==1:
        #     ax_ctc.set_ylim([np.min(np.cumsum(tcs)), np.max(np.cumsum(tcs))])
        ax_ctc.yaxis.tick_right()
        fig1.add_subplot(ax_source)
        fig1.add_subplot(ax_ctc)
            
    ax_source.set_xlabel('Spatial sources')
    ax_ctc.set_xlabel('Cumulative time courses')
            
    # if shared == 1:                                                             # if the colourbar is shared between each subplot, the axes need extending to make space for it.
    #     #fig1.tight_layout(rect=[0.1, 0, 1., 1])
    cax = fig1.add_axes([0.03, 0.1, 0.01, 0.3])
    fig1.colorbar(im, cax=cax, orientation='vertical')
    #pdb.set_trace()
    
    if figures == 'window':                                                                 # possibly save the output
        pass
    elif figures == "png":
        try:
            fig1.savefig(f"{png_path}/{title}.png")
            plt.close()
        except:
            print(f"Failed to save the figure.  Trying to continue.  ")
    elif figures == 'png+window':
        try:
            fig1.savefig(f"{png_path}/{title}.png")
        except:
            print(f"Failed to save the figure.  Trying to continue.  ")
    else:
        pass
    
    

#%%

def dem_and_temporal_source_figure(sources, sources_mask, fig_kwargs, dem = None, temporal_data = None, fig_title = None,
                                   max_pixels = 1000):
    """ Given sources recovered by a blind signal separation method (e.g. PCA or ICA) compare them in space to hte DEM,
    and in time to the temporal baselines.  
    Inputs:
        sources | rank 2 array | as row vectors.  eg. 5 x999 for 5 sources.  
        sources_mask | rank 2 | boolean array with a True value for any masked pixel.  Number of False pixels should be the same as the number of columns in row_vectors
        fig_kwargs | dict | pass straing to plot_source_tc_correlations, see that for details.  
        dem | masked array | a DEM as a masked array.  It should work if not availble.  
        temporal data | dict | contains the temporal_baselines and the tcs (time courses).  It should work if not available.  
        fig_title | string | sets the window title and the name of the .png produced.  
        
    Returns:
        Figure
        dem_to_sources_comparisons | dict | results of comparison between spatial sources and DEM.  xyzs: x and y and colours for each point from kernel density estimate, line_xys | list | xy points for line of best fit. corr_coefs | pearson correlation coefficeint for points.  
        tcs_to_tempbaselines_comparisons | dict | as above, but correlations between temporal baselines and time courses (ie if long temrpoal baseline, is component used strongly.  )
        
    History:
        2021_09_12 | MEG | Written.  
        2022_01_14 | MEG | Add return of comparison dicts.  
    """
    import numpy as np
    import numpy.ma as ma
    
    from icasar.aux2 import update_mask_sources_ifgs

    def reduce_n_pixs(r2_arrays, n_pixels_new):
        """
        """
        n_pixels_old = r2_arrays[0].shape[1]                                # each pixel is a new column
        index = np.arange(n_pixels_old)
        np.random.shuffle(index)
        r2_arrays_new = []
        index = index[:n_pixels_new]
        for r2_array in r2_arrays:
            r2_arrays_new.append(r2_array[:, index])
        return r2_arrays_new
    
    if fig_title is not None:
        print(f"Starting to create the {fig_title} figure:")
    
    if dem is not None:
        dem_ma = ma.masked_invalid(dem)                                                                                                             # LiCSBAS dem uses nans, but lets switch to a masked array (with nans masked)
        dem_new_mask, sources_new_mask, mask_both = update_mask_sources_ifgs(sources_mask, sources,                             # this takes mask and data as row vectors for one set of masked pixels (the sources from pca) 
                                                                             ma.getmask(dem_ma), ma.compressed(dem_ma)[np.newaxis,:])            # and the mask and data as row vectors from the other set of masked pixels (the DEM, hence why it's being turned into a row vector)
        
        [sources_new_mask, dem_new_mask] = reduce_n_pixs([sources_new_mask, dem_new_mask], max_pixels)                                                          # possibly reduce the number of pixels to speed things up (kernel density estimate is slow)
        dem_to_sources_comparisons = signals_to_master_signal_comparison(sources_new_mask, dem_new_mask, density = True)                                        # And then we can do kernel density plots for each IC and the DEM
        
    else:
        dem_to_sources_comparisons = None
        dem_ma = None
    
    if temporal_data is not None:
        tcs_to_tempbaselines_comparisons = signals_to_master_signal_comparison(temporal_data['tcs'].T, 
                                                                               np.asarray(temporal_data['temporal_baselines'])[np.newaxis,:], density = True)               # And then we can do kernel density plots for each IC and the DEM
    else:
        tcs_to_tempbaselines_comparisons = None
                                                 
    plot_source_tc_correlations(sources, sources_mask, dem_ma, dem_to_sources_comparisons, tcs_to_tempbaselines_comparisons, fig_title = fig_title, **fig_kwargs)       # do the atual plotting
    print("Done.  ")
    return dem_to_sources_comparisons, tcs_to_tempbaselines_comparisons

#%%



def plot_source_tc_correlations(sources, mask, dem = None, dem_to_ic_comparisons = None, tcs_to_tempbaselines_comparisons = None,
                                png_path = './', figures = "window", fig_title = None):
    """Given information about the ICs, their correlations with the DEM, and their time courses correlations with an intererograms temporal basleine, 
    create a plot of this information.  
    Inputs:
        sources | rank 2 array | sources as row vectors.  
        mask | rank 2 boolean | to convert a source from a row vector to a rank 2 masked array.  
        dem | rank 2 array | The DEM.  Can also be a masked array.  
        dem_to_ic_comparisons | dict | keys:
                                        xyzs | list of rank 2 arrays | entry in the list for each signal, xyz are rows.  
                                        line_xys | list of rank 2 arrays | entry in the list for each signal, xy are points to plot for the lines of best fit
                                        cor_coefs | list | correlation coefficients between each signal and the master signal.  
        tcs_to_tempbaselines_comparisons| dict | keys as above.  
        png_path | string | if a png is to be saved, a path to a folder can be supplied, or left as default to write to current directory.  
        figures | string,  "window" / "png" / "png+window" | controls if figures are produced (either as a window, saved as a png, or both)
    Returns:
        figure
    History:
        2021_04_22 | MEG | Written.  
        2021_04_23 | MEG | Update so that axes are removed if they are not being used.  
        
    """
    import numpy as np
    import matplotlib.pyplot as plt
    from icasar.aux1 import col_to_ma
    from icasar.aux2 import remappedColorMap, truncate_colormap

    n_sources = sources.shape[0]

    # colour map stuff
    ifg_colours = plt.get_cmap('coolwarm')
    cmap_mid = 1 - np.max(sources)/(np.max(sources) + abs(np.min(sources)))                                    # get the ratio of the data that 0 lies at (eg if data is -15 to 5, ratio is 0.75)
    if cmap_mid < (1/257):                                                                                                 # this is a fudge so that if plot starts at 0 doesn't include the negative colorus for the smallest values
        ifg_colours_cent = remappedColorMap(ifg_colours, start=0.5, midpoint=0.5, stop=1.0, name='shiftedcmap')
    else:
        ifg_colours_cent = remappedColorMap(ifg_colours, start=0.0, midpoint=cmap_mid, stop=1.0, name='shiftedcmap')


    f, axes = plt.subplots(3, (n_sources+1), figsize = (15,7))
    plt.subplots_adjust(wspace = 0.1)
    f.canvas.manager.set_window_title(f"{fig_title}")
    
    # 1: Plot the DEM:
    if dem is not None:
        terrain_cmap = plt.get_cmap('terrain')
        terrain_cmap = truncate_colormap(terrain_cmap, 0.2, 1)    
        dem_plot = axes[1,0].matshow(dem, cmap = terrain_cmap)
        axin = axes[1,0].inset_axes([0, -0.06, 1, 0.05])
        cbar_1 = f.colorbar(dem_plot, cax=axin, orientation='horizontal')
        cbar_1.set_label('Height (m)', fontsize = 8)
        axes[1,0].set_title('DEM')
        axes[1,0].set_xticks([])
        axes[1,0].set_yticks([])
    else:
        axes[1,0].set_axis_off()
        
    # 2: Find the x and y limits for the 2d scatter plots
    if dem_to_ic_comparisons is not None:                                                               # first check that it actually exists.  
        row1_all_xyzs = np.stack(dem_to_ic_comparisons['xyzs'], axis = 2)                               # merge together into a rank 3 numpy array. (3 x n_pixels x n_ics?)
        row1_xlim = (np.min(row1_all_xyzs[0,]), np.max(row1_all_xyzs[0,]))                              # x limits are min and max of the first row
        row1_ylim = (np.min(row1_all_xyzs[1,]), np.max(row1_all_xyzs[1,]))                              # y limits are min and max of the second row
    
    if tcs_to_tempbaselines_comparisons is not None:                                                    # as above.          
        row2_all_xyzs = np.stack(tcs_to_tempbaselines_comparisons['xyzs'], axis = 2)
        row2_xlim = (np.min(row2_all_xyzs[0,]), np.max(row2_all_xyzs[0,]))        
        row2_ylim = (np.min(row2_all_xyzs[1,]), np.max(row2_all_xyzs[1,]))        
    
    # 3: Loop through each IC
    for ic_n in range(n_sources):
        # 2a: Plotting the IC
        im = axes[0,ic_n+1].matshow(col_to_ma(sources[ic_n,:], mask), cmap = ifg_colours_cent, vmin = np.min(sources), vmax = np.max(sources))
        axes[0,ic_n+1].set_xticks([])
        axes[0,ic_n+1].set_yticks([])
        axes[0,ic_n+1].set_title(f"Source {ic_n}")
        
        # 2B: Plotting the IC to DEM scatter, if the data are available
        if dem_to_ic_comparisons is not None:
            axes[1,ic_n+1].scatter(dem_to_ic_comparisons['xyzs'][ic_n][0,:],
                                   dem_to_ic_comparisons['xyzs'][ic_n][1,:], c= dem_to_ic_comparisons['xyzs'][ic_n][2,:])
            axes[1,ic_n+1].plot(dem_to_ic_comparisons['line_xys'][ic_n][0,:], dem_to_ic_comparisons['line_xys'][ic_n][1,:], c = 'r')
            axes[1,ic_n+1].set_xlim(row1_xlim[0], row1_xlim[1])
            axes[1,ic_n+1].set_ylim(row1_ylim[0], row1_ylim[1])
            axes[1,ic_n+1].axhline(0, c='k')
            axes[1,ic_n+1].yaxis.tick_right()                                       # set ticks to be on the right. 
            if ic_n != (n_sources-1):
                axes[1,ic_n+1].yaxis.set_ticklabels([])                             # if it's not the last one, turn the  tick labels off
            else:
                axes[1,ic_n+1].yaxis.set_ticks_position('right')                    # but if it is, make sure they're on the right.  
                axes[1,ic_n+1].set_ylabel(f"IC")
                axes[1,ic_n+1].yaxis.set_label_position('right')
            if ic_n == int(n_sources/2):
                axes[1,ic_n+1].set_xlabel('Height (m)')
            axes[1,ic_n+1].set_title(f"CorCoef: {np.round(dem_to_ic_comparisons['cor_coefs'][ic_n],2)}", fontsize = 7, color = 'r')    
        else:
            axes[1,ic_n+1].set_axis_off()
                
                

        if tcs_to_tempbaselines_comparisons is not None:
            axes[2,ic_n+1].scatter(tcs_to_tempbaselines_comparisons['xyzs'][ic_n][0,:],
                                   tcs_to_tempbaselines_comparisons['xyzs'][ic_n][1,:], c= tcs_to_tempbaselines_comparisons['xyzs'][ic_n][2,:])
            axes[2,ic_n+1].plot(tcs_to_tempbaselines_comparisons['line_xys'][ic_n][0,:], tcs_to_tempbaselines_comparisons['line_xys'][ic_n][1,:], c = 'r')
            axes[2,ic_n+1].set_xlim(row2_xlim[0], row2_xlim[1])
            axes[2,ic_n+1].set_ylim(row2_ylim[0], row2_ylim[1])                                                    # force them to all share a y axis.  Gnerally not good as such varying scales.  
            axes[2,ic_n+1].axhline(0, c='k')
            axes[2,ic_n+1].yaxis.tick_right()

            if ic_n != (n_sources-1):
                axes[2,ic_n+1].yaxis.set_ticklabels([])                                                            # if it's not the last one, turn the  tick labels off
            else:
                axes[2,ic_n+1].yaxis.set_ticks_position('right')                                                   # but if it is, make sure they're on the right.  
                axes[2,ic_n+1].set_ylabel(f"IC usage strength")
                axes[2,ic_n+1].yaxis.set_label_position('right')
            
            if ic_n == int(n_sources/2):                                                                            # on roughly the middle plot....
                axes[2,ic_n+1].set_xlabel('Temporal Baseline (days)')                                               # add an x label.  
                                
            axes[2,ic_n+1].set_title(f"CorCoef: {np.round(tcs_to_tempbaselines_comparisons['cor_coefs'][ic_n],2)}", fontsize = 7, color = 'r')    
        else:
            axes[2,ic_n+1].set_axis_off()


    # 3: The ICs colorbar
    axin = axes[0,0].inset_axes([0.5, 0, 0.1, 1])            
    cbar_2 = f.colorbar(im, cax=axin, orientation='vertical')
    cbar_2.set_label('IC')
    axin.yaxis.set_ticks_position('left')

    # last tidying up
    for ax in [axes[0,0], axes[2,0]]:
        ax.set_axis_off()

    f.tight_layout()    
    
    if figures == 'window':                                                                 # possibly save the output
        pass
    elif figures == "png":
        f.savefig(f"{png_path}/{fig_title}.png")
        plt.close()
    elif figures == 'png+window':
        f.savefig(f"{png_path}/{fig_title}.png")
    else:
        pass  


#%%



def visualise_ICASAR_inversion(interferograms, sources, time_courses, mask, n_data = 10,png_path = './',figures = "window", fig_title = None):
    """Given interferograms (that don't need to be mean centered), visualise how the 
    BSS recontruction (A@S) can be used to reconstruct them.  
    Inputs:
        Interferograms | rank 2 array | interferograms as row vectors
        sources | rank 2 array | souces as row vectors(e.g. 5 x 54000)
        time_courses | rank 2 array | time courses as column vectors (e.g. 85 x 5)
        mask | rank 2 array | to convert a row vector to a rank 2 array (image) for plotting.  
        n_data | int | number of data to plot. 
    Returns:
        figure
    History:
        2021_03_03 | MEG | Written.  
        2021_11_25 | MEG | Write the docs
    """
    import numpy as np
    
    def plot_ifg(ifg, ax, mask, vmin, vmax):
        """
        """
        w = ax.matshow(col_to_ma(ifg, mask), interpolation ='none', aspect = 'equal', vmin = vmin, vmax = vmax,cmap='jet')                                                   # 
        axin = ax.inset_axes([0, -0.06, 1, 0.05])
        fig.colorbar(w, cax=axin, orientation='horizontal')
        ax.set_yticks([])
        ax.set_xticks([])
    
    import matplotlib.pyplot as plt
    
    interferograms_mc = interferograms - np.mean(interferograms, axis = 1)[:, np.newaxis]
    interferograms_ICASAR = time_courses @ sources
    residual = interferograms_mc - interferograms_ICASAR
    
    if n_data > interferograms.shape[0]:
        n_data = interferograms.shape[0]

    
    fig, axes = plt.subplots(3, n_data, figsize = (15,7))  
    if n_data == 1:    
        axes = np.atleast_2d(axes).T                                                # make 2d, and a column (not a row)
    
    row_labels = ['Data', 'Model', 'Resid.' ]
    for ax, label in zip(axes[:,0], row_labels):
        ax.set_ylabel(label)

    for data_n in range(n_data):
        vmin = np.min(np.stack((interferograms_mc[data_n,], interferograms_ICASAR[data_n,], residual[data_n])))
        vmax = np.max(np.stack((interferograms_mc[data_n,], interferograms_ICASAR[data_n,], residual[data_n])))
        plot_ifg(interferograms_mc[data_n,], axes[0,data_n], mask, vmin, vmax)
        plot_ifg(interferograms_ICASAR[data_n,], axes[1,data_n], mask, vmin, vmax)
        plot_ifg(residual[data_n,], axes[2,data_n], mask, vmin, vmax)
    
    fig.tight_layout()
    if figures=='window':
        pass
    elif figures=='png':
        fig.savefig(f"{png_path}/{fig_title}.png")
        plt.close()
    elif figures=='png+window':
        fig.savefig(f"{png_path}/{fig_title}.png")
    else:
        pass
    plt.close()




#%%

def signals_to_master_signal_comparison(signals, master_signal, density = False):
        """ Given an array of signals (as row vectors), compare it to a single signal and plot a kernel
        density estimate, and calculate a line of best fit through the points with R**2 value.  
        Inputs:
            signals | rank 2 | signals as rows.  Even if there's only 1 signal, it still needs to be rank 2
            master_signal | rank 2 | signal as a row, but has to be rank 2
            density | boolean | If True, gaussian kernel density estimate for the points.  Can be slow.  
            
        Returns:
            signal_to_msignal_comparison | dict | keys:
                                                    xyzs | list of rank 2 arrays | entry in the list for each signal, xyz are rows.  
                                                    line_xys | list of rank 2 arrays | entry in the list for each signal, xy are points to plot for the lines of best fit
                                                    cor_coefs | list | correlation coefficients between each signal and the master signal.  
            
        History:
            2021_04_22 | MEG | Written.  
            2021_04_26 | MEG | Add check that the signals are of the same length.  
        """
        import numpy as np
        from scipy.stats import gaussian_kde
        import numpy.polynomial.polynomial as poly                                             # used for lines of best fit through dem/source plots
        
        n_signals, n_pixels = signals.shape                                                    # each signal is a row, observations of that are columns.  
        if n_pixels != master_signal.shape[1]:
            raise Exception(f"The signals aren't of the same length (2nd dimension), as 'signals' is {n_pixels} long, but 'master_signal' is {master_signal.shape[1]} long.  Exiting.  ")
        xyzs = []                                                                              # initiate
        line_xys = []
        cor_coefs = []
        print(f"    Starting to calculate the 2D kernel density estimates for the signals.  Completed ", end = '')
        for signal_n, signal in enumerate(signals):                                            # signal is a row of signals, and loop through them.  
            
            # 1: Do the kernel density estimate
            xy = np.vstack((master_signal, signal[np.newaxis,:]))                              # master signal will be on X and be the top row.  
            x = xy[:1,:]                                    
            y = xy[1:2,:]
            if density:
                z = gaussian_kde(xy)(xy)
                idx = z.argsort()                                                               # need to be sorted so that when plotted, those with the highest z value go on top.                                  
                x, y, z = x[0,idx], y[0,idx], z[idx]  
                xyzs.append(np.vstack((x,y,z)))                                                 # 3 rows, for each of x,y and z
            else:
                xyzs.append(np.vstack((x,y,np.zeros(n_pixels))))                                # if we're not doing the kernel density estimate, z value is just zeros.  
                    
            # 2: calculate the lines of best fit
            line_coefs = poly.polyfit(x, y, 1)                                                  # polynomial of order 1 (i.e. a line of best fit)
            line_yvals = (poly.polyval(x, line_coefs))                                          # calculate the lines yvalues for all x points
            line_xys.append(np.vstack((x, line_yvals)))                                         # x vals are first row, y vals are 2nd row
            
            # 3: And the correlation coefficient
            # import pdb; pdb.set_trace()
            cor_coefs.append(np.corrcoef(x, y)[1,0])                                            # which is a 2x2 matrix, but we just want the off diagonal (as thats the correlation coefficient between the signals)
            
            print(f"{signal_n} ", end = '')
        print('\n')
        
        signal_to_msignal_comparison = {'xyzs' : xyzs,
                                        'line_xys' : line_xys,
                                        'cor_coefs' : cor_coefs}
        
        return signal_to_msignal_comparison



#%%

def create_all_ifgs(ifgs_r2, ifg_dates, max_n_all_ifgs = 1000):
    """Given a rank 2 of incremental ifgs, calculate all the possible ifgs that still step forward in time (i.e. if deformation is positive in all incremental ifgs, 
    it remains positive in all the returned ifgs.)  If acquisition dates are provided, the tmeporal baselines of all the possible ifgs can also be found.  
    Inputs:
        ifgs_r2 | rank 2 array | Interferograms as row vectors.  
        ifg_dates | list of strings | dates in the form YYYYMMDD_YYYYMMDD.  As the interferograms are incremental, this should be the same length as the number of ifgs
    Returns:
        ifgs_r2 | rank 2 array | Only the ones that are non-zero (the diagonal in ifgs_r3) and in the lower left corner (so deformation isn't reversed.  )
    History:
        2021_04_13 | MEG | Written
        2021_04_19 | MEG | add funcionality to calculate the temporal baselines of all possible ifgs.  
        2021_04_29 | MEG | Add functionality to handle networks with breaks in them.  
    """
    import numpy as np
    import datetime as dt
    from datetime import datetime, timedelta
    import random
    from icasar.aux2 import acquisitions_from_ifg_dates
    
    def split_network_to_lists(ifgs_r2, ifg_dates):
        """Given a r2 of ifgs (ie row vectors) and a list of their dates (YYYYMMDD_YYYYMMDD), break these into lists that are 
        continuous (i.e. no gaps)
        """
    
        ifg_dates_continuous = []                                                                   # list of the list the dates for a continuous network
        ifgs_r2_continuous = []                                                                     # and the incremental interferograms in that network.  
        start_continuous_run = 0
        for ifg_n in range(n_ifgs-1):                                                               # iterate                                 
            if (ifg_dates[ifg_n][9:] != ifg_dates[ifg_n+1][:8]):                                   # if the dates don't agree (ie. the slave of one isn't the master of the other), we've got to the end of a network
                ifg_dates_continuous.append(ifg_dates[start_continuous_run:ifg_n+1])                # +1 as want to include the last date in the selection
                ifgs_r2_continuous.append(ifgs_r2[start_continuous_run:ifg_n+1,])
                start_continuous_run = ifg_n+1                                                      # +1 so that when we index the next time, it doesn't include ifg_n
            if ifg_n == n_ifgs -2:                                                                  #  if we've got to the end of the list.              
                ifg_dates_continuous.append(ifg_dates[start_continuous_run:])                       # select to the end.  
                ifgs_r2_continuous.append(ifgs_r2[start_continuous_run:,])
                
        return ifg_dates_continuous, ifgs_r2_continuous
    
    def create_all_possible_ifgs(networks):
        """
        """
        n_networks = len(networks)
        ifgs_all_r2 = []
        dates_all_r1 = []
        for n_network, network in enumerate(networks):                                                         # loop through each network.  
            ifgs_r2_temp = network['ifgs_r2']
            ifg_dates_temp = network['ifg_dates']
            n_acq = ifgs_r2_temp.shape[0] + 1
            
            # 2a: convert from daisy chain of incremental to a relative to a single master at the start of the time series.  
            acq1_def = np.zeros((1, n_pixs))                                                     # deformation is 0 at the first acquisition
            ifgs_cs = np.cumsum(ifgs_r2_temp, axis = 0)                                          # convert from incremental to cumulative.  
            ifgs_cs = np.vstack((acq1_def, ifgs_cs))                                             # add the 0 at first time ifg to the other cumulative ones. 
            
            # 2b: create all possible ifgs
            ifgs_cube = np.zeros((n_acq, n_acq, n_pixs))                                    # cube to store all possible ifgs in
            for i in range(n_acq):                                                          # used to loop through each column
                ifgs_cube[:,i,] = ifgs_cs - ifgs_cs[i,]                                     # make one column (ie all the rows) by taking all the ifgs and subtracting one time from it
               
            # 2c: Get only the positive ones (ie the lower left quadrant)    
            lower_left_indexes = triange_lower_left_indexes(n_acq)                              # get the indexes of the ifgs in the lower left corner (ie. non 0, and with unreveresed deformation.  )
            ifgs_all_r2.append(ifgs_cube[lower_left_indexes[:,0], lower_left_indexes[:,1], :])        # get those ifgs and store as row vectors.  
            
            # 2d: Calculate the dates that the new ifgs run between.  
            acq_dates = acquisitions_from_ifg_dates(ifg_dates_temp)                                                         # get the acquisitions from the ifg dates.  
            ifg_dates_all_r2 = np.empty([n_acq, n_acq], dtype='U17')                                                        # initate an array that can hold unicode strings.  
            for row_n, date1 in enumerate(acq_dates):                                                                       # loop through rows
                for col_n, date2 in enumerate(acq_dates):                                                                   # loop through columns
                    ifg_dates_all_r2[row_n, col_n] = f"{date2}_{date1}"
            ifg_dates_all_r1 = list(ifg_dates_all_r2[lower_left_indexes[:,0], lower_left_indexes[:,1]])             # just get the lower left corner (like for the ifgs)
    
            dates_all_r1.append(ifg_dates_all_r1)
    
        # 3: convert lists back to a single matrix of all interferograms.  
        ifgs_all_r2 = np.vstack(ifgs_all_r2)                                                                            # now one big array of n_ifgs x n_pixels
        dates_all_r1 = [item for sublist in dates_all_r1 for item in sublist]                                           # dates_all_r1 is a list (one for each connected network) of lists (each ifg date).  The turns them to a singe list.  
        
        return ifgs_all_r2, dates_all_r1
    
    
    def triange_lower_left_indexes(side_length):
        """ For a square matrix of size side_length, get the index of all the values that are in the lower
        left quadrant (i.e. all to the lower left of the diagonals).  
        Inputs:
            side_length | int | side length of the square.  e.g. 5 for a 5x5
        Returns:
            lower_left_indexes | rank 2 array | indexes of all elements below the diagonal.  
        History:
            2021_04_13 | MEG | Written.  
        """
        import numpy as np
        zeros_array = np.ones((side_length, side_length))                                                               # initate as ones so none will be selected.  
        zeros_array = np.triu(zeros_array)                                                                              # set the lower left to 0s
        lower_left_indexes = np.argwhere(zeros_array == 0)                                                              # select only the lower lefts
        return lower_left_indexes

    
    ########### begin main function
    n_ifgs, n_pixs = ifgs_r2.shape
        
    
    
    # 1: Determine if the network is continuous, and if not split it into lists
    ifg_dates_continuous, ifgs_r2_continuous = split_network_to_lists(ifgs_r2, ifg_dates)                               # If there is a break (gap) in the network, this splits the ifgs_dates and ifgs based on this.  
    n_networks = len(ifg_dates_continuous)                                                      # get the number of connected networks.  
    
    # 2: build a better set of information for each network.  
    n_ifgs_all_total = 0                                                                                            # the total number of ifgs that can be made in the network
    networks = []                                                                           # each item is a dict, containing ifg_dates, length_dats, n_ifgs, and n_ifgs_all (the number of unique interferograms that can be made)
    for n_network in range(n_networks):  
        network_dict = {'ifgs_r2'       : ifgs_r2_continuous[n_network],
                        'ifg_dates'     : ifg_dates_continuous[n_network]}
        
        network_start_date = dt.datetime.strptime(ifg_dates_continuous[n_network][0][:8], '%Y%m%d')
        network_end_date = dt.datetime.strptime(ifg_dates_continuous[n_network][-1][9:], '%Y%m%d')
        network_dict['length_days'] = (network_end_date - network_start_date).days
        network_dict['n_ifgs'] = network_dict['ifgs_r2'].shape[0]
        network_dict['n_ifgs_all'] = int(((network_dict['n_ifgs']+1)**2 - (network_dict['n_ifgs']+1)) / 2)                  # +1 as there is 1 more acquisition than incremental interferogram.  
        networks.append(network_dict)
        n_ifgs_all_total += network_dict['n_ifgs_all']                                                          # add to the running total of the total number of ifgs
           
    #3: determine if we can make all ifgs, or if we need to make only some of them.  
    if n_ifgs_all_total < max_n_all_ifgs:                                                               # if we can just make all ifgs, 
        ifgs_all_r2, dates_all_r1 = create_all_possible_ifgs(networks)
        
    else:    
        ifgs_all_r2 = []                                                                                                # list with entry for each entwork
        dates_all_r1 = []                                                                                               # list for all networks
        for network in networks:
            n_ifgs_from_network = int(max_n_all_ifgs * (network['n_ifgs_all'] / n_ifgs_all_total))                    # get the fraction of ifgs that each network will provide ot the total.  e.g. network 1 = 800, network 2 = 800, but 1000 in total, 500 from each network

            # 0: get some info about the ifgs
            n_pixs = network['ifgs_r2'].shape[1]
            n_acq = network['n_ifgs'] + 1

            # 1: Make the cumulative ifgs
            acq1_def = np.zeros((1, n_pixs))                                                     # deformation is 0 at the first acquisition
            ifgs_cs = np.cumsum(network['ifgs_r2'], axis = 0)                                          # convert from incremental to cumulative.  
            ifgs_cs = np.vstack((acq1_def, ifgs_cs))                                             # add the 0 at first time ifg to the other cumulative ones.     
                   
            # 2: get the acquisition dates:
            acq_dates = acquisitions_from_ifg_dates(network['ifg_dates'])                                                         # get the acquisitions from the ifg dates.  

            # 3: create the list of acquisiton dates that is the correct (for this network) length
            ifg_acq_start_acq_ends = []                                                                                  # list of tuples of acquisitions each ifg will be between
            while len(ifg_acq_start_acq_ends) < n_ifgs_from_network:                                                     # until we have enough...
                acq_start = np.random.randint(0, n_acq)                                                                 # random start acq
                acq_end = np.random.randint(0, n_acq)                                                                   # random end acq
                if (acq_start < acq_end) and ((acq_start, acq_end) not in ifg_acq_start_acq_ends):                       # if start is before end (ie only in lower left of all acquisitions square) and not already in list of pairs
                    ifg_acq_start_acq_ends.append((acq_start, acq_end))                                                  # add to pair
            
            # 4: make the ifgs for those acquisition dates.  
            for ifg_acq_start_acq_end in ifg_acq_start_acq_ends:                                                        # iterate through all the pairs we need to get 
                ifgs_all_r2.append(ifgs_cs[ifg_acq_start_acq_end[1],] - ifgs_cs[ifg_acq_start_acq_end[0],])               # subtract one ifg from the other (end - start)
                dates_all_r1.append(f"{acq_dates[ifg_acq_start_acq_end[0]]}_{acq_dates[ifg_acq_start_acq_end[1]]}")         # get teh dates that that ifg spans
                
        # 5: convert lists back to a single matrix of all interferograms.  
        ifgs_all_r2 = np.vstack(ifgs_all_r2)                                                                            # now one big array of n_ifgs x n_pixels
                    
    print(f"When creating all interferograms, {ifgs_r2.shape[0]} were passed to the function, and these were found to make {n_network+1} connected networks.  "
          f"From these, {ifgs_all_r2.shape[0]} interferograms were created.  ")
    
    return ifgs_all_r2, dates_all_r1    
    


#%%

def create_cumulative_ifgs(ifgs_dc, ifg_dates_dc):
    """ Given a time series of incremental (daisy chain) interferograms, calculate the cumulative interferograms  relative to the first acquisition.  
    Inputs:
        ifgs_dc | rank 2 array | ifgs as row vectors.  
        ifg_dates_dc | list | list of YYYYMMDD_YYYYMMDD 
    Returns:
        ifgs_cum | rank 2 array | ifgs as row vectors, cumulative and relative to the first acquisition.  
        ifg_dates_cum | list | list of YYYYMMDD_YYYYMMDD 
    History:
        2021_11_29 | MEG | Written.  
        2021_11_30 | MEG | Update so that doesn't create the acquisition 0 - acquisition 0 interferogram of 0 displacement.  

    """
    import numpy as np
    from icasar.aux2 import baseline_from_names
    
    # 0: First make the ifgs, v1 that uses that has acquisition 0 to acquisition 0 as a row of 0 displacements at the start
    # ifgs_cum_0 = np.zeros((1, ifgs_dc.shape[1]))                            # 0 displacement on first acquistion
    # ifgs_cum = np.cumsum(ifgs_dc, axis = 0)                                 # displacement to last date of each daisy chain interferogram.  
    # ifgs_cum = np.vstack((ifgs_cum_0, ifgs_cum))                            # combine so first acuqisiton has 0 displacmenent.  
    # 0b: or ignores a0 to a0:
    ifgs_cum = np.cumsum(ifgs_dc, axis = 0)                                 # displacement to last date of each daisy chain interferogram.  

    
    # 1: then make the ifg dates.  
    acq_0 = ifg_dates_dc[0][:8]
    #ifg_dates_cum = [f"{acq_0}_{acq_0}"]
    ifg_dates_cum = []
    for ifg_date_dc in ifg_dates_dc:
        ifg_dates_cum.append(f"{acq_0}_{ifg_date_dc[9:]}")
    
    return ifgs_cum, ifg_dates_cum
        

    

#%%    

def plot_temporal_signals(signals, title = None, signal_names = None,
                          figures = "window",  png_path = './'):
    """Plot a set of time signals stored in a matrix as rows.  
    Inputs:
        signals | rank 2 array | signals as row vectors.  e.g. 1x100
        title | string | figure title.  
        signals_names | list of strings | names of each signal
        figures | string,  "window" / "png" / "png+window" | controls if figures are produced (either as a window, saved as a png, or both)
        png_path | string | if a png is to be saved, a path to a folder can be supplied, or left as default to write to current directory.  
    Returns:
        Figure, either as a window or saved as a png
    History:
        2020/09/09 | MEG | Written
    
    """
    import matplotlib.pyplot as plt
    import numpy as np
    
    n_signals = signals.shape[0]
    fig1, axes = plt.subplots(n_signals,1, figsize = (10,6))
    if title is not None:
        fig1.canvas.manager.set_window_title(title)
        fig1.suptitle(title)
    for signal_n, signal in enumerate(signals):
        axes[signal_n].plot(np.arange(0, signals.shape[1]), signal)
        if signal_names is not None:
            axes[signal_n].set_ylabel(signal_names[signal_n])
        axes[signal_n].grid(alpha = 0.5)
        if signal_n != (n_signals-1):
            axes[signal_n].set_xticklabels([])
            
    if figures == 'window':                                                                 # possibly save the output
        pass
    elif figures == "png":
        fig1.savefig(f"{png_path}/{title}.png")
        plt.close()
    elif figures == 'png+window':
        fig1.savefig(f"{png_path}/{title}.png")
    else:
        pass
                          # connect the figure and the function.  


#%%


def plot_pca_variance_line(pc_vals, title = '', figures = 'window', png_path = './'):
    """
    A function to display the cumulative variance in each dimension of some high D data
    Inputs:
        pc_vals | rank 1 array | variance in each dimension.  Most important dimension first.  
        title | string | figure title
        figures | string,  "window" / "png" / "png+window" | controls if figures are produced (either as a window, saved as a png, or both)
        png_path | string or None | if a png is to be saved, a path to a folder can be supplied, or left as default to write to current directory.  
    Returns:
        figure, either as window or saved as a png
    History:
        2019/XX/XX | MEG | Written
        2020/03/03 | MEG | Add option to save as png
    """
    import numpy as np
    import matplotlib.pyplot as plt
    from matplotlib.ticker import MaxNLocator
    
    
    f, ax = plt.subplots()
    pc_vals_cs = np.concatenate((np.array([0]), np.cumsum(pc_vals)))
    x_vals = np.arange(len(pc_vals_cs)) 
    ax.plot(x_vals, pc_vals_cs/pc_vals_cs[-1])
    ax.scatter(x_vals, pc_vals_cs/pc_vals_cs[-1])
    ax.set_xlabel('Component number')
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    ax.set_ylabel('Cumulative Variance')
    ax.set_ylim([0, 1])
    ax.set_title(title)
    f.canvas.manager.set_window_title(title)
    

    if figures == 'window':
        pass
    elif figures == "png":
        f.savefig(f"{png_path}/01_pca_variance_line.png")
        plt.close()
    elif figures == 'png+window':
        f.savefig(f"{png_path}/01_pca_variance_line.png")
    else:
        pass
        
        
        
        
#%%
        
        
def maps_tcs_rescale(maps, tcs):
    """
    A function to rescale spaital maps to have unit range and rescale each's time cource (tc)
    so that there is no change to the product of the two matrices
    
    input:
        maps | array | spatial maps as rows (e.g. 2x1775)
        tcs  | array | time courses as columns (e.g. 15x2)
    Output:
        maps_scaled | array | spatial maps as rows with each row having unit range
        tcs_scaled | array | TCs scaled so that new maps x new tcs equals maps x tcs
    
    2017/05/15 | written
    
    """
    import numpy as np
    
    def rescale_unit_range(signals):
        """
        rescale a matrix of row vectors so that each row has a range of 1.  
        Also record the scaling factor required to rescale each row vector
        signals are rows
        Input:
            signals: array with each signal as a new row 
        Output:
            signals_rescale | array | each row has a range of 1
            signals_factor | array | factor that each row is dvided by to adjust range
        """
        import numpy as np
        
        signals_rescale = np.ones(signals.shape)                                    # initiate rescaled array
        signals_factor = np.ones((np.size(signals, axis=0) , 1))                    # initiate array to record scaling factor for each row
           
        for i in np.arange(np.size(signals, axis = 0)):
            signals_factor[i,0] = (np.max(signals[i,:])-np.min(signals[i,:]))
            signals_rescale[i,:] = signals[i,:]/signals_factor[i,0]
            
        return signals_rescale, signals_factor

    
    maps_scaled , scaling = rescale_unit_range(maps)
    tcs_scaled = tcs * np.ravel(scaling)
    return maps_scaled, tcs_scaled



#%%
  
    
def bss_components_inversion(sources, interferograms):
    """
    A function to fit an interferogram using components learned by BSS, and return how strongly
    each component is required to reconstruct that interferogramm, and the 
    
    Inputs:
        sources | n_sources x pixels | ie architecture I.  Mean centered
        interferogram | list of (n_ifgs x pixels) | Doesn't have to be mean centered, multiple interferograms to be fit can be fit by making the list as long as required.  
        
    Outputs:
        m | rank 1 array | the strengths with which to use each source to reconstruct the ifg.  
        mean_l2norm | float | the misfit between the ifg and the ifg reconstructed from sources
    """
    import numpy as np
    
    inversion_results = []
    for interferogram in interferograms:
        interferogram -= np.mean(interferogram)                     # mean centre
        n_pixels = np.size(interferogram)
    
    
        d = interferogram.T                                        # now n_pixels x n_ifgs
        g = sources.T                                              # a matrix of ICA sources and each is a column (n_pixels x n_sources)
        
        ### Begin different types of inversions.  
        m = np.linalg.inv(g.T @ g) @ g.T @ d                       # m (n_sources x 1), least squares
        #m = g.T @ np.linalg.inv(g @ g.T) @ d                      # m (n_sources x 1), least squares with minimum norm condition.     COULDN'T GET TO WORK.  
        #m = np.linalg.pinv(g) @ d                                   # Moore-Penrose inverse of G for a simple inversion.  
        # u = 1e0                                                                 # bigger value favours a smoother m, which in turn can lead to a worse fit of the data.  1e3 gives smooth but bad fit, 1e1 is a compromise, 1e0 is rough but good fit.  
        # m = np.linalg.inv(g.T @ g + u*np.eye(g.shape[1])) @ g.T @ d;                # Tikhonov solution  
        
        
        ### end different types of inversion
        d_hat = g@m
        d_resid = d - d_hat
        mean_l2norm = np.sqrt(np.sum(d_resid**2))/n_pixels          # misfit between ifg and ifg reconstructed from sources
        
        inversion_results.append({'tcs'      : m,
                                  'model'    : d_hat,
                                  'residual' : d_resid,
                                  'l2_norm'  : mean_l2norm})
    
    return inversion_results


#%%
    

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


#%% taken from insar_tools.py

def r2_to_r3(ifgs_r2, mask):
    """ Given a rank2 of ifgs as row vectors, convert it to a rank3. 
    Inputs:
        ifgs_r2 | rank 2 array | ifgs as row vectors 
        mask | rank 2 array | to convert a row vector ifg into a rank 2 masked array        
    returns:
        phUnw | rank 3 array | n_ifgs x height x width
    History:
        2020/06/10 | MEG  | Written
    """
    import numpy as np
    import numpy.ma as ma
    
    n_ifgs = ifgs_r2.shape[0]
    ny, nx = col_to_ma(ifgs_r2[0,], mask).shape                                   # determine the size of an ifg when it is converter from being a row vector
    
    ifgs_r3 = np.zeros((n_ifgs, ny, nx))                                                # initate to store new ifgs
    for ifg_n, ifg_row in enumerate(ifgs_r2):                                           # loop through all ifgs
        ifgs_r3[ifg_n,] = col_to_ma(ifg_row, mask)                                  
    
    mask_r3 = np.repeat(mask[np.newaxis,], n_ifgs, axis = 0)                            # expand the mask from r2 to r3
    ifgs_r3_ma = ma.array(ifgs_r3, mask = mask_r3)                                      # and make a masked array    
    return ifgs_r3_ma


#%% Copied from small_plot_functions.py


def r2_arrays_to_googleEarth(images_r3_ma, lons, lats, layer_name_prefix = 'layer', kmz_filename = 'ICs',
                             out_folder = './'):
    """ Given one or several arrays in a rank3 array, create a multilayer Google Earth file (.kmz) of them.  
    Inputs:
        images_r3_ma | rank3 masked array |x n_images x ny x nx
        lons | rank 2 array | lons of each pixel in the image.  
        lats | rank 2 array | lats of each pixel in theimage. 
        layer_name_prefix | string | Can be used to set the name of the layes in the kmz (nb of the form layer_name_prefix_001 etc. )
        kmz_filename | string | Sets the name of the kmz produced
        out_folder | pathlib Path | path to location to save .kmz.  
    Returns:
        kmz file
    History:
        2020/06/10 | MEG | Written
        2021/03/11 | MEG | Update to handle incorrectly sized lons and lats arrays (e.g. rank2 arrays instead of rank 1)
    """
    import numpy as np
    import os
    import shutil
    import simplekml
    from pathlib import Path


    n_images = images_r3_ma.shape[0]    
    if type(out_folder) == str:                                                                                     # this should really be a path, but it could easily be a string.  
        out_folder = Path(out_folder)                                                                               # if it is a string, conver it.  
    # 0 temporary folder for intermediate pngs
    try:
        os.mkdir('./temp_kml')                                                                       # make a temporay folder to save pngs
    except:
        print("Can't create a folder for temporary kmls.  Trying to delete 'temp_kml' incase it exisits already... ", end = "")
        try:
            shutil.rmtree('./temp_kml')                                                              # try to remove folder
            os.mkdir('./temp_kml')                                                                       # make a temporay folder to save pngs
            print("Done. ")
        except:
          raise Exception("Problem making a temporary directory to store intermediate pngs" )

    # 1: Initiate the kml
    kml = simplekml.Kml()
        
    # 2 Begin to loop through each iamge
    for n_image in np.arange(n_images)[::-1]:                                           # Reverse so that first IC is processed last and appears as visible
        layer_name = f"{layer_name_prefix}_{str(n_image).zfill(3)}"                     # get the name of a layer a sttring
        r2_array_to_png(images_r3_ma[n_image,], layer_name, './temp_kml/')              # save as an intermediate .png
        
        ground = kml.newgroundoverlay(name= layer_name)                                 # add the overlay to the kml file
        ground.icon.href = f"./temp_kml/{layer_name}.png"                               # and the actual image part
    
        ground.gxlatlonquad.coords = [(lons[-1,0], lats[-1,0]), (lons[-1,-1],lats[-1,-1]),           # lon, lat of image south west, south east
                                      (lons[0,-1], lats[0,-1]), (lons[0,0],lats[0,0])]         # north east, north west  - order is anticlockwise around the square, startign in the lower left
       
    #3: Tidy up at the end
    kml.savekmz(out_folder / f"{kmz_filename}.kmz", format=False)                                    # Saving as KMZ
    shutil.rmtree('./temp_kml')    


#%% Copied from small_plot_functions.py

def r2_array_to_png(r2, filename, png_folder = './'):    
    """ Given a rank 2 array/image, save it as a png with no borders.  
    If a masked array is used, transparency for masked areas is conserved.  
    Designed for use with Google Earth overlays.  
    
    Inputs:
        r2 | rank 2 array | image / array to be saved
        filename | string | name of .png
        png_folder | string | folder to save in, end with /  e.g. ./kml_outputs/
    Returns:
        png of figure
    History:
        2020/06/10 | MEG | Written
        2021_05_05 | MEG | Change colours to coolwarm.  
        
    """
    import matplotlib.pyplot as plt
    
    f, ax = plt.subplots(1,1)
    ax.matshow(r2, cmap = plt.get_cmap('coolwarm'))
    plt.gca().set_axis_off()
    plt.subplots_adjust(top = 1, bottom = 0, right = 1, left = 0, hspace = 0, wspace = 0)
    plt.margins(0,0)
    plt.gca().xaxis.set_major_locator(plt.NullLocator())
    plt.gca().yaxis.set_major_locator(plt.NullLocator())
    plt.savefig(f"{png_folder}{filename}.png", bbox_inches = 'tight',pad_inches = 0, transparent = True)
    plt.close()


#%%

def prepare_point_colours_for_2d(labels, cluster_order):
    """Given the label for each point (ie 1, 2 or 3 say, or -1 if noise) and the order of importance to the clusters 
    (ie cluster 3 is the most compact and isolated so has the highest Iq value, then cluster 1, then cluster 2), return 
    a list of colours for each point so they can be plotted using a standard  .scatter funtcion.  Ie all the points labelled
    3 have the same colour.  
    
    Inputs:
        label | rank 1 array | the label showing which cluster each point is in.  e.g. (1000)
        cluster_order | rank 1 array | to determine which cluster should be blue (the best one is always in blue, the 2nd best in orange etc.  )
    Returns:
        labels_chosen_colours | np array | colour for each point.  Same length as label.  
    History:
        2020/09/10 | MEG | Written
        2020/09/11 | MEG | Update so returns a numpy array and not a list (easier to index later on.  )
    """
    import numpy as np
    n_clusters = len(cluster_order)
    
    colours = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
               '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf']           # the standard nice Matplotlib colours
    if n_clusters > 10:                                                         # if we have more than 10 clsuters, generate some random colours
        for i in range(n_clusters - 10):                                        # how many more colours we need (as we already have 10)
            colours.append(('#%02X%02X%02X' % (np.random.randint(0,25), 
                                               np.random.randint(0,25),
                                               np.random.randint(0,25))))       # generate colours randomly (ie a point between 0 and 255 in 3 dimensions.  )
    else:
        colours = colours[:n_clusters]                                          # crop to length if we have 10 or less colours
        
    colours2 = []                                                               # new list of colours, 1st item is the colour that label 0 should be (which is not necesarily blue)
    for i in range(n_clusters):                                                 # loop through each cluster
        colours2.append(colours[int(np.argwhere(cluster_order == i))])          # populate the list
    
    labels_chosen_colours = []                                           # initiate a list where instead of label for each source, we have its colour
    for label in(labels):                                           # Loop through each point's label
        if label == (-1):                                           # if noise, 
            labels_chosen_colours.append('#c9c9c9')                     # colour is grey
        else:               
            labels_chosen_colours.append(colours2[label])           # otherwise, the correct colour (nb colours 2 are reordered so the most imporant clusters have the usual blue etc. colours)
    labels_chosen_colours = np.asarray(labels_chosen_colours)       # convert from list to numpy array
    return labels_chosen_colours


#%%

def prepare_legends_for_2d(clusters_by_max_Iq_no_noise, Iq):
        """Given the cluster order and the cluster quality index (Iq), create a lenend ready for plot_2d_interactive_fig.  
        Inputs:
            clusters_by_max_Iq_no_noise | rank1 array | e.g. (3,2,4,1) if cluster 3 has the highest Iq.  
            Iq | list | Iq for each clusters.  1st item in list is Iq for 1st cluster.  
        Returns:
            legend_dict | dict | contains the legend symbols (a list of complicated Matplotlib 2D line things), and the labels as a list of strings.  
        History:
            2020/09/10 | MEG | Written
            
        """
        import numpy as np
        from matplotlib.lines import Line2D                                  # for the manual legend
        n_clusters = len(Iq)
        
        legend_elements = [Line2D([0], [0], marker='o', color='w', markerfacecolor='#1f77b4'), 
                            Line2D([0], [0], marker='o', color='w', markerfacecolor='#ff7f0e'), 
                            Line2D([0], [0], marker='o', color='w', markerfacecolor='#2ca02c'), 
                            Line2D([0], [0], marker='o', color='w', markerfacecolor='#d62728'), 
                            Line2D([0], [0], marker='o', color='w', markerfacecolor='#9467bd'), 
                            Line2D([0], [0], marker='o', color='w', markerfacecolor='#8c564b'), 
                            Line2D([0], [0], marker='o', color='w', markerfacecolor='#e377c2'), 
                            Line2D([0], [0], marker='o', color='w', markerfacecolor='#7f7f7f'), 
                            Line2D([0], [0], marker='o', color='w', markerfacecolor='#bcbd22'), 
                            Line2D([0], [0], marker='o', color='w', markerfacecolor='#17becf')]
        if n_clusters > 10:                                                                  # if we have more than 10 clsuters, repeat the same colours the required number of times
            for i in range(n_clusters-10):
                legend_elements.append(Line2D([0], [0], marker='o', color='w', markerfacecolor='#%02X%02X%02X' % (np.random.randint(0,255),
                                                                                                                  np.random.randint(0,255),
                                                                                                                  np.random.randint(0,255))))
        legend_elements = legend_elements[:n_clusters]                                      # crop to length
    
        legend_labels = []
        for i in clusters_by_max_Iq_no_noise:
                legend_labels.append(f'#: {i}\nIq: {np.round(Iq[i], 2)} ')                                   # make a list of strings to name each cluster
        legend_labels.append('Noise')
        legend_elements.append(Line2D([0], [0], marker='o', color='w', markerfacecolor='#c9c9c9'))              # but if we have 10 clusters (which is the max we plot), Noise must be added as the 11th
        legend_dict = {'elements' : legend_elements,
                       'labels'   : legend_labels}
        return legend_dict

