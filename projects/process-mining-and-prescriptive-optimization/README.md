# Process Mining and Prescriptive Optimization

A vendor-neutral benchmark that connects **event-log process discovery** to an explicit **resource-allocation decision**.

The project is intentionally narrower than a commercial process-intelligence platform. Its purpose is to make the analytical chain inspectable:

```text
event log
  -> variants + directly-follows graph
  -> service/wait statistics
  -> queueing approximation
  -> integer resource intervention
  -> out-of-sample process simulation
```

## Why this project exists

Process-mining work often stops after finding bottlenecks. Operations research often starts from a cleaned mathematical model and hides how the candidate intervention was identified.

This project joins the two steps. The event log identifies process structure and operational load; a transparent prescriptive layer then allocates a small resource budget to activities.

## Event model

Each event contains:

```text
case_id
activity
start_time
end_time
```

`discover_process` computes:

- directly-follows counts;
- complete case variants;
- activity counts;
- mean service time;
- observed waiting time;
- empirical activity arrival rates.

The included generator creates a synthetic order-to-ship process with an optional rework branch:

```text
Receive -> Inspect -> [Rework] -> Pack -> Ship
```

## Prescriptive layer

For each activity, the historical event log supplies an estimated arrival rate and mean service time. The intervention model approximates each activity as an independent M/M/c queue using the Erlang-C waiting-time formula.

Given current server counts and an integer budget, `optimize_resources` enumerates all small feasible allocations and minimizes a weighted expected queue-wait objective.

This is an **exact enumeration oracle for the small intervention budget**, not a claim that the independent M/M/c approximation is an exact model of a real process.

## Validation

The example uses a held-out synthetic event stream with the same random seed for baseline and intervention scenarios. This common-random-number comparison isolates the effect of the resource allocation.

Run:

```bash
python -m pip install -e ".[dev]"
pytest
python examples/run_demo.py
```

The demo reports dominant variants, allocated extra servers, queueing-model objective, baseline cycle time and intervention cycle time.

## Scope and limitations

- The event log is synthetic and is not presented as evidence about a named factory or enterprise process.
- Queueing stations are optimized independently; blocking, batching, shared workers and skill matrices are omitted.
- The process-discovery layer is deliberately compact and does not attempt Petri-net conformance checking.
- The resource optimizer is appropriate for small budgets. Larger workforce problems should use MILP/CP/SAA formulations.
- A natural extension is to replace the synthetic log with a public BPI-style event log and add conformance diagnostics before intervention optimization.
