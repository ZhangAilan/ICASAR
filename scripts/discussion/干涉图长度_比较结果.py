#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/05/06
# Function:
#   讨论不同干涉图长度下的对ICASAR分离信号的影响
#   统计15、30、45、60、75、90、105、111的干涉图集下的PCA、ICA和aps与deformation的均方根误差（format全部为cum）
#-------------------------------------------------------------------
import numpy as np
import pickle
from matplotlib import pyplot as plt
save_path='data/Synthetic_Fault/disscussion/干涉图长度/results'

def RMSE(x,y):
    return np.sqrt(np.nanmean((x-y)**2))

ifgs_set=[15,30,45,60,75,90,105,111]
RMSE_PCA=[]
RMSE_ICA=[]
RMSE_aps=[]
for i in range(len(ifgs_set)):
    deformation_flie='data/Synthetic_Fault/disscussion/干涉图长度/velocity_{}.pkl'.format(ifgs_set[i])
    aps_phase_file='data/Synthetic_Fault/disscussion/干涉图长度/velocity_aps_{}.pkl'.format(ifgs_set[i])
    stacking_PCA_file='example_spatial_03_APS_{}ifgs_cum/deformation_velocity_pca_r2.pkl'.format(ifgs_set[i])
    stacking_ICA_file='example_spatial_03_APS_{}ifgs_cum/deformation_velocity_ica_r2.pkl'.format(ifgs_set[i])
    with open(deformation_flie,'rb') as f:
        deformation=pickle.load(f)
    with open(aps_phase_file,'rb') as f:
        aps_phase_stacking=pickle.load(f)
    with open(stacking_PCA_file,'rb') as f:
        stacking_PCA=pickle.load(f)
    with open(stacking_ICA_file,'rb') as f:
        stacking_ICA=pickle.load(f)
    
    RMSE_PCA.append(RMSE(deformation,stacking_PCA))
    RMSE_ICA.append(RMSE(deformation,stacking_ICA))
    RMSE_aps.append(RMSE(deformation,aps_phase_stacking))

print(f'RMSE_PCA:{RMSE_PCA}')
print(f'RMSE_ICA:{RMSE_ICA}')
print(f'RMSE_aps:{RMSE_aps}')

#plot
plt.figure()
plt.plot(ifgs_set,RMSE_PCA,label='PCA')
plt.plot(ifgs_set,RMSE_ICA,label='ICA')
plt.plot(ifgs_set,RMSE_aps,label='APS')
plt.scatter(ifgs_set,RMSE_PCA)  
plt.scatter(ifgs_set,RMSE_ICA)
plt.scatter(ifgs_set,RMSE_aps)
plt.xlabel('ifgs_set')
plt.ylabel('RMSE')
plt.title('Stacking Compare')
plt.legend()
plt.savefig(f'{save_path}/Stacking.png')

#save RMSE to txt (np.savetxt)
np.savetxt(f'{save_path}/RMSE_PCA.txt',RMSE_PCA)
np.savetxt(f'{save_path}/RMSE_ICA.txt',RMSE_ICA)
np.savetxt(f'{save_path}/RMSE_aps.txt',RMSE_aps)

print('Done!')
    