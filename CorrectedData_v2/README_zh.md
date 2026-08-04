# CorrectedData_v2

本目录是从 Demod1/Demod2 原始 TXT 时间序列重新生成的版本化修正数据，未覆盖旧数据。

## 正确通道映射

- Demod1：28 个沥青层 FBG（CH1=8、CH2=6、CH3=8、CH4=6）。
- Demod2：22 个土层 FBG（CH1=8、CH2=6、CH3=8）以及 CH4 温度参考。

## 时间过程定义

原始记录是从 0 荷载切换到加荷载并持续至记录结束，没有卸载阶段。因此本目录提供：

- `zero_load_baseline_nm`：检测到加载之前的同次试验基线；
- `delta_lambda_initial_nm`：加载后 15–60 秒的初期响应减去基线；
- `delta_lambda_final_nm`：记录结束前 60–10 秒的末期持载响应减去基线；
- `delta_lambda_peak_signed_nm`：加载段 1 秒中值序列中绝对值最大的带符号响应；
- `loaded_creep_change_nm`：末期持载值减去初期持载值；
- `load_onset_s`：自动检测的 0 荷载到加荷载切换时刻。

本数据不能直接提供卸载后的残余沉降。若要研究残余沉降，需要另行采集包含卸载和恢复阶段的序列。

## 文件

- `Corrected_Response_Matrix_Table_v2.csv`：22 工况 × 51 通道的修正响应表；
- `Corrected_Load_Event_Table_v2.csv`：每个工况的加载时刻和分析窗口；
- `Corrected_Case_Layer_Summary_v2.csv`：逐工况、逐层汇总；
- `Corrected_Sensor_Mapping_v2.csv`：正确传感器层位与坐标；
- `manifest.json`：版本与数据定义；
- `build_corrected_dataset_v2.py`：完整可复现生成脚本。

## 质量标记

- `OK`：可直接使用；
- `REVIEW_HISTORICAL_DRIFT`：独立无荷载基线中曾出现漂移，建议降权；
- `EXCLUDE_HIGH_PRELOAD_NOISE`：该工况加载前噪声过高，默认排除；
- `TEMPERATURE_REFERENCE`：温度参考通道，不作为应变标签。

## 相对位移

FBG 应变可用于恢复相对于加载前状态的挠度变化 `Delta w(x,y,t)`，但需要边界条件或至少一个位移锚点消除刚体平移与线性坡度零空间。未进行位移标定时，不应把它称为绝对沉降高程。
