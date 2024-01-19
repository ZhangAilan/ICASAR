import numpy as np
import matplotlib.pyplot as plt

# 打开干涉图文件
# 'rb'代表以二进制模式读取文本
with open('data/Synthetic_Fault/aps_data/CorrectedIfgs-model6-defoFlag1-wetFlag1-hydroFlag1-iteraNum1-solver2-ueFixMethod0-weightScheme1-shortBt60-shortBtRelax500/geo_20170404-20170416.unw.APScorrected', 'rb') as fid:
    # 读取数据
    data = np.fromfile(fid, dtype='>f4').reshape(207, 235)
print(data)

# 获取数据的行列数
rows, cols = data.shape
print('Number of rows:', rows)
print('Number of columns:', cols)

# 绘制图像
plt.imshow(data, cmap='jet', aspect='auto')
plt.show()