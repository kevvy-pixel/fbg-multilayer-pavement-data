"""Build a versioned, correctly mapped 0-load -> loaded FBG response dataset."""
from __future__ import annotations

import argparse
import itertools
import json
import shutil
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


SENSORS = [
    # demod, channel, sensor count, layer, direction, x coordinates, y coordinates, z
    ("Demod1", 1, 8, "Asphalt", "Longitudinal", np.arange(37, 73, 5), np.full(8, 18.0), -4.0, "SAL2-8FBGs"),
    ("Demod1", 2, 6, "Asphalt", "Transverse", np.full(6, 42.5), np.arange(12.5, 38, 5), -4.0, "SAT2-6FBGs"),
    ("Demod1", 3, 8, "Asphalt", "Longitudinal", np.arange(50, 86, 5), np.full(8, 25.0), -4.0, "SAL1-8FBGs"),
    ("Demod1", 4, 6, "Asphalt", "Transverse", np.full(6, 101.0), np.arange(8, 34, 5), -4.0, "SAT1-6FBGs"),
    ("Demod2", 1, 8, "Soil", "Longitudinal", np.arange(31.5, 67, 5), np.full(8, 25.0), -17.0, "SSL1-8FBGs"),
    ("Demod2", 2, 6, "Soil", "Transverse", np.full(6, 90.0), np.arange(8, 34, 5), -17.0, "SST-6FBGs"),
    ("Demod2", 3, 8, "Soil", "Longitudinal", np.arange(44.5, 80, 5), np.full(8, 19.5), -17.0, "SSL2-8FBGs"),
    ("Demod2", 4, 1, "Temperature", "Temperature", np.array([np.nan]), np.array([np.nan]), np.nan, "Temperature"),
]


def parse_enlight(path: Path):
    timestamps = []
    channels = [[] for _ in range(4)]
    with path.open("r", encoding="utf-8", errors="ignore") as handle:
        in_data = False
        for line in handle:
            if line.startswith("Timestamp\t"):
                in_data = True
                continue
            if not in_data:
                continue
            tokens = line.rstrip().split("\t")
            if len(tokens) < 6:
                continue
            try:
                stamp = datetime.strptime(tokens[0], "%Y/%m/%d %H:%M:%S.%f")
                counts = [int(tokens[index]) for index in range(1, 5)]
                values = np.asarray(tokens[5:], dtype=float)
            except (ValueError, TypeError):
                continue
            if values.size != sum(counts):
                continue
            timestamps.append(stamp)
            cursor = 0
            for channel, count in enumerate(counts):
                channels[channel].append(values[cursor : cursor + count])
                cursor += count
    if not timestamps:
        raise ValueError(f"No time samples parsed from {path}")
    seconds = np.asarray([(stamp - timestamps[0]).total_seconds() for stamp in timestamps])
    return timestamps, seconds, channels


def best_initial_subsequence(observed: np.ndarray, reference: np.ndarray) -> np.ndarray:
    best = None
    for indices in itertools.combinations(range(len(observed)), len(reference)):
        selected = observed[list(indices)]
        residual = selected - reference
        score = float(np.sum((residual - np.median(residual)) ** 2))
        if best is None or score < best[0]:
            best = (score, np.asarray(indices))
    return best[1]


def monotone_match(observed: np.ndarray, target: np.ndarray) -> np.ndarray:
    """Choose an ordered target-length subsequence nearest the previous tracked peaks."""
    n_target = len(target)
    n_obs = len(observed)
    if n_obs < n_target:
        output = np.full(n_target, np.nan)
        # Greedy fallback for rare missing-peak rows.
        available = list(range(n_obs))
        for index, value in enumerate(target):
            if not available:
                break
            nearest = min(available, key=lambda item: abs(observed[item] - value))
            if abs(observed[nearest] - value) < 0.35:
                output[index] = observed[nearest]
                available.remove(nearest)
        return output
    cost = np.full((n_target + 1, n_obs + 1), np.inf)
    take = np.zeros((n_target + 1, n_obs + 1), dtype=bool)
    cost[0, :] = 0
    for i in range(1, n_target + 1):
        for j in range(1, n_obs + 1):
            skip = cost[i, j - 1]
            use = cost[i - 1, j - 1] + (observed[j - 1] - target[i - 1]) ** 2
            if use <= skip:
                cost[i, j] = use
                take[i, j] = True
            else:
                cost[i, j] = skip
    indices = []
    i, j = n_target, n_obs
    while i > 0 and j > 0:
        if take[i, j]:
            indices.append(j - 1)
            i -= 1
            j -= 1
        else:
            j -= 1
    indices.reverse()
    return observed[indices]


def track_variable_channel(rows, reference):
    reference = np.asarray(reference, dtype=float)
    first_window = rows[: min(300, len(rows))]
    modal_count = pd.Series([len(row) for row in first_window]).mode().iloc[0]
    same = np.stack([row for row in first_window if len(row) == modal_count])
    typical = np.median(same, axis=0)
    initial_indices = best_initial_subsequence(typical, reference)
    target = typical[initial_indices]
    output = np.full((len(rows), len(reference)), np.nan)
    for row_index, row in enumerate(rows):
        matched = monotone_match(np.asarray(row), target)
        output[row_index] = matched
        valid = np.isfinite(matched) & (np.abs(matched - target) < 0.5)
        target[valid] = 0.98 * target[valid] + 0.02 * matched[valid]
    frame = pd.DataFrame(output).interpolate(limit=30, limit_direction="both")
    return frame.to_numpy(), int(modal_count), initial_indices.tolist()


def fixed_channel(rows, count):
    output = np.full((len(rows), count), np.nan)
    for index, row in enumerate(rows):
        use = min(count, len(row))
        output[index, :use] = row[:use]
    return pd.DataFrame(output).interpolate(limit=30, limit_direction="both").to_numpy()


def second_medians(seconds, values):
    bins = np.floor(seconds).astype(int)
    unique = np.unique(bins)
    time = np.asarray([np.median(seconds[bins == item]) for item in unique])
    data = np.asarray([np.nanmedian(values[bins == item], axis=0) for item in unique])
    return time, data


def detect_onset(seconds, asphalt):
    time, data = second_medians(seconds, asphalt)
    early = data[time < 180]
    noise = 1.4826 * np.nanmedian(np.abs(np.diff(early, axis=0) - np.nanmedian(np.diff(early, axis=0), axis=0)), axis=0)
    noise = np.maximum(noise, 2e-4)
    # Manual loading occurred near the middle of each ten-minute record, but
    # one verified slow setup starts around 360 s; retain a wider safe window.
    candidates = np.arange(240, 421)
    scores = []
    for candidate in candidates:
        before = np.nanmedian(data[(time >= candidate - 20) & (time <= candidate - 3)], axis=0)
        after = np.nanmedian(data[(time >= candidate + 3) & (time <= candidate + 20)], axis=0)
        standardized = np.abs(after - before) / noise
        finite = standardized[np.isfinite(standardized)]
        scores.append(np.mean(np.sort(finite)[-8:]) if finite.size >= 8 else np.nanmean(finite))
    best = int(np.nanargmax(scores))
    return float(candidates[best]), float(scores[best]), time, data


def signed_peak(values):
    min_value = np.nanmin(values, axis=0)
    max_value = np.nanmax(values, axis=0)
    return np.where(np.abs(min_value) > np.abs(max_value), min_value, max_value)


def load_metadata(case_id):
    import re

    match = re.search(r"(\d+)kg", case_id)
    load_kg = float(match.group(1)) if match else np.nan
    if "纵中心线" in case_id:
        load_type = "LongitudinalLine"
        cm = re.search(r"(\d+(?:\.\d+)?)cm", case_id)
        p1 = (float(cm.group(1)), 25.0) if cm else (np.nan, 25.0)
        p2 = (np.nan, np.nan)
    elif "双点对称" in case_id:
        load_type = "DualSymmetric"
        p1, p2 = (40.0, 25.0), (80.0, 25.0)
    elif "双点不对称" in case_id:
        load_type = "DualAsymmetric"
        p1, p2 = (40.0, 25.0), (90.0, 25.0)
    elif "偏心" in case_id:
        load_type = "SingleEccentric"
        p1, p2 = (60.0, 20.0), (np.nan, np.nan)
    else:
        load_type = "SingleCenter"
        p1, p2 = (60.0, 25.0), (np.nan, np.nan)
    return load_kg, load_type, *p1, *p2


def window_median(seconds, values, start, stop):
    mask = (seconds >= start) & (seconds <= stop)
    return np.nanmedian(values[mask], axis=0)


def process_case(root: Path, case_id: str, baseline_d2_ch1: np.ndarray):
    raw = {}
    diagnostics = {}
    start_times = {}
    for demod in ("Demod1", "Demod2"):
        stamps, seconds, channels = parse_enlight(root / demod / f"{case_id}.txt")
        start_times[demod] = stamps[0]
        matrices = []
        for channel in range(4):
            count = 1 if demod == "Demod2" and channel == 3 else (8, 6, 8, 6)[channel]
            if demod == "Demod2" and channel == 0:
                matrix, modal_count, initial_indices = track_variable_channel(channels[channel], baseline_d2_ch1)
                diagnostics["d2_ch1_modal_peak_count"] = modal_count
                diagnostics["d2_ch1_selected_initial_indices"] = ";".join(map(str, initial_indices))
            else:
                matrix = fixed_channel(channels[channel], count)
            matrices.append(matrix)
        raw[demod] = (seconds, matrices)

    d1_seconds, d1_channels = raw["Demod1"]
    asphalt = np.column_stack(d1_channels)
    onset, confidence, _, _ = detect_onset(d1_seconds, asphalt)
    duration = d1_seconds[-1]

    rows = []
    summaries = []
    for sensor_spec in SENSORS:
        demod, channel, count, layer, direction, xs, ys, z, sensor_string = sensor_spec
        seconds, matrices = raw[demod]
        values = matrices[channel - 1]
        # Within-run zero-load baseline and three loaded summaries.
        baseline = window_median(seconds, values, max(30, onset - 60), onset - 10)
        initial = window_median(seconds, values, onset + 15, onset + 60)
        final = window_median(seconds, values, duration - 60, duration - 10)
        time_1s, value_1s = second_medians(seconds, values)
        loaded = value_1s[(time_1s >= onset + 3) & (time_1s <= duration - 3)] - baseline
        peak = signed_peak(loaded)
        pre = values[(seconds >= max(30, onset - 60)) & (seconds <= onset - 10)]
        noise = np.nanstd(pre - np.nanmedian(pre, axis=0), axis=0)
        for sensor in range(count):
            sensor_id = f"D{1 if demod == 'Demod1' else 2}_CH{channel}_S{sensor + 1}"
            rows.append(
                {
                    "case_id": case_id,
                    "sensor_id": sensor_id,
                    "sensor_string": sensor_string,
                    "x_cm": xs[sensor],
                    "y_cm": ys[sensor],
                    "z_cm": z,
                    "layer": layer,
                    "direction": direction,
                    "channel": f"D{1 if demod == 'Demod1' else 2}_CH{channel}",
                    "interrogator": demod,
                    "zero_load_baseline_nm": baseline[sensor],
                    "loaded_initial_nm": initial[sensor],
                    "loaded_final_nm": final[sensor],
                    "delta_lambda_initial_nm": initial[sensor] - baseline[sensor],
                    "delta_lambda_final_nm": final[sensor] - baseline[sensor],
                    "delta_lambda_peak_signed_nm": peak[sensor],
                    "loaded_creep_change_nm": final[sensor] - initial[sensor],
                    "preload_noise_std_nm": noise[sensor],
                }
            )
    load_kg, load_type, p1_x, p1_y, p2_x, p2_y = load_metadata(case_id)
    for row in rows:
        row.update(
            {
                "load_kg": load_kg,
                "load_type": load_type,
                "p1_x": p1_x,
                "p1_y": p1_y,
                "p2_x": p2_x,
                "p2_y": p2_y,
                "load_onset_s": onset,
            }
        )
    event = {
        "case_id": case_id,
        "recording_start_demod1": start_times["Demod1"].isoformat(),
        "recording_start_demod2": start_times["Demod2"].isoformat(),
        "demod_start_offset_ms": (start_times["Demod2"] - start_times["Demod1"]).total_seconds() * 1000,
        "duration_s": duration,
        "sample_rate_hz": 1 / np.median(np.diff(d1_seconds)),
        "transition_type": "zero_load_to_loaded",
        "load_onset_s": onset,
        "onset_detection_score": confidence,
        "baseline_window_s": f"{max(30, onset - 60):.1f}-{onset - 10:.1f}",
        "loaded_initial_window_s": f"{onset + 15:.1f}-{onset + 60:.1f}",
        "loaded_final_window_s": f"{duration - 60:.1f}-{duration - 10:.1f}",
        **diagnostics,
    }
    return rows, event


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("data_repo", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    baseline = pd.read_csv(args.data_repo / "Unified_Baseline_Table_Demod2.csv")
    d2_ch1_ref = baseline[baseline.channel.eq("D2_CH1")].sort_values("sensor_id").UnifiedBaseline_nm.to_numpy()
    case_ids = sorted(path.stem for path in (args.data_repo / "Demod1").glob("*.txt"))
    all_rows = []
    events = []
    for case_index, case_id in enumerate(case_ids, 1):
        print(f"[{case_index:02d}/{len(case_ids):02d}] {case_id}", flush=True)
        rows, event = process_case(args.data_repo, case_id, d2_ch1_ref)
        all_rows.extend(rows)
        events.append(event)

    response = pd.DataFrame(all_rows)
    event_table = pd.DataFrame(events)
    baseline_quality = pd.concat(
        [
            pd.read_csv(args.data_repo / "Unified_Baseline_Table_Demod1.csv"),
            pd.read_csv(args.data_repo / "Unified_Baseline_Table_Demod2.csv"),
        ],
        ignore_index=True,
    )[["sensor_id", "QualityFlag", "NoiseStdMean_nm"]].rename(
        columns={
            "QualityFlag": "historical_baseline_quality",
            "NoiseStdMean_nm": "historical_noise_std_nm",
        }
    )
    response = response.merge(baseline_quality, on="sensor_id", how="left")
    response["analysis_quality"] = "OK"
    response.loc[
        response.historical_baseline_quality.ne("OK"), "analysis_quality"
    ] = "REVIEW_HISTORICAL_DRIFT"
    response.loc[
        response.preload_noise_std_nm.gt(0.05), "analysis_quality"
    ] = "EXCLUDE_HIGH_PRELOAD_NOISE"
    response.loc[response.layer.eq("Temperature"), "analysis_quality"] = "TEMPERATURE_REFERENCE"
    response.to_csv(args.output / "Corrected_Response_Matrix_Table_v2.csv", index=False, encoding="utf-8-sig")
    event_table.to_csv(args.output / "Corrected_Load_Event_Table_v2.csv", index=False, encoding="utf-8-sig")

    summary = (
        response.groupby(["case_id", "layer"])
        .agg(
            sensors=("sensor_id", "count"),
            max_abs_initial_nm=("delta_lambda_initial_nm", lambda x: np.max(np.abs(x))),
            max_abs_final_nm=("delta_lambda_final_nm", lambda x: np.max(np.abs(x))),
            max_abs_peak_nm=("delta_lambda_peak_signed_nm", lambda x: np.max(np.abs(x))),
            median_abs_creep_nm=("loaded_creep_change_nm", lambda x: np.median(np.abs(x))),
        )
        .reset_index()
    )
    summary.to_csv(args.output / "Corrected_Case_Layer_Summary_v2.csv", index=False, encoding="utf-8-sig")
    mapping = response.drop_duplicates("sensor_id")[["sensor_id", "sensor_string", "x_cm", "y_cm", "z_cm", "layer", "direction", "channel", "interrogator"]]
    mapping.to_csv(args.output / "Corrected_Sensor_Mapping_v2.csv", index=False, encoding="utf-8-sig")

    manifest = {
        "version": "CorrectedData_v2",
        "task": "零荷载到加载并持载；不包含卸载阶段",
        "cases": int(response.case_id.nunique()),
        "rows": int(len(response)),
        "asphalt_sensors_per_case": int((response[response.layer.eq("Asphalt")].groupby("case_id").size()).median()),
        "soil_sensors_per_case": int((response[response.layer.eq("Soil")].groupby("case_id").size()).median()),
        "temperature_sensors_per_case": int((response[response.layer.eq("Temperature")].groupby("case_id").size()).median()),
        "notes": [
            "Demod1 对应沥青层，共28个FBG。",
            "Demod2 对应土层，共22个FBG，D2_CH4为温度参考。",
            "所有波长变化都使用同次记录中检测到加载前的零荷载窗口作为基线。",
            "原始记录仅包含零荷载到加载并持载的过程，不能得到卸载后的残余沉降。",
            "加入边界或位移锚点假设后可重建相对位移；仅凭应变不能识别绝对沉降。",
        ],
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    source_script = Path(__file__).resolve()
    target_script = (args.output / "build_corrected_dataset_v2.py").resolve()
    if source_script != target_script:
        shutil.copy2(source_script, target_script)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
