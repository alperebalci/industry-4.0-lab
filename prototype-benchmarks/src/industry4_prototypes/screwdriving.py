from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

from .common import rng, safe_binary_metrics

FEATURES = [
    "final_torque",
    "rundown_angle",
    "snug_torque",
    "seating_slope",
    "cycle_time",
    "speed_mean",
    "current_peak",
    "ambient_temp",
]


def make_screwdriving_data(n_lots: int = 24, cycles_per_lot: int = 140, seed: int = 7) -> pd.DataFrame:
    g = rng(seed)
    rows = []
    for lot in range(n_lots):
        material_shift = g.normal(0, 0.35)
        tool_wear = max(0.0, (lot - 8) / n_lots) + g.normal(0, 0.03)
        for cycle in range(cycles_per_lot):
            ambient = 21 + 0.18 * lot + g.normal(0, 1.1)
            rundown = 410 + 18 * material_shift + g.normal(0, 15)
            snug = 1.8 + 0.12 * material_shift + g.normal(0, 0.08)
            slope = 0.085 - 0.018 * tool_wear - 0.006 * material_shift + g.normal(0, 0.0045)
            final_torque = 5.4 + 0.08 * material_shift + g.normal(0, 0.18)
            speed = 520 - 16 * material_shift + g.normal(0, 24)
            current_peak = 3.6 + 0.25 * tool_wear + 0.11 * material_shift + g.normal(0, 0.18)
            cycle_time = 1.15 + 0.05 * material_shift + 0.08 * tool_wear + g.normal(0, 0.06)
            latent = (
                -4.2
                + 1.25 * (abs(rundown - 410) / 15.0)
                + 2.6 * max(0.0, (0.080 - slope) / 0.008)
                + 1.10 * (abs(snug - 1.8) / 0.10)
                + 0.9 * tool_wear
                + 0.12 * abs(ambient - 24)
            )
            p = 1 / (1 + np.exp(-latent))
            defect = int(g.random() < p)
            rows.append(
                {
                    "lot": lot,
                    "cycle": cycle,
                    "final_torque": final_torque,
                    "rundown_angle": rundown,
                    "snug_torque": snug,
                    "seating_slope": slope,
                    "cycle_time": cycle_time,
                    "speed_mean": speed,
                    "current_peak": current_peak,
                    "ambient_temp": ambient,
                    "defect": defect,
                }
            )
    return pd.DataFrame(rows)


def run_screwdriving_benchmark(seed: int = 7) -> dict[str, float]:
    df = make_screwdriving_data(seed=seed)
    split_lot = int(df["lot"].max() * 0.72)
    train = df[df["lot"] <= split_lot]
    test = df[df["lot"] > split_lot]

    full = RandomForestClassifier(
        n_estimators=220, min_samples_leaf=8, class_weight="balanced", random_state=seed
    )
    torque_only = RandomForestClassifier(
        n_estimators=160, min_samples_leaf=8, class_weight="balanced", random_state=seed
    )
    full.fit(train[FEATURES], train["defect"])
    torque_only.fit(train[["final_torque"]], train["defect"])

    full_score = full.predict_proba(test[FEATURES])[:, 1]
    torque_score = torque_only.predict_proba(test[["final_torque"]])[:, 1]
    m = safe_binary_metrics(test["defect"].to_numpy(), full_score)
    base = safe_binary_metrics(test["defect"].to_numpy(), torque_score)
    return {
        "test_cycles": int(len(test)),
        "test_defect_rate": float(test["defect"].mean()),
        "full_roc_auc": m["roc_auc"],
        "full_average_precision": m["average_precision"],
        "full_brier": m["brier"],
        "torque_only_roc_auc": base["roc_auc"],
        "auc_gain_over_final_torque": m["roc_auc"] - base["roc_auc"],
    }
