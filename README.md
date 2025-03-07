# multiprocess-python
current task
- can receive signal
next
- make a tx and rx sdr
- stream result with zmq (maybe run with ubuntu)-
- (in case want to use bladerf windows) follow another markdown file

general idea
<img src = https://github.com/user-attachments/assets/d649d67e-a638-41c6-be69-30c61d00abcf>


result
```
load files
complete load_PSS_seq!
start process
fshift_corr:  {0} {np.int64(2)} {np.int64(212552)} {np.float64(0.06803419198859888)}
fshift_corr:  {15000} {np.int64(0)} {np.int64(135308)} {np.float64(0.06483307552265592)}
fshift_corr:  {30000} {np.int64(1)} {np.int64(211873)} {np.float64(0.16513477579241917)}
fshift_corr:  {45000} {np.int64(1)} {np.int64(211873)} {np.float64(0.23058730841798264)}
fshift_0: {'fshift_data': 0, 'fshift_NID2': 2, 'fshift_corr_ind': 212552, 'fshift_corr_val': 0.06803419198859888}
fshift_15000: {'fshift_data': 15000, 'fshift_NID2': 0, 'fshift_corr_ind': 135308, 'fshift_corr_val': 0.06483307552265592}
fshift_30000: {'fshift_data': 30000, 'fshift_NID2': 1, 'fshift_corr_ind': 211873, 'fshift_corr_val': 0.16513477579241917}
fshift_45000: {'fshift_data': 45000, 'fshift_NID2': 1, 'fshift_corr_ind': 211873, 'fshift_corr_val': 0.23058730841798264}
---max_fshift_corr---sel_fshift fshift_45000, sel_NID2 1, sel_corr_ind 211873, sel_corr_val 0.23058730841798264
```
