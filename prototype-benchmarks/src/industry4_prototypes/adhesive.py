from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.metrics import average_precision_score
from sklearn.preprocessing import StandardScaler

from .common import rng

FEATURES = [
    "pressure_mean",
    "pressure_std",
    "flow_mean",
    "flow_cv",
    "material_temp",
    "humidity",
    "path_error",
]


def make_adhesive_data(n_batches: int = 30, beads_per_batch: int = 90, seed: int = 11) -> pd.DataFrame:
    g = rng(seed)
    rows = []
    for batch in range(n_batches):
        viscosity = g.normal(0, 0.7)
        for bead in range(beads_per_batch):
            humidity = 42 + 0.55 * batch + g.normal(0, 5)
            material_temp = 24 + 0.07 * batch + g.normal(0, 0.8)
            anomaly = int(g.random() < (0.035 + 0.002 * max(batch - 15, 0)))
            mode = g.integers(0, 3) if anomaly else -1
            pressure_mean = 5.0 + 0.15 * viscosity + g.normal(0, 0.18)
            pressure_std = 0.12 + abs(g.normal(0, 0.025))
            flow_mean = 18.0 - 0.7 * viscosity + g.normal(0, 0.55)
            flow_cv = 0.035 + abs(g.normal(0, 0.009))
            path_error = abs(g.normal(0.16, 0.06))
            if mode == 0:
                pressure_mean += 0.7
                flow_mean -= 2.8
                pressure_std += 0.08
            elif mode == 1:
                pressure_std += 0.25
                flow_cv += 0.07
            elif mode == 2:
                path_error += 0.65
                flow_mean -= 0.7
            rows.append(
                {
                    "batch": batch,
                    "bead": bead,
                    "pressure_mean": pressure_mean,
                    "pressure_std": pressure_std,
                    "flow_mean": flow_mean,
                    "flow_cv": flow_cv,
                    "material_temp": material_temp,
                    "humidity": humidity,
                    "path_error": path_error,
                    "bond_failure": anomaly,
                }
            )
    return pd.DataFrame(rows)


def _iforest_score(train: pd.DataFrame, test: pd.DataFrame, cols: list[str], seed: int) -> np.ndarray:
    scaler = StandardScaler().fit(train[cols])
    model = IsolationForest(n_estimators=220, contamination=0.06, random_state=seed)
    model.fit(scaler.transform(train[cols]))
    return -model.score_samples(scaler.transform(test[cols]))


def run_adhesive_benchmark(seed: int = 11) -> dict[str, float]:
    df = make_adhesive_data(seed=seed)
    train = df[(df["batch"] < 20) & (df["bond_failure"] == 0)]
    test = df[df["batch"] >= 20]
    multi = _iforest_score(train, test, FEATURES, seed)
    pressure = _iforest_score(train, test, ["pressure_mean"], seed)
    y = test["bond_failure"].to_numpy()
    multi_ap = float(average_precision_score(y, multi))
    pressure_ap = float(average_precision_score(y, pressure))
    return {
        "test_beads": int(len(test)),
        "test_failure_rate": float(y.mean()),
        "multivariate_average_precision": multi_ap,
        "pressure_only_average_precision": pressure_ap,
        "ap_gain_over_pressure_only": multi_ap - pressure_ap,
    }
