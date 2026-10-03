from industry4_prototypes import (
    run_adhesive_benchmark,
    run_compressed_air_benchmark,
    run_material_batch_benchmark,
    run_screwdriving_benchmark,
)


def test_screwdriving_adds_signal_beyond_final_torque():
    m = run_screwdriving_benchmark()
    assert m["full_roc_auc"] > 0.70
    assert m["auc_gain_over_final_torque"] > 0.10


def test_adhesive_multivariate_detection_beats_pressure_only():
    m = run_adhesive_benchmark()
    assert (
        m["multivariate_average_precision"]
        > m["pressure_only_average_precision"]
    )


def test_material_batch_optimizer_reduces_predicted_deviation():
    m = run_material_batch_benchmark()
    assert m["future_batch_mae"] < 0.35
    assert m["predicted_reduction_fraction"] > 0.05


def test_compressed_air_detects_and_prioritizes_leaks():
    m = run_compressed_air_benchmark()
    assert m["zone_hour_precision"] > 0.70
    assert m["zone_hour_recall"] > 0.70
    assert m["top_ranked_zone_is_true_leaker"] == 1.0
