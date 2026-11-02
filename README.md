# 路面 FBG 传感器—荷载工况数据集

## 1. 这是什么

这是一个用于研究“路面不同位置施加荷载后，FBG 光纤传感器波长如何变化”的完整数据集。它把同一项目的原始采集文件、解调仪与传感器的对应关系、整理后的可分析表格、以及路面三维坐标模型放在同一个目录中。

数据的基本逻辑是：

**荷载工况 → 路面上的荷载坐标 → FBG 传感器空间位置 → Demod1/2 的通道 → 每个传感器点的波长响应**。

其中，波长通常以 nm 表示；荷载质量以 kg 表示；空间模型中的坐标以 m 表示，整理后的响应表中坐标以 cm 表示。

## 2. 目录结构

```text
guochuang_fbg_pavement_dataset/
├─ README.md                         本说明（先读这里）
├─ DATA_DICTIONARY.md                文件和字段字典
├─ SOURCE_PATHS.md                   原始来源与整理规则
├─ dataset_manifest.json             文件数量、行数、单位等机器可读摘要
├─ file_inventory.csv                每个文件的相对路径、大小和时间
├─ mapping/
│  └─ demod对应关系.xlsx             官方通道—传感器对应关系
├─ raw_data/                         原始采集文件，未改写
│  ├─ Demod1/                        有荷载工况的 Demod1 TXT
│  ├─ Demod2/                        有荷载工况的 Demod2 TXT
│  ├─ demo1无工况结果/               Demod1 无荷载基线 Peaks.*.txt
│  └─ demo2无工况结果/               Demod2 无荷载基线 Peaks.*.txt
├─ reorganized_dataset/              按 Excel 映射整理后的 CSV
└─ spatial_model/                    路面、传感器、荷载位置模型
```

## 3. 解调仪与通道对应关系

项目有两个解调仪，每个解调仪有 CH1–CH4 四个通道。Excel 是映射的权威来源：

| 解调仪 | 通道 | 传感器字符串 | 所在层 | 含义 |
|---|---|---|---|---|
| Demod1 | CH1 | SAL1 | 沥青层 | 纵向传感器 |
| Demod1 | CH2 | SAT1 | 沥青层 | 横向/另一条传感器 |
| Demod1 | CH3 | SSL1 | 土层 | 纵向传感器 |
| Demod1 | CH4 | SST | 土层 | 横向/另一条传感器 |
| Demod2 | CH1 | SAL2 | 沥青层 | 纵向传感器 |
| Demod2 | CH2 | SAT2 | 沥青层 | 横向/另一条传感器 |
| Demod2 | CH3 | SSL2 | 土层 | 纵向传感器 |
| Demod2 | CH4 | 温度传感器 | — | 温度通道，不作为结构传感器使用 |

一个通道不是一个点，而是一串 FBG 传感器点。整理后的 `sensor_id` 用 `D1_CH1_S1` 这类形式表示：`D1/D2` 是解调仪，`CH1–CH4` 是通道，`S1...` 是该通道中的第几个传感器点。

## 4. 无工况与有荷载数据

`raw_data/demo1无工况结果` 和 `raw_data/demo2无工况结果` 只有 `Peaks.*.txt`，表示没有施加任何荷载时各通道/各传感器点的自然波长记录。它们用于估计零荷载基线、噪声和跟踪质量，不应解释成某个荷载工况的响应。

`raw_data/Demod1` 与 `raw_data/Demod2` 是有荷载的原始 TXT。每个文件对应一个工况，文件头保留采集日期、采样设置、通道配置等信息，后面的时间行包含四个通道的传感器计数和波长值。

## 5. 三类荷载工况

1. **单点**：在一个坐标点施加荷载，例如 `10kg单点中心加载`、`40kg单点偏心加载`。
2. **双点**：在两个不同坐标点同时施加荷载。`对称`表示两个点关于中心线对称，`不对称`表示两个点不对称。
3. **纵中心线**：沿固定的纵向中心线选择一个 x 坐标加载；每次实验仍然只在一个坐标点施加荷载，不是同时加载一整条线。例如 `40kg纵中心线42.5cm加载` 表示 40 kg、纵中心线、x=42.5 cm 的单点加载。

整理后的数据包含 22 个有荷载工况，质量覆盖 5、10、20、25、30、35、40、50、60、70、80 kg。每个工况的荷载类型、荷载点坐标和加载时刻可在 `Reorganized_Load_Event_Table.csv` 与 `Reorganized_Response_Matrix.csv` 中查看。

## 6. 整理后 CSV 的用途

- `Reorganized_Sensor_Mapping.csv`：每个结构传感器点的通道、层位、方向、坐标和 `sensor_id`。
- `Reorganized_Load_Event_Table.csv`：每个工况的两个解调仪记录起始时间、时间偏移、采样率、荷载开始时刻和基线/加载窗口。
- `Reorganized_Response_Matrix.csv`：每个“工况 × 传感器点”一行的汇总响应，包括零荷载波长、加载初期/末期波长、波长变化量、荷载质量和荷载坐标。
- `NoLoad_Baseline.csv`：从无工况文件得到的每个传感器点基线和质量统计。
- `sensor_quality_weights_from_no_load_peaks.csv`：根据无工况噪声、漂移、跟踪情况计算的质量权重；权重越高通常表示该点越可靠。
- `film_dynamic_training_table.csv`：以相对时间展开的动态训练表。一行是一个“工况 × 传感器点 × 相对时间”的观测，适合时序/机器学习建模。
- `fixed_case_split_reorganized_mapping.csv`：固定的数据划分；5 个工况为 `fixed_test`，其余为 `development`，用于避免同一工况同时出现在训练和测试中。
- `manifest.json`、`film_dynamic_training_manifest.json`、`sensor_quality_weights_manifest.json`：生成规则和统计摘要。

## 7. 空间模型

`spatial_model/` 保存 MATLAB 图形文件、源代码和三个坐标表：

- `sensor_coordinates.csv`：每条传感器串的起止点、代表点、层位和类型。
- `all_fbg_points_coordinates.csv`：展开到每个 FBG 点的坐标表。
- `load_points_coordinates.csv`：中心单点、纵中心线位置、对称/不对称双点、偏心点等荷载位置。
- `model.m`：生成三维路面、传感器和荷载点的 MATLAB 脚本；坐标原点在路面顶面左下角，x 为长度方向（0–1.20 m），y 为宽度方向（0–0.50 m），z 向下为负。
- `2d.fig`、`3d.fig`：已经保存的 MATLAB 图形。

## 8. 推荐阅读顺序

先看本文件，再看 `mapping/demod对应关系.xlsx`；接着看 `reorganized_dataset/Reorganized_Sensor_Mapping.csv` 理解传感器点和坐标；然后用 `Reorganized_Load_Event_Table.csv`、`Reorganized_Response_Matrix.csv` 或 `film_dynamic_training_table.csv` 做分析；需要画空间关系时再使用 `spatial_model/`。

原始 TXT 保留在 `raw_data/`，用于追溯和重新解析。整理后的 CSV 是分析入口，不会改变原始采集文件。
