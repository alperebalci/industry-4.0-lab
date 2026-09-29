from process_prescriptive import (
    discover_process,
    generate_synthetic_log,
    mean_cycle_time_hours,
    optimize_resources,
)


def test_process_discovery_finds_main_and_rework_variants():
    log = generate_synthetic_log(cases=100, seed=4)
    summary = discover_process(log)
    assert summary.cases == 100
    assert ("Receive", "Inspect") in summary.direct_follows
    assert len(summary.variants) >= 2


def test_resource_optimizer_respects_budget_and_improves_queueing_objective():
    current = {"Receive": 2, "Inspect": 1, "Rework": 1, "Pack": 1, "Ship": 2}
    log = generate_synthetic_log(cases=180, seed=7, servers=current)
    summary = discover_process(log)

    baseline = optimize_resources(summary, current, budget=0)
    improved = optimize_resources(summary, current, budget=2)

    assert sum(improved.extra_servers.values()) <= 2
    assert improved.expected_weighted_wait_hours <= baseline.expected_weighted_wait_hours


def test_prescriptive_plan_improves_same_stream_cycle_time():
    current = {"Receive": 2, "Inspect": 1, "Rework": 1, "Pack": 1, "Ship": 2}
    history = generate_synthetic_log(cases=180, seed=11, servers=current)
    plan = optimize_resources(discover_process(history), current, budget=2)

    baseline = generate_synthetic_log(cases=220, seed=21, servers=current)
    changed = generate_synthetic_log(cases=220, seed=21, servers=plan.servers)
    assert mean_cycle_time_hours(changed) <= mean_cycle_time_hours(baseline)
