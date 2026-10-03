from __future__ import annotations

import numpy as np
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score


def rng(seed: int) -> np.random.Generator:
    return np.random.default_rng(seed)


def safe_binary_metrics(y_true: np.ndarray, score: np.ndarray) -> dict[str, float]:
    return {
        "roc_auc": float(roc_auc_score(y_true, score)),
        "average_precision": float(average_precision_score(y_true, score)),
        "brier": float(brier_score_loss(y_true, np.clip(score, 0.0, 1.0))),
    }
