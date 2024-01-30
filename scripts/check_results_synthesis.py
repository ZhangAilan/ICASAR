#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/01/27
# Function:
#   check whether the Hydro + Wet + APScorrected = Obs
#   Synthesis data
#-------------------------------------------------------------------
import os
import numpy as np
import matplotlib.pyplot as plt
import pickle

file_path='D:\\ICASAR\\data\\Synthetic_Fault\\aps_data\\CorrectedIfgs-model6-defoFlag1-wetFlag1-hydroFlag1-iteraNum1-solver2-ueFixMethod0-weightScheme1-shortBt60-shortBtRelax500'
date = '20170404-20170416'
mask_path='data/Synthetic_Fault/mask.pkl'
with open(os.path.join(file_path, f'geo_{date}.APS'), 'rb') as fid:
    APS_data = np.fromfile(fid, dtype='>f4').reshape(207, 235)
with open(os.path.join(file_path, f'geo_{date}.unw.APScorrected'), 'rb') as fid:
    APScorrected = np.fromfile(fid, dtype='>f4').reshape(207, 235)
with open(os.path.join(file_path, f'geo_{date}.hydro'), 'rb') as fid:
    Hydro = np.fromfile(fid, dtype='>f4').reshape(207, 235)
with open(os.path.join(file_path, f'geo_{date}.unw.wet'), 'rb') as fid:
    Wet = np.fromfile(fid, dtype='>f4').reshape(207, 235)
with open(os.path.join(file_path, f'geo_{date}.unw'), 'rb') as fid:
    Obs = np.fromfile(fid, dtype='>f4').reshape(207, 235)
with open(mask_path, 'rb') as fid:
    mask = pickle.load(fid)

diff= APScorrected+Hydro+Wet-Obs
diff=np.where(mask,np.nan,diff)
np.savetxt('data/Synthetic_Fault/aps_data/diff.txt',diff)
plt.imshow(diff, cmap='jet', aspect='auto')
plt.colorbar()
plt.savefig('data/Synthetic_Fault/aps_data/diff.png')
print('Done!!!')
