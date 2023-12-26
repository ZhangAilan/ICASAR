import numpy as np
import matplotlib.pyplot as plt

with open('D:\\ICASAR\\data\\Synthetic_Fault\\raw_data\\simDatasetsConsiderDefHydroWet\\geo_20170404-20170416.unw','rb') as fid:
    data=np.fromfile(fid,dtype='>f4').reshape(207,235)

plt.imshow(data, cmap='jet', aspect='auto', vmin=-40, vmax=40)
plt.colorbar()
plt.show()