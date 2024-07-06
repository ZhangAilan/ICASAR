#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/03/25
# Function:
#   stacking Altyn data (real results)
#-------------------------------------------------------------------
import pickle
import numpy as np

ifgs_file_path='data/Altyn_Tagh_Fault/aps_data_real/real_correct/displacement_r2.pkl'
tbaseline_file_path='data/Altyn_Tagh_Fault/aps_data_real/real_correct/tbaseline_info.pkl'
save_path='data/Altyn_Tagh_Fault/aps_data_real/aps_real_corrected_stacking'

#load the data
with open(ifgs_file_path,'rb') as f:
    ifgs_data=pickle.load(f)
with open(tbaseline_file_path,'rb') as f:
    tbaseline_info=pickle.load(f)

ifgs_corrected=ifgs_data['cumulative']
tbaselines=tbaseline_info['baselines']
mask=ifgs_data['mask']
print("\nifgs_corrected:\n",ifgs_corrected.shape)
print("\ntbaselines:\n",tbaselines)
print("\nmask:\n",mask.shape)

#stacking
ph_sum=np.zeros(ifgs_corrected[0].shape)
t_sum=0
for i in range(len(tbaselines)):
    time_baseline=tbaselines[i]
    time_baseline=time_baseline/365.25
    t_sum+=time_baseline**2
    for j in range(ifgs_corrected.shape[1]):
        ph_sum[j]+=ifgs_corrected[i][j]*time_baseline
ph_rate=ph_sum/t_sum
deformation_velocity=ph_rate*(-0.056/(4*np.pi))*1000

#plot
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
import matplotlib.pyplot as plt
import os

deformation_velocity=col_to_ma(deformation_velocity,mask)
plt.imshow(deformation_velocity,cmap='jet',aspect='auto',vmin=-5,vmax=5)
plt.colorbar()
plt.savefig(os.path.join(save_path,'velocity_mm_yr.png'))

with open(os.path.join(save_path,'velocity_mm_yr.pkl'),'wb') as f:
    pickle.dump(deformation_velocity,f)

print("Done!!!")


