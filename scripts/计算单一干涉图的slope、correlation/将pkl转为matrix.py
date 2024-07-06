#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/06/23
# Function:
#   将pkl转为matlab中的matrix
#-------------------------------------------------------------------
import numpy as np
import pickle
import scipy.io as sio
import os
import matplotlib.pyplot as plt

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

#file path
save_path='scripts/计算单一干涉图的slope、correlation'
aps_corrected_path='data/Synthetic_Fault/aps_corrected_data.pkl'
ICA_corrected_path='example_spatial_03_APS_cum/deformation_ifgs_ICA_series.pkl'
PCA_corrected_path='example_spatial_03_APS_cum/deformation_ifgs_PCA_series.pkl'
syn_def_path='data/Synthetic_Fault/结果/deformation_data/ifg_defo_subtract_reference.pkl'
raw_ifgs_path='data/Synthetic_Fault/raw_data/simDatasetsConsiderDefHydroWet'
dates_path='data/Synthetic_Fault/temp_corrected/tbaseline_info.pkl'
mask_path='data/Synthetic_Fault/mask.pkl'

with open(aps_corrected_path,'rb') as f:
    aps_corrected=pickle.load(f)
with open(ICA_corrected_path,'rb') as f:
    ICA_corrected=pickle.load(f)
with open(PCA_corrected_path,'rb') as f:
    PCA_corrected=pickle.load(f)
with open(syn_def_path,'rb') as f:
    syn_def=pickle.load(f)
with open(mask_path,'rb') as f:
    mask=pickle.load(f)
# print(ICA_corrected.shape)
#load the dates 
with open(dates_path, 'rb') as f:
    dates_all = pickle.load(f)
converted_dates = dates_all['ifg_dates']

unw_names=[]
for date_range in converted_dates:
    start_date,end_date=date_range.split('_')  
    unw_name=f"geo_{start_date}-{end_date}.unw"
    unw_names.append(unw_name)
# print(unw_names)

line_numbers=[1, 11, 19, 31, 43, 55, 65, 77, 89, 97, 108, 118, 125, 136, 142, 153, 159, 167, 179, 191, 201, 209, 218, 224, 232, 243, 252, 262, 271, 281, 292, 304, 316, 327, 338, 348, 357, 367, 375, 385, 394, 402, 414, 426, 438, 450, 461, 474, 485, 497, 504, 517, 529, 542, 548, 558, 568, 577, 585, 594, 601, 609, 618, 626, 633, 645, 653, 662, 672, 682, 690, 696, 707, 715, 725, 733, 744, 754, 763, 771, 778, 785, 791, 796, 801, 806, 811, 816, 821, 826, 830, 833, 836, 839, 842, 847, 852, 857, 862, 866, 870, 874, 878, 882, 887, 892, 895, 899, 903, 906, 908]
#reshape
syn_true_defo=[]
raw_ifgs=[]
ica_defo=[]
pca_defo=[]
for i in range(len(line_numbers)):
    index=line_numbers[i]-1
    synthetic_deformation=syn_def[:, :, index].T
    synthetic_deformation=np.where(mask,np.nan,synthetic_deformation)
    syn_true_defo.append(synthetic_deformation)

    with open(os.path.join(raw_ifgs_path,unw_names[i]), 'rb') as f: #raw ifg
        raw_ifg=np.fromfile(f, dtype='>f4').reshape(207, 235)
    raw_ifg = np.ma.array(raw_ifg, mask=mask)
    raw_ifgs.append(raw_ifg)

    ica_deformation=col_to_ma(ICA_corrected[i,:],mask) #ica deformation
    pca_deformation=col_to_ma(PCA_corrected[i,:],mask)
    ica_defo.append(ica_deformation)
    pca_defo.append(pca_deformation)


aps_corrected = np.array(aps_corrected, dtype=np.double)
syn_true_defo = np.array(syn_true_defo, dtype=np.double)
raw_ifgs = np.array(raw_ifgs, dtype=np.double)
ica_defo = np.array(ica_defo, dtype=np.double)
pca_defo = np.array(pca_defo, dtype=np.double)

#长周期操作，窗口设置为10，周期约为120天左右
def sliding_window_sum(array, window_size):
    """
    对数组的第一个维度进行滑动窗口求和
    array (np.ndarray): 原始数组
    window_size (int): 滑动窗口的大小
    """
    # 获取原始数组的形状
    original_shape = array.shape
    # 计算新的形状
    new_shape = (original_shape[0] - window_size + 1,) + original_shape[1:]
    # 创建新数组
    new_array = np.zeros(new_shape)
    # 对第一个维度进行滑动窗口求和
    for i in range(new_shape[0]):
        new_array[i] = np.sum(array[i:i+window_size], axis=0)
    return new_array

window_size = 20
aps_corrected = sliding_window_sum(aps_corrected, window_size)
syn_true_defo = sliding_window_sum(syn_true_defo, window_size)
raw_ifgs = sliding_window_sum(raw_ifgs, window_size)
ica_defo = sliding_window_sum(ica_defo, window_size)
pca_defo = sliding_window_sum(pca_defo, window_size)


#save to mat
#很重要的一点：ica和pca的结果中已经没有nan值，所以在计算时不必再考虑
sio.savemat(os.path.join(save_path,'syn_true_defo.mat'),{'syn_true_defo':syn_true_defo})
sio.savemat(os.path.join(save_path,'ica_defo.mat'),{'ica_defo':ica_defo})
sio.savemat(os.path.join(save_path,'pca_defo.mat'),{'pca_defo':pca_defo})
sio.savemat(os.path.join(save_path,'raw_ifgs.mat'),{'raw_ifgs':raw_ifgs})
sio.savemat(os.path.join(save_path,'aps_corrected.mat'),{'aps_corrected':aps_corrected})
print ("Done!!!")