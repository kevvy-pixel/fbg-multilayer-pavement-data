# FBG 多层路面试验数据仓库

本仓库保存多层沥青路面模型试验的原始解调数据、传感器坐标、基线分析结果和版本化响应数据。当前建模与神经场实验应优先使用 `CorrectedData_v2`，旧版 `Response_Matrix_Table.csv` 仅用于结果追溯。

## 当前权威数据版本

`CorrectedData_v2` 从 Demod1/Demod2 原始时间序列重新生成，主要修正如下：

- Demod1：28个沥青层FBG；
- Demod2：22个土层FBG，外加1个温度参考；
- 修正D1_CH3、D1_CH4、D2_CH1、D2_CH2的历史层位和坐标错误；
- 每个工况使用同次记录的加载前窗口建立零荷载基线；
- 自动识别零荷载到加载状态的切换时刻；
- 对D2_CH1的可变峰数执行单调轨迹匹配；
- 提供加载初期、持载末期、带符号峰值和持载蠕变量；
- 对历史漂移和高预载噪声提供质量标记。

## 数据过程边界

现有原始记录包含：

`零荷载 → 加载瞬间 → 持载变化 → 持载末期`

不包含卸载和恢复阶段，因此可研究加载瞬时响应、持载变形、持载蠕变、相对挠度变化和沥青—土层响应时延，但不能直接研究卸载后的残余沉降。

## 目录说明

| 路径 | 说明 |
|---|---|
| `Demod1/` | 沥青层解调仪原始记录 |
| `Demod2/` | 土层与温度通道原始记录 |
| `CorrectedData_v2/` | 当前权威修正数据、映射、事件表和生成脚本 |
| `baseline_data/` | 基线分析数据 |
| `geometry/` | 传感器与试件几何信息 |
| `UnifiedDataBase/`、`ResponseDatabase/` | 旧版处理中间结果，仅用于追溯 |

## 重新生成修正数据

需要Python 3.10及以上版本，并安装 `numpy` 和 `pandas`：

```powershell
python CorrectedData_v2/build_corrected_dataset_v2.py . CorrectedData_v2
```

脚本可以直接在 `CorrectedData_v2` 中运行；若源脚本与目标脚本为同一文件，不再执行自复制，从而避免 `SameFileError`。

## 主要输出

- `Corrected_Response_Matrix_Table_v2.csv`：22工况×51通道；
- `Corrected_Load_Event_Table_v2.csv`：加载时刻与分析窗口；
- `Corrected_Case_Layer_Summary_v2.csv`：逐工况逐层汇总；
- `Corrected_Sensor_Mapping_v2.csv`：正确层位、方向和坐标；
- `manifest.json`：版本、规模和适用范围；
- `README_zh.md`：字段与质量标记详细说明。

## 质量标记

- `OK`：可直接使用；
- `REVIEW_HISTORICAL_DRIFT`：历史基线存在漂移，建议降权；
- `EXCLUDE_HIGH_PRELOAD_NOISE`：加载前噪声过高，默认排除；
- `TEMPERATURE_REFERENCE`：温度参考，不作为应变标签。

## 使用约束

未经过位移计、DIC或激光测量标定时，FBG反演结果应称为“相对挠度”或“相对位移代理”，不应称为绝对沉降高程。数据的访问、复制和公开应遵守试验授权及论文数据政策。
