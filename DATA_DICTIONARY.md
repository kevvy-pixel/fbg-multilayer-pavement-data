# 数据字典

## 统一标识

- `case_id`：工况名称，也是对应原始 TXT 文件名（不含 `.txt`）。
- `sensor_id`：整理后的唯一传感器点编号，例如 `D1_CH1_S1`。
- `sensor_string`：传感器串名称，例如 `SAL1`、`SAT2`。
- `channel`：解调仪通道，如 `D1_CH1`。

## 坐标与单位

- `x_cm`, `y_cm`, `z_cm`：整理后 CSV 中的传感器/荷载坐标，单位 cm。
- `X_m`, `Y_m`, `Z_m` 以及 `*_m`：空间模型 CSV 中的坐标，单位 m。
- `load_kg`：荷载质量，单位 kg。这里记录的是实验文件名和整理表中的质量标签，不等同于力（N）。
- `response_ue`：动态训练表中的响应列，表示从原始波长处理得到的响应值；具体预处理规则以对应 manifest 和重建脚本为准。

## 响应字段

- `zero_load_baseline_nm`：零荷载基线波长。
- `loaded_initial_nm` / `loaded_final_nm`：加载窗口初期/末期波长。
- `delta_lambda_initial_nm` / `delta_lambda_final_nm`：相对零荷载基线的波长变化。
- `delta_lambda_peak_signed_nm`：记录窗口内的带符号峰值波长变化。
- `loaded_creep_change_nm`：加载初期到加载末期的变化，用于观察保持荷载期间的变化。
- `load_onset_s`：从记录开始计的荷载开始时间，单位 s。

## 动态训练表字段

`film_dynamic_training_table.csv` 在响应字段之外，还包含 `relative_time_s`、`absolute_time_s`、`quality_weight`、`load_type`、`p1_x/p1_y`、`p2_x/p2_y`、`split_role` 和 `dev_fold`。`relative_time_s` 是相对工况时间；`absolute_time_s` 是原记录中的秒位置；双点工况用 p1/p2 表示两个荷载点，单点工况只使用 p1。

## 工况类型编码

- `SingleCenter`：单点中心
- `SingleEccentric`：单点偏心
- `DoubleSymmetric`：双点对称
- `DoubleAsymmetric`：双点不对称
- `LongitudinalCenterLine`：纵中心线上的单点
