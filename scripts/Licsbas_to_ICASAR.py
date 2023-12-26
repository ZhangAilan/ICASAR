# This scipt is used for the Xianshui River data.
# Convert the data obtained from LiCSBAS into a format that can be used by ICASAR.


import h5py
import numpy as np
import numpy.ma as ma
import os
import pickle

#TOOLS
def read_img(file, length, width, dtype=np.float32, endian='little'):
    if endian == 'little':
        data = np.fromfile(file, dtype=dtype).reshape((length, width))
    else:
        data = np.fromfile(file, dtype=dtype).byteswap().reshape((length, width))
    return data

def rank3_ma_to_rank2(ifgs_r3,consistent_mask=False):
    n_ifgs=ifgs_r3.shape[0]
    #1: fix the mask
    mask_coh_water=ifgs_r3.mask
    if consistent_mask:
        mask_coh_water_consistent=mask_coh_water[0,]
    else:
        mask_coh_water_sum=np.sum(mask_coh_water,axis=0)
        mask_coh_water_consistent=np.where(mask_coh_water_sum == 0, np.zeros(mask_coh_water_sum.shape),
                                                                          np.ones(mask_coh_water_sum.shape)).astype(bool)

    ifgs_r3_consistent=ma.array(ifgs_r3,mask=ma.repeat(mask_coh_water_consistent[np.newaxis,],n_ifgs,axis=0))

    #2: convert to rank2
    n_pixs=ma.compressed(ifgs_r3_consistent[0,]).shape[0]
    ifgs_r2=np.zeros((n_ifgs,n_pixs))
    for ifg_n, ifg in enumerate(ifgs_r3_consistent):
        ifgs_r2[ifg_n,:]=ma.compressed(ifg)

    return ifgs_r2,mask_coh_water_consistent

def daisy_chain_from_acquisitions(acquisitions):
    daisy_chain=[]
    n_acqs=len(acquisitions)
    for i in range(n_acqs-1):
        daisy_chain.append(f"{acquisitions[i]}_{acquisitions[i+1]}")
    return daisy_chain

def baseline_from_names(names_list):
    from datetime import datetime
    baselines=[]
    for file in names_list:
        master=datetime.strptime(file.split('_')[-2],'%Y%m%d')
        slave=datetime.strptime(file.split('_')[-1][:8],'%Y%m%d')
        baselines.append(-1*(master-slave).days)
    return baselines        

def create_lon_lat_meshgrids(corner_lon,corner_lat,post_lon,post_lat,ifg):
    ny,nx=ifg.shape
    x=corner_lon+(post_lon*np.arange(nx))
    y=corner_lat+(post_lat*np.arange(ny))
    xx,yy=np.meshgrid(x,y)
    geocode_info={'lons_mg':xx,
                  'lats_mg':yy}
    return geocode_info

folder_path='/home/z/data/licsbas_example02/135D_06019'

#0:Path and name
file_name_cum='cum.h5'
filepath_cum=os.path.join(folder_path,file_name_cum)
file_name_mask='mask'
filepath_mask=os.path.join(folder_path,file_name_mask)

new_folder_name='results'
save_path=os.path.join(folder_path,new_folder_name)
os.makedirs(save_path,exist_ok=True)

#1: get the incremental deformation
cumh5=h5py.File(filepath_cum,'r')
displacement_r3={}
displacement_r2={}
tbaseline_info={}
tbaseline_info["acq_dates"]=cumh5['imdates'][()].astype(str).tolist()
cumulative=cumh5['cum'][()]
cumulative*=0.01

# access the dataset
dataset_names = list(cumh5.keys())
for dataset_name in dataset_names:
    dataset = cumh5[dataset_name]
    print("{:<10s} \t {:<10s}".format(dataset_name, str(dataset.shape)))
    #print("Dataset Value:", dataset[()])  # 获取数据集的值



#2: Reference the time series 
length,width=(cumh5['slc.mli'][()]).shape
ref_str=cumh5['refarea'][()]
ref_str=ref_str.decode()
ref_xy = {'x_start': int(ref_str.split('/')[0].split(':')[0]),
          'x_stop': int(ref_str.split('/')[0].split(':')[1]),
          'y_start': int(ref_str.split('/')[1].split(':')[0]),
          'y_stop': int(ref_str.split('/')[1].split(':')[1])}
print('\nref_xy\n',ref_xy)
try:  # reference the time series
    ifg_offsets = np.nanmean(cumulative[:, ref_xy['y_start']: ref_xy['y_stop'], ref_xy['x_start']: ref_xy['x_stop']],axis=(1, 2))  # get the offset between the reference pixel/area and 0 for each time
    cumulative = cumulative - np.repeat(np.repeat(ifg_offsets[:, np.newaxis, np.newaxis], cumulative.shape[1], axis=1),cumulative.shape[2],axis=2)  # do the correction (first make ifg_offsets teh same size as cumulative).
    print(f"Succesfully referenced the LiCSBAS time series using the pixel/area selected by LiCSBAS.  ")
except:
    print(f"Failed to reference the LiCSBAS time series - use with caution!  ")


#3： open the mask
mask_licsbas=read_img(filepath_mask,length,width)
mask_licsbas=np.logical_and(mask_licsbas,np.invert(np.isnan(mask_licsbas)))
mask_licsbas=np.invert(mask_licsbas)

dem=cumh5['hgt'][()]
mask_dem=np.isnan(dem)
mask_cum=np.isnan(cumulative)
mask_cum=(np.sum(mask_cum,axis=0)>0)
mask=np.logical_or(mask_dem,mask_cum)  
#mask=np.logical_or(mask_licsbas,np.logical_or(mask_dem,mask_cum))

mask_r3=np.repeat(mask[np.newaxis,],cumulative.shape[0],0)
dem_ma=ma.array(dem,mask=mask)
displacement_r2['dem']=dem_ma
displacement_r3['dem']=dem_ma


#4: mask the data
displacement_r3['cumulative']=ma.array(cumulative,mask=mask_r3)
displacement_r3['incremental']=np.diff(displacement_r3['cumulative'],axis=0)
if displacement_r3['incremental'].mask.shape==():
    displacement_r3['incremental'].mask=mask_r3[1:]
n_im,length,width=displacement_r3['cumulative'].shape

displacement_r2['cumulative'],displacement_r2['mask']=rank3_ma_to_rank2(displacement_r3['cumulative'])
displacement_r2['incremental'],_=rank3_ma_to_rank2(displacement_r3['incremental'])
#print("\nnumber_displacement_r2_incremental:\n",displacement_r2['incremental'].shape[0])

#5: get the dates
tbaseline_info['ifg_dates']=daisy_chain_from_acquisitions(tbaseline_info['acq_dates'])
tbaseline_info['baselines']=baseline_from_names(tbaseline_info['ifg_dates'])
tbaseline_info['baselines_cumulative']=np.cumsum(tbaseline_info['baselines'])

#6: get the lons and lats
geocode_info=create_lon_lat_meshgrids(cumh5['corner_lon'][()],cumh5['corner_lat'][()],
                                      cumh5['post_lon'][()],cumh5['post_lat'][()],displacement_r3['incremental'][0,:,:])
displacement_r2['lons']=geocode_info['lons_mg']
displacement_r2['lats']=geocode_info['lats_mg']
displacement_r3['lons']=geocode_info['lons_mg']
displacement_r3['lats']=geocode_info['lats_mg']

#7: save the data
save_displacement_path=os.path.join(save_path,'displacement_r2.pkl')
with open(save_displacement_path, 'wb') as f:
    pickle.dump(displacement_r2, f)
save_tbaseline_path=os.path.join(save_path,'tbaseline_info.pkl')
with open(save_tbaseline_path,'wb') as f:
    pickle.dump(tbaseline_info,f)
print("Done!")
