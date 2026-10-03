from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error

from .common import rng

FEATURES = [
    "tensile_strength",
    "thickness",
    "hardness",
    "temperature_setpoint",
    "line_speed",
    "tool_age",
]


def make_material_batch_data(n_batches: int = 36, parts_per_batch: int = 80, seed: int = 19) -> pd.DataFrame:
    g = rng(seed)
    rows = []
    for batch in range(n_batches):
        tensile = 310 + g.normal(0, 18)
        thickness = 0.80 + g.normal(0, 0.022)
        hardness = 72 + g.normal(0, 3.5)
        batch_shift = (
            0.020 * (tensile - 310)
            - 1.8 * (thickness - 0.80)
            + 0.016 * (hardness - 72)
        )
        for part in range(parts_per_batch):
            temperature = 190 + g.normal(0, 4.0)
            speed = 1.0 + g.normal(0, 0.075)
            tool_age = (part / parts_per_batch) + 0.025 * batch
            quality = (
                batch_shift
                + 0.015 * (temperature - 190)
                - 0.55 * (speed - 1.0)
                + 0.18 * tool_age
                + 0.0008 * (temperature - 190) ** 2
                + g.normal(0, 0.16)
            )
            rows.append(
                {
                    "batch": batch,
                    "part": part,
                    "tensile_strength": tensile,
                    "thickness": thickness,
                    "hardness": hardness,
                    "temperature_setpoint": temperature,
                    "line_speed": speed,
                    "tool_age": tool_age,
                    "quality_deviation": quality,
                }
            )
    return pd.DataFrame(rows)


def run_material_batch_benchmark(seed: int = 19) -> dict[str, float]:
    df = make_material_batch_data(seed=seed)
    train = df[df["batch"] < 27]
    test = df[df["batch"] >= 27].copy()

    model = RandomForestRegressor(
        n_estimators=240,
        min_samples_leaf=5,
        random_state=seed,
    )
    model.fit(train[FEATURES], train["quality_deviation"])
    pred = model.predict(test[FEATURES])

    recommendations = []
    nominal_abs = []

    for _, group in test.groupby("batch"):
        context = group.iloc[0]
        tool_age = float(group["tool_age"].median())
        candidates = []

        for temp in np.linspace(182, 198, 17):
            for speed in np.linspace(0.88, 1.12, 13):
                row = pd.DataFrame(
                    [{
                        "tensile_strength": context["tensile_strength"],
                        "thickness": context["thickness"],
                        "hardness": context["hardness"],
                        "temperature_setpoint": temp,
                        "line_speed": speed,
                        "tool_age": tool_age,
                    }]
                )
                q = float(model.predict(row[FEATURES])[0])
                penalty = 0.015 * abs(temp - 190) + 0.30 * abs(speed - 1.0)
                candidates.append((abs(q) + penalty, q, temp, speed))

        _, q_rec, _, _ = min(candidates)
        recommendations.append(abs(q_rec))

        nominal_row = pd.DataFrame(
            [{
                "tensile_strength": context["tensile_strength"],
                "thickness": context["thickness"],
                "hardness": context["hardness"],
                "temperature_setpoint": 190.0,
                "line_speed": 1.0,
                "tool_age": tool_age,
            }]
        )
        nominal_abs.append(abs(float(model.predict(nominal_row[FEATURES])[0])))

    return {
        "future_batch_mae": float(mean_absolute_error(test["quality_deviation"], pred)),
        "future_batches": int(test["batch"].nunique()),
        "mean_predicted_abs_deviation_nominal": float(np.mean(nominal_abs)),
        "mean_predicted_abs_deviation_recommended": float(np.mean(recommendations)),
        "predicted_reduction_fraction": float(
            1 - np.mean(recommendations) / np.mean(nominal_abs)
        ),
    }
