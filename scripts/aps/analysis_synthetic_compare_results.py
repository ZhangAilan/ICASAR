#------------------------------------------------------------------
# Author: ZhangYuehao
# Email: yuehaozhang@njtech.edu.cn
# Zhihu: https://www.zhihu.com/people/bu-meng-cheng-kong-46/posts
# GitHub: https://github.com/ZhangAilan
#-------------------------------------------------------------------
# Date: 2024/03/28
# Function:
#   Analysis of the results of single interferogram comparison with synthetic deformation
#   RMSE
#-------------------------------------------------------------------
import matplotlib.pyplot as plt

ica_format='all'  #here can change the 'all/cum/inc'
RMSE_file_path='data\Synthetic_Fault\compare_results\single_compare_{}\RMSE_results.txt'.format(ica_format)

#read the txt file
with open(RMSE_file_path, 'r') as f:
    aps_RMSE=[]
    PCA_RMSE=[]
    ICA_RMSE=[]
    for line in f:
        data = line.strip().split(',')
        aps_RMSE.append(float(data[0]))
        PCA_RMSE.append(float(data[1]))
        ICA_RMSE.append(float(data[2]))
print("aps_RMSE:", aps_RMSE)
print("PCA_RMSE:", PCA_RMSE)
print("ICA_RMSE:", ICA_RMSE)

#plot the RMSE
plt.figure()
plt.bar(range(len(aps_RMSE)), aps_RMSE, label='APS')
plt.bar(range(len(PCA_RMSE)), PCA_RMSE, label='PCA')
plt.bar(range(len(ICA_RMSE)), ICA_RMSE, label='ICA')
plt.xlabel('Data Order')
plt.ylabel('RMSE')
plt.title('RMSE of Synthetic Deformation and APS/PCA/ICA')
plt.locator_params(axis='y', nbins=5) 
plt.legend()
plt.show()