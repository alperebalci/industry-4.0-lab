from __future__ import annotations

import json

from process_prescriptive import (
    discover_process,
    generate_synthetic_log,
    mean_cycle_time_hours,
    optimize_resources,
)

current = {
    "Receive": 2,
    "Inspect": 1,
    "Rework": 1,
    "Pack": 1,
    "Ship": 2,
}

history = generate_synthetic_log(cases=180, seed=2026, servers=current)
summary = discover_process(history)
plan = optimize_resources(summary, current_servers=current, budget=2)

baseline_eval = generate_synthetic_log(cases=240, seed=99, servers=current)
optimized_eval = generate_synthetic_log(cases=240, seed=99, servers=plan.servers)

print(
    json.dumps(
        {
            "top_variants": [
                {"variant": list(v), "count": c}
                for v, c in sorted(
                    summary.variants.items(),
                    key=lambda item: item[1],
                    reverse=True,
                )[:5]
            ],
            "extra_servers": plan.extra_servers,
            "queueing_objective": plan.expected_weighted_wait_hours,
            "baseline_cycle_time_hours": mean_cycle_time_hours(baseline_eval),
            "optimized_cycle_time_hours": mean_cycle_time_hours(optimized_eval),
        },
        indent=2,
    )
)
