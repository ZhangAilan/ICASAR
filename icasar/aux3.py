# Author: ZYH 
# Date: 2023/12/26
# Description: Some auxiliary functions for ICASAR
 

def recover_signal_timeseries_plot(sources,time_courses,source_number,mask,file_path,fig_title,phUnw_mean):
    '''
    Plot the interferogram sequence of the recovered sources
    '''
    import matplotlib.pyplot as plt
    import numpy as np
    from icasar.aux1 import col_to_ma

    A=time_courses[:,source_number]
    A = np.reshape(A, (len(A), 1))
    S=sources[source_number:source_number+1]
    ifgs_sources=A@S+phUnw_mean
    #print("\nA:\n",A)
    #print("\nS:\n",S)
    #print("\nifgs_sources:\n",ifgs_sources)

    ifgs_sources_rows=ifgs_sources.shape[0]
    num_cols=15
    num_rows=int(np.ceil(ifgs_sources_rows/num_cols))
    fig1,axes=plt.subplots(num_rows,num_cols,figsize=(20,10))
    for i in range(num_rows*num_cols):
        if i<ifgs_sources_rows:
            row=i//num_cols
            col=i%num_cols
            ax=axes[row,col]
            ax.imshow(col_to_ma(ifgs_sources[i,:],mask))
            ax.set_yticks([])
            ax.set_xticks([])
        else:
            row=i//num_cols
            col=i%num_cols
            ax=axes[row,col]
            ax.axis('off')

    fig1.suptitle(fig_title)
    fig1.savefig(f"{file_path}/{fig_title}.png")
    plt.close()


def plot_mixtures_ifgs(phUnw,mask,file_path):
    '''
    Plot the original mixture interferogram sequence.
    '''
    import matplotlib.pyplot as plt
    import numpy as np
    from icasar.aux1 import col_to_ma

    fig_title = 'Mixtures (interferograms)'
    phUnw_rows = phUnw.shape[0]
    num_cols = 15
    num_rows = int(np.ceil(phUnw_rows / num_cols))
    fig, axes = plt.subplots(num_rows, num_cols, figsize=(20, 10))
    for i in range(num_rows * num_cols):
        if i < phUnw_rows:
            row = i // num_cols  # 计算子图所在的行
            col = i % num_cols  # 计算子图所在的列
            ax = axes[row, col]
            ax.imshow(col_to_ma(phUnw[i, :], mask))
            ax.set_xticks([])
            ax.set_yticks([])
        else:
            row = i // num_cols  # 计算子图所在的行
            col = i % num_cols  # 计算子图所在的列
            ax = axes[row, col]
            ax.axis('off')
    fig.suptitle(fig_title)
    fig.canvas.manager.set_window_title(fig_title)
    fig.savefig(f"{file_path}/{fig_title}.png")
    plt.tight_layout()
    plt.close()


def stacking_insar(sources,time_courses,source_number,mask,file_path,time_baselines,phUnw_mean):
    '''
    Use the stacking InSAR method to calculate the average surface deformation velocity and plot the average surface deformation velocity map for the region.
    :param sources: Spatial components of the recovered sources.
    :param time_courses: Temporal components of the recovered sources.
    :param source_number: Index position of the surface deformation source.
    :param time_baselines: Time baselines within this period, a single value.
    '''

    import numpy as np
    import matplotlib.pyplot as plt
    from icasar.aux1 import col_to_ma

    A=time_courses[:,source_number]
    A=np.reshape(A,(len(A),1))
    S=sources[source_number:source_number+1]
    ifgs_sources=A@S+phUnw_mean

    #inc tbaselines
    time_baselines_inc=np.diff(time_baselines)

    #stacking InSAR
    ph_sum=[0 for _ in range(len(ifgs_sources[0]))]
    t_sum=0
    for i,time_baseline in enumerate(time_baselines_inc):
        ph_sum+=time_baseline*ifgs_sources[i]
        t_sum=time_baseline**2
    ph_rate=ph_sum/t_sum
    deformation_velocity=ph_rate*(-0.056/(4*np.pi))*1000
    deformation_velocity= np.array(deformation_velocity).reshape(1, -1)

    fig_title='deformation_velocity'
    fig, ax = plt.subplots(figsize=(10, 10))
    vmin=np.min(deformation_velocity)
    vmax=np.max(deformation_velocity)
    w=ax.matshow(col_to_ma(deformation_velocity[0,:],mask),vmin=vmin,vmax=vmax)
    axin = ax.inset_axes([0, -0.06, 1, 0.05])
    fig.colorbar(w, cax=axin, orientation='horizontal')
    ax.set_xticks([])
    plt.title(fig_title)
    plt.savefig(f"{file_path}/{fig_title}.png")
    plt.close()

    return deformation_velocity