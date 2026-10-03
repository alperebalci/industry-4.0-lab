from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import precision_score, recall_score

from .common import rng


def make_compressed_air_data(n_hours: int = 24 * 45, seed: int = 23) -> pd.DataFrame:
    g = rng(seed)
    rows = []
    leak_start = {"zone_a": 24 * 29, "zone_b": 24 * 35, "zone_c": 10**9}
    leak_size = {"zone_a": 7.0, "zone_b": 4.5, "zone_c": 0.0}

    for hour in range(n_hours):
        tod = hour % 24
        weekday = (hour // 24) % 7 < 5
        shift = int(weekday and 6 <= tod < 22)
        production = max(
            0.0,
            (65 if shift else 7) + 12 * np.sin(hour / 12) + g.normal(0, 7),
        )
        states = {
            "zone_a": int(g.random() < (0.82 if shift else 0.12)),
            "zone_b": int(g.random() < (0.68 if shift else 0.08)),
            "zone_c": int(g.random() < (0.55 if shift else 0.05)),
        }

        row = {"hour": hour, "shift": shift, "production": production}
        for i, zone in enumerate(["zone_a", "zone_b", "zone_c"]):
            expected = 8 + 0.19 * production + (18 - 2 * i) * states[zone]
            leak = leak_size[zone] if hour >= leak_start[zone] else 0.0
            row[f"{zone}_state"] = states[zone]
            row[f"{zone}_flow"] = expected + leak + g.normal(0, 1.8)
            row[f"{zone}_leak"] = int(leak > 0)
        rows.append(row)

    return pd.DataFrame(rows)


def run_compressed_air_benchmark(seed: int = 23) -> dict[str, float]:
    df = make_compressed_air_data(seed=seed)
    healthy = df[df["hour"] < 24 * 25]
    eval_df = df[df["hour"] >= 24 * 25].copy()

    all_true = []
    all_pred = []
    losses = {}

    for zone in ["zone_a", "zone_b", "zone_c"]:
        cols = ["shift", "production", f"{zone}_state"]
        model = RandomForestRegressor(
            n_estimators=180,
            min_samples_leaf=5,
            random_state=seed,
        )
        model.fit(healthy[cols], healthy[f"{zone}_flow"])

        train_residual = healthy[f"{zone}_flow"] - model.predict(healthy[cols])
        threshold = float(np.quantile(train_residual, 0.995))

        residual = eval_df[f"{zone}_flow"] - model.predict(eval_df[cols])
        predicted_leak = residual > threshold
        true_leak = eval_df[f"{zone}_leak"].astype(bool)

        all_true.extend(true_leak.tolist())
        all_pred.extend(predicted_leak.tolist())
        losses[zone] = float(np.clip(residual, 0, None).sum())

    ranked = sorted(losses, key=losses.get, reverse=True)

    return {
        "zone_hour_precision": float(
            precision_score(all_true, all_pred, zero_division=0)
        ),
        "zone_hour_recall": float(
            recall_score(all_true, all_pred, zero_division=0)
        ),
        "top_ranked_zone_is_true_leaker": float(
            ranked[0] in {"zone_a", "zone_b"}
        ),
        "estimated_loss_zone_a": losses["zone_a"],
        "estimated_loss_zone_b": losses["zone_b"],
        "estimated_loss_zone_c": losses["zone_c"],
    }
