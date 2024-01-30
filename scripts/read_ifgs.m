 % 打开干涉图文件
 % 'rb'代表以二进制模式读取文本
 % 'rt'代表以文本模式读取文本
fid = fopen('D:\ICASAR\data\Altyn_Tagh_Fault\aps_data\CorrectedTSIfgs-model6-defoFlag1-wetFlag1-hydroFlag1-iteraNum1-solver2-ueFixMethod0-weightScheme1-shortBt60-shortBtRelax500-longBtMinMax0-500\geo_20170404-20170428.APS', 'rb', 'ieee-be'); % 使用大端序读取

% 读取数据
data = fread(fid, [235 207], 'float');
fclose(fid);

% 获取数据的行列数
[rows,cols]=size(data);
fprintf('Number of rows: %d\n', rows);
fprintf('Number of columns: %d\n', cols);

%绘制图像
figure;imagesc(data')
colorbar; 