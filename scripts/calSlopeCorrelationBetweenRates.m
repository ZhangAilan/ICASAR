% Script used to calculate the slope and correlation between the recovered
% deformation rate and the true fault motion rate
%
% By Shuai WANG @NJTECH 2023-03-15
%==========================================================================
load('ref_index.mat');
width     = 235;
length    = 207;
lon_first = 93.4351852;
lat_first = 41.0972222;
post      = 0.015432;

fid  = fopen('ph_rate_simulated','rt','ieee-be');
data = fread(fid,[width length],'float');
fclose(fid);

fid  = fopen('ph_rate_nocorrection','rt','ieee-be');
nocorrection = fread(fid,[width length],'float');
nocorrection(nocorrection==0) = NaN;
fclose(fid);

fid  = fopen('ph_rate_linear','rt','ieee-be');
linear = fread(fid,[width length],'float');
linear(linear==0) = NaN;
fclose(fid);

fid  = fopen('ph_rate_css','rt','ieee-be');
css = fread(fid,[width length],'float');
css(css==0) = NaN;
fclose(fid);

fid  = fopen('ph_rate_apsphase','rt','ieee-be');
apsphase = fread(fid,[width length],'float');
apsphase(apsphase==0) = NaN;
fclose(fid);

figure;
subplot(2,3,1);
imagesc(data');title('simulated');caxis([-0.5 2])
subplot(2,3,2);
imagesc(nocorrection');title('nocorrection');caxis([-0.5 2])
subplot(2,3,3);
imagesc(linear');title('linear');caxis([-0.5 2])
subplot(2,3,4);
imagesc(css');title('css');caxis([-0.5 2])
subplot(2,3,5);
imagesc(apsphase');title('apsphase');caxis([-0.5 2])

% nocorrection
ref_value = data';
ref_value = ref_value(:);
ref_value = ref_value(ref_index);
data      = data - nanmean(ref_value);

data = data(:);
A    = [data ones(48645,1)];

B    = nocorrection(:);
index=find(~isnan(B));

A    = A(index,:);
B    = B(index,:);

[x stdx MRSE]=lscov(A,B);

slope_nocorrection     = x(1);
intercept_nocorrection = x(2);
fitrms_nocorrection    = rms(A(:,1)-B);

corr_nocorrection      = corr2(A(:,1),B);

% linear
A    = [data ones(48645,1)];

B    = linear(:);
index=find(~isnan(B));

A    = A(index,:);
B    = B(index,:);

[x stdx MRSE]=lscov(A,B);

slope_linear     = x(1);
intercept_linear = x(2);
fitrms_linear    = rms(A(:,1)-B);

corr_linear      = corr2(A(:,1),B);

% css
A    = [data ones(48645,1)];

B    = css(:);
index=find(~isnan(B));

A    = A(index,:);
B    = B(index,:);

[x stdx MRSE]=lscov(A,B);

slope_css     = x(1);
intercept_css = x(2);
fitrms_css    = rms(A(:,1)-B);

corr_css      = corr2(A(:,1),B);

% apsphase
A    = [data ones(48645,1)];

B    = apsphase(:);
index=find(~isnan(B));

A    = A(index,:);
B    = B(index,:);

[x stdx MRSE]=lscov(A,B);

slope_apsphase     = x(1);
intercept_apsphase = x(2);
fitrms_apsphase    = rms(A(:,1)-B);

corr_apsphase      = corr2(A(:,1),B);

[slope_nocorrection slope_linear slope_css slope_apsphase]
[corr_nocorrection corr_linear corr_css corr_apsphase]

% 
fid  = fopen('sig_ph_rate_nocorrection','rt','ieee-be');
sig_nocorrection = fread(fid,[width length],'float');
sig_nocorrection(sig_nocorrection==0) = NaN;
fclose(fid);

fid  = fopen('sig_ph_rate_linear','rt','ieee-be');
sig_linear = fread(fid,[width length],'float');
sig_linear(sig_linear==0) = NaN;
fclose(fid);

fid  = fopen('sig_ph_rate_css','rt','ieee-be');
sig_css = fread(fid,[width length],'float');
sig_css(sig_css==0) = NaN;
fclose(fid);

fid  = fopen('sig_ph_rate_apsphase','rt','ieee-be');
sig_apsphase = fread(fid,[width length],'float');
sig_apsphase(sig_apsphase==0) = NaN;
fclose(fid);

[nanmean(nanmean(sig_nocorrection)) nanmean(nanmean(sig_linear)) nanmean(nanmean(sig_css)) nanmean(nanmean(sig_apsphase))]