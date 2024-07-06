#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/05/06
# Function:
#   组织合适于ICASAR的数据格式，包括15、30、45、...、111的干涉图集
#   计算该干涉图集下的deformation velocity
#   计算该干涉图集下的aps stacking
#-------------------------------------------------------------------
import numpy as np
import pickle
import os
import scipy.io
import datetime
import numpy.ma as ma 
import matplotlib.pyplot as plt                      

def create_lon_lat_meshgrids(corner_lon,corner_lat,post_lon,post_lat,ifg):
    ny,nx=ifg.shape
    x=corner_lon+(post_lon*np.arange(nx))
    y=corner_lat+(post_lat*np.arange(ny))
    xx,yy=np.meshgrid(x,y)
    geocode_info={'lons_mg':xx,
                  'lats_mg':yy}
    return geocode_info

def baseline_from_names(names_list):
    from datetime import datetime
    baselines=[]
    for file in names_list:
        master=datetime.strptime(file.split('_')[-2],'%Y%m%d')
        slave=datetime.strptime(file.split('_')[-1][:8],'%Y%m%d')
        baselines.append(-1*(master-slave).days)
    return baselines
#-------------------------------------------------------设置参数-------------------------------------------------------#
ifgs_set=[15,30,45,60,75,90,105,111]
file_path='data/Synthetic_Fault/raw_data/simDatasetsConsiderDefHydroWet'
ifg_fileldist_path=os.path.join(file_path,"ifg_filelist.txt")
epoch_master_slave_dates_info_path=os.path.join(file_path,"simSAR.mat")
data=scipy.io.loadmat(epoch_master_slave_dates_info_path)
save_path='data/Synthetic_Fault/disscussion/干涉图长度'
file_aps_path="data/Synthetic_Fault/aps_data/CorrectedIfgs-model6-defoFlag1-wetFlag1-hydroFlag2-iteraNum1-solver2-ueFixMethod0-weightScheme1-shortBt60-shortBtRelax500"
dem_path=os.path.join(file_path,"EQA.dem")
aps_corrected_data_path='data/Synthetic_Fault/aps_corrected_data.pkl'

#the reference region
reference_region = np.array([[95.15, 40.03],
                             [95.25, 40.03],
                             [95.25, 39.93],
                             [95.15, 39.93],])
WIDTH=  235
FILE_LENGTH=  207
X_FIRST=   93.4352
X_STEP=    0.0154
Y_FIRST=   41.0972
Y_STEP=   -0.0154

#lons && lats
corner_lon=X_FIRST  #经度
corner_lat=Y_FIRST  #纬度
post_lon=X_STEP
post_lat=Y_STEP

ref_index=[]
for item in reference_region:
    x,y=item
    i=int(np.floor((x-X_FIRST)/X_STEP))
    j=int(np.floor((y-Y_FIRST)/Y_STEP))
    ref_index.append([i,j])

ifg_defo=data['ifg_defo']
sar_epoch=data['sar_epoch']
date_format="%Y%m%d"
converted_dates=[]
for i in range(len(sar_epoch)-1):
    start_date=datetime.datetime.strptime(str(sar_epoch[i][0]),date_format).strftime(date_format)
    end_date=datetime.datetime.strptime(str(sar_epoch[i + 1][0]), date_format).strftime(date_format)
    converted_dates.append(f"{start_date}_{end_date}")

#dem
with open(dem_path,'rb') as f:
    dem=np.fromfile(f,dtype='>f4').reshape(FILE_LENGTH,WIDTH)

#aps corrected data
with open(aps_corrected_data_path,'rb') as f:
    aps_corrected_data=pickle.load(f)
print(aps_corrected_data.shape)

#-------------------------------------------------------开始处理-------------------------------------------------------#
for i_1 in range(len(ifgs_set)):
    item=ifgs_set[i_1]
    converted_dates_ifgset=converted_dates[:item]
    print("----------------------------------------------------")
    print("\nStart to process the NO.{} ifgs set.".format(i_1))

    ####---------------------------------------------calculate the deformation velocity---------------------------------------------------------------------------####
    time_baselines=[]
    for date in converted_dates_ifgset:
        start_date,end_date=date.split('_')
        start_date=datetime.datetime.strptime(start_date,date_format)
        end_date=datetime.datetime.strptime(end_date,date_format)
        time_baselines.append((end_date-start_date).days)
    print("\nTime baselines of the NO.{} ifgs set:\n{}".format(i_1,time_baselines))

    unw_names=[]
    for date_range in converted_dates_ifgset:
        start_date,end_date=date_range.split('_')  
        unw_name=f"geo_{start_date}-{end_date}.unw"
        unw_names.append(unw_name)
    print("\nUnwrapped names of the NO.{} ifgs set:\n{}".format(i_1,unw_names))
    
    line_numbers=[]  #save the line number of the unw_names
    with open(ifg_fileldist_path,'r') as f:
        for i,line in enumerate(f,start=1):
            if any(name in line for name in unw_names):
                line_numbers.append(i)
    print("\nLine numbers of the NO.{} ifgs set:\n{}".format(i_1,line_numbers))
    #read the ifg_defo data
    defo_data=[]
    for index in line_numbers:
        defo_data.append(ifg_defo[:,:,index-1])
    defo_data=np.array(defo_data)
    print("\nThe shape of the deformation data of the NO.{} ifgs set:".format(i_1),defo_data.shape)

    #stacking
    time_baselines_cum=np.cumsum(time_baselines)
    defo_data_cum=np.cumsum(defo_data,axis=0)
    ph_sum=np.zeros((235,207))
    t_sum=0
    for m in range(len(time_baselines_cum)):
        time_baseline=time_baselines_cum[m]
        time_baseline=time_baseline/365.25
        t_sum+=time_baseline**2
        for j in range(defo_data_cum[m].shape[0]):
            for k in range(defo_data_cum[m].shape[1]):
                ph_sum[j][k]+=time_baseline*defo_data_cum[m][j][k]
    ph_rate=ph_sum/t_sum
    velocity=ph_rate
    print("\nThe shape of the velocity of the NO.{} ifgs set:".format(i_1),velocity.shape)

    #remove the average value of the reference region
    ref_index=np.array(ref_index)
    ref_value=[]
    for index in ref_index:
        ref_value.append(velocity[index[0],index[1]])
    ref_value=np.array(ref_value)
    velocity=velocity-ref_value.mean()
    velocity=velocity.T

    #save the velocity
    velocity_file=os.path.join(save_path,f'velocity_{item}.pkl')
    with open(velocity_file,'wb') as f:
        pickle.dump(velocity,f) 

    ####---------------------------------------------组织成ICASAR所需的数据格式---------------------------------------------------------------------------####
    unw_names=[name.replace('.unw','.unw.APScorrected') for name in unw_names]
    #ifgs数据
    displacement_r3={}
    displacement_r3_inc=[]
    for unw_name in unw_names:
        fullpath=os.path.join(file_aps_path,unw_name)
        with open(fullpath,'rb') as f:
            ifg_data=np.fromfile(f,dtype='>f4').reshape(FILE_LENGTH,WIDTH)
            ifg_data[ifg_data == 0] = np.nan
            displacement_r3_inc.append(ifg_data)
    displacement_r3['incremental']=np.array(displacement_r3_inc)

    #mask
    mask_nan_r3=np.where(np.isnan(displacement_r3['incremental']),True,False)
    mask_r2=np.any(mask_nan_r3,axis=0)

    #dem
    displacement_r3['dem']=dem

    #将displacement_r3转换为displacement_r2
    displacement_r2={}
    n_ifgs=displacement_r3['incremental'].shape[0]
    ifgs_r3_masked=ma.array(displacement_r3['incremental'],mask=ma.repeat(mask_r2[np.newaxis,],n_ifgs,axis=0))
    n_pixs=ma.compressed(ifgs_r3_masked[0,]).shape[0]
    ifgs_r2=np.zeros((n_ifgs,n_pixs))
    for ifg_n,ifg in enumerate(ifgs_r3_masked):
        ifgs_r2[ifg_n,:]=ma.compressed(ifg)

    displacement_r2['incremental']=ifgs_r2
    displacement_r2['mask']=mask_r2
    displacement_r2['dem']=displacement_r3['dem']
    displacement_r2['cumulative']=np.cumsum(displacement_r2['incremental'],axis=0)
    print(displacement_r2['cumulative'].shape)

    #经纬度数据
    geocode_info=create_lon_lat_meshgrids(corner_lon,corner_lat,post_lon,post_lat,displacement_r2['dem'])
    displacement_r2['lons']=geocode_info['lons_mg']
    displacement_r2['lats']=geocode_info['lats_mg']

    #日期数据
    tbaseline_info={}
    tbaseline_info['ifg_dates']=converted_dates_ifgset
    tbaseline_info['baselines']=baseline_from_names(tbaseline_info['ifg_dates'])
    tbaseline_info['baselines_cumulative']=np.cumsum(tbaseline_info['baselines'])

    #save the data
    displacement_file=os.path.join(save_path,f'displacement_r2_{item}.pkl')    
    tbaseline_info_file=os.path.join(save_path,f'tbaseline_info_{item}.pkl')
    with open(displacement_file,'wb') as f:
        pickle.dump(displacement_r2,f)
    with open(tbaseline_info_file,'wb') as f:
        pickle.dump(tbaseline_info,f)
    print("\nNO.{} ICASAR所需数据已转换完成。".format(i_1))


    ####---------------------------------------------计算该干涉图集下的aps stacking---------------------------------------------------------------------------####
    aps_corrected_data_ifgset=aps_corrected_data[:item,:,:]
    #stacking
    displacement_r3_cum=np.cumsum(displacement_r3_inc,axis=0)
    ph_sum=np.zeros((207,235))
    t_sum=0
    for m in range(len(time_baselines_cum)):
        time_baseline=time_baselines_cum[m]
        time_baseline=time_baseline/365.25
        t_sum+=time_baseline**2
        for j in range(displacement_r3_cum[m].shape[0]):
            for k in range(displacement_r3_cum[m].shape[1]):
                ph_sum[j][k]+=time_baseline*displacement_r3_cum[m][j][k]
    ph_rate=ph_sum/t_sum
    deformation_velocity=ph_rate

    #save the velocity
    velocity_file=os.path.join(save_path,f'velocity_aps_{item}.pkl')
    with open(velocity_file,'wb') as f:
        pickle.dump(deformation_velocity,f)
    print("\nNO.{} 干涉图集下的aps stacking已完成。".format(i_1))
print("\nAll the process has been completed!!!")


