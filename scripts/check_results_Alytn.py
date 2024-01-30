#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/01/27
# Function:
#   check whether the Hydro + Wet + APScorrected = Obs
#   Alytn fault data
#-------------------------------------------------------------------
import os
import numpy as np
import matplotlib.pyplot as plt
import pickle

file_path='data/Altyn_Tagh_Fault/aps_data/CorrectedIfgs-model6-defoFlag1-wetFlag1-hydroFlag1-iteraNum1-solver2-ueFixMethod0-weightScheme1-shortBt60-shortBtRelax500'
date = '20170404-20170428'
mask_path='data/Altyn_Tagh_Fault/mask.pkl'
with open(os.path.join(file_path, f'geo_{date}.APS'), 'rb') as fid:
    APS_data = np.fromfile(fid, dtype='>f4').reshape(207, 235)
with open(os.path.join(file_path, f'geo_{date}.UEcorrected.APScorrected'), 'rb') as fid:
    APScorrected = np.fromfile(fid, dtype='>f4').reshape(207, 235)
with open(os.path.join(file_path, f'geo_{date}.hydro'), 'rb') as fid:
    Hydro = np.fromfile(fid, dtype='>f4').reshape(207, 235)
with open(os.path.join(file_path, f'geo_{date}.UEcorrected.wet'), 'rb') as fid:
    Wet = np.fromfile(fid, dtype='>f4').reshape(207, 235)
with open(os.path.join(file_path, f'geo_{date}.UEcorrected'), 'rb') as fid:
    Obs = np.fromfile(fid, dtype='>f4').reshape(207, 235)
with open(mask_path, 'rb') as fid:
    mask = pickle.load(fid)

with open('data/Altyn_Tagh_Fault/raw_data/unw-coh0.5-decimated-withUECorrectedAuto/geo_20170404-20170428.unw_mask_utm.UEcorrected','rb') as f:
    unw_mask=np.fromfile(f,dtype='>f4').reshape(207,235)

diff= Hydro + Wet + APScorrected - Obs
diff=np.where(mask,np.nan,diff)
np.savetxt('data/Altyn_Tagh_Fault/aps_data/diff.txt',diff)
plt.imshow(diff, cmap='jet', aspect='auto')
plt.colorbar()
plt.savefig('data/Altyn_Tagh_Fault/aps_data/diff.png')
print('Done!!!')