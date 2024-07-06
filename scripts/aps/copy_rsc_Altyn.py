#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/01/14
# Function:
#   copy the rsc file to fit the aps_phase program
#-------------------------------------------------------------------
import os
folder_path='data/Altyn_Tagh_Fault/raw_data/unw-coh0.5-decimated-withUECorrectedAuto'
rsc_file_path='data/Altyn_Tagh_Fault/raw_data/unw-coh0.5-decimated-withUECorrectedAuto/geo_20210314-20210326.unw_mask_utm.UEcorrected.rsc'

#read the rsc file
with open(rsc_file_path,'r') as f:
    rsc=f.readlines()

#get a list of all .UEcorrected files
ifg_filelist=[f for f in os.listdir(folder_path) if f.endswith('.UEcorrected')]
#save the ifg_filelist
with open(folder_path+'/ifg_filelist.txt','w') as f:
    for i in ifg_filelist:
        f.write(i+'\n')

# #write the rsc file
# for i in ifg_filelist[:-1]:
#     with open(folder_path+'/'+i+'.rsc','w') as f:
#         for line in rsc:
#             f.write(line)
print('Done!')