# 来源与整理规则

## 原始来源

- 原始有荷载/无荷载数据：`D:\matlab\guochuang\data数据`
- 路面三维位置模型：`D:\matlab\guochuang\路面3d位置模型（fbg位置+荷载位置）`
- 解调仪—通道—传感器对应关系：`C:\Users\27356\Music\Desktop\demod对应关系.xlsx`
- 已整合数据：`C:\Users\27356\Documents\Codex\2026-10-07\c-users-27356-documents-codex-2026\outputs\reorganized_dataset_excel_mapping`

## 本目录的整理原则

1. 原始 TXT、MATLAB 文件和 Excel 映射按原目录内容复制，未对源文件做改写。
2. `reorganized_dataset/` 保留已有整合结果，作为分析用的规范化表格层。
3. Excel 映射优先于文件名推断；通道含义以 `demod对应关系.xlsx` 为准。
4. 无工况数据只将 `Peaks.*.txt` 视为零荷载基线来源。
5. Demod2 CH4 的温度通道保留在映射和原始数据中，但动态结构传感器训练表标记为温度并排除在结构传感器统计之外。

## 可追溯性

`file_inventory.csv` 给出本数据集内每个文件的相对路径、大小和复制时的修改时间；`dataset_manifest.json` 给出主要文件数量和行数。若需要重新生成整理表，应从原始 TXT、Excel 映射和空间模型重新解析，而不是直接修改结果 CSV。
