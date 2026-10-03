# Industry 4.0 Project Candidates

This backlog contains **candidate** projects that complement the existing Industry 4.0 Lab without duplicating projects already marked `Ready`.

These are not presented as completed industrial case studies. A runnable synthetic implementation of all four candidates is available in [`prototype-benchmarks/`](prototype-benchmarks/). The synthetic suite validates software structure, split discipline, baselines, and decision logic; promotion into the main project map still requires a suitable real or redistributable industrial dataset and evidence at the physical run / lot / asset level.

No proprietary company data, process recipes, or confidential parameter values are assumed here.

## Selection criteria

A candidate is retained only when it adds a distinct industrial problem class and supports a defensible cyber-physical data pipeline:

- machine/process telemetry linked to a physical outcome;
- traceability across run, asset, batch, lot, tool, or assembly;
- a decision or intervention beyond pure prediction;
- evaluation that respects time, lot, machine, or session boundaries;
- a credible path from diagnosis to parameter adjustment, inspection, maintenance, or energy action.

## 1. Adaptive screwdriving from torque-angle signatures

**Prototype status.** Implemented and regression-tested in [`prototype-benchmarks/`](prototype-benchmarks/); synthetic fixture only.

**Problem.** Loose joints, stripped threads, cross-threading, missing seating, and material variation can produce different torque-angle-speed signatures even when the final torque value appears acceptable.

**Data contract.**

- per-cycle torque, angle, spindle speed, current, and timestamp series;
- controller program / recipe and fastener identifier;
- product, station, tool, bit, material, and batch traceability;
- ambient temperature where relevant;
- downstream audit torque, leak test, functional test, or rework outcome.

**Baseline.**

1. Engineer physically interpretable signature features: rundown angle, snug point, torque gradient, seating slope, peak torque, prevailing torque, and cycle duration.
2. Train a leakage-safe defect-risk model with splits by time and production lot.
3. Compare against controller threshold rules and final-torque-only baselines.

**Advanced extension.**

Use constrained contextual optimization to recommend torque / angle / speed windows for a material or part context while enforcing controller and process-engineering limits. Recommendations must remain advisory unless validated experimentally.

**Evaluation.**

- defect recall and precision at the assembly-cycle level;
- false-alarm rate per 1,000 cycles;
- calibration of predicted defect probability;
- rework / scrap reduction under a frozen decision threshold;
- parameter-policy feasibility rate.

**Promotion gate.** At least one dataset must contain full torque-angle curves plus an independent quality label; final torque alone is insufficient.

---

## 2. Adhesive dispensing anomaly detection with environmental context

**Prototype status.** Implemented and regression-tested in [`prototype-benchmarks/`](prototype-benchmarks/); synthetic fixture only.

**Problem.** Bead gaps, unstable flow, nozzle restriction, viscosity drift, robot-path deviations, and environmental changes can create weak or incomplete bonds that are not obvious from a single pressure threshold.

**Data contract.**

- nozzle pressure, flow, temperature, material temperature, dispense duration, and valve state;
- robot position / path metadata and line speed;
- adhesive batch and open-time / pot-life information where available;
- ambient temperature and humidity;
- downstream vision, leak, destructive-test, or bond-strength result.

**Baseline.**

1. Synchronize dispensing telemetry with each physical bead or part.
2. Detect multivariate anomalies using robust statistical and tree-based methods.
3. Quantify which signal families add value beyond pressure-only monitoring.

**Advanced extension.**

Build a sequence model or change-point detector for within-bead anomalies, then combine anomaly severity with environmental and material-batch variables for root-cause attribution.

**Evaluation.**

- event-level anomaly recall;
- detection delay within a dispense cycle;
- false alarms per production hour;
- performance by adhesive batch and environmental regime;
- incremental value over univariate pressure rules.

**Promotion gate.** The dataset must link telemetry to an independent bond-quality or downstream process outcome. Unlabeled synthetic traces alone do not qualify.

---

## 3. Raw-material batch shift to adaptive process setpoints

**Prototype status.** Implemented and regression-tested in [`prototype-benchmarks/`](prototype-benchmarks/); synthetic fixture only.

**Problem.** Steel coils, polymers, rubber compounds, coatings, and other incoming materials can vary by batch. A fixed machine recipe may therefore produce different quality outcomes even when nominal specifications are met.

**Data contract.**

- incoming material certificate or measured properties;
- supplier / batch / lot identifiers;
- machine recipe and actual process parameters;
- product geometry / variant and tool or mold identity;
- final dimensional, mechanical, surface, leak, or scrap outcome;
- time and line / machine identifiers.

**Baseline.**

1. Estimate between-batch and within-batch variation with hierarchical or mixed-effects models.
2. Train a quality model using material + process features.
3. Evaluate on future material batches, not random rows from the same batch.

**Advanced extension.**

Use constrained Bayesian optimization, contextual bandits, or robust optimization to propose a small safe adjustment to machine setpoints for a new material batch. Compare against a fixed nominal recipe and a process-engineer rule baseline.

**Evaluation.**

- future-batch prediction error or defect discrimination;
- worst-batch quality metric;
- reduction in out-of-spec production;
- magnitude and feasibility of recommended parameter changes;
- robustness under supplier or seasonal distribution shift.

**Promotion gate.** Material-lot traceability and process outcomes must coexist in the same dataset. A generic tabular quality dataset without batch identity is not sufficient.

---

## 4. Compressed-air leak detection and energy-loss prioritization

**Prototype status.** Implemented and regression-tested in [`prototype-benchmarks/`](prototype-benchmarks/); synthetic fixture only.

**Problem.** Compressed-air networks can lose substantial energy through leaks, but raw plant-level flow alone does not identify whether abnormal demand comes from leakage, legitimate machine operation, or schedule changes.

**Data contract.**

- header and branch pressure / flow telemetry;
- compressor power and operating state;
- machine or zone operating-state signals;
- production schedule or machine-cycle context;
- acoustic / ultrasonic observations if available;
- maintenance confirmation of leak location and repair time.

**Baseline.**

1. Build an operating-context model for expected air demand.
2. Detect persistent residual consumption during matched production states.
3. Rank suspected zones by estimated energy loss rather than anomaly score alone.

**Advanced extension.**

Combine network topology with change-point detection or probabilistic localization to infer likely leak zones. Add an intervention layer that prioritizes repairs by expected kWh loss, confidence, accessibility, and maintenance capacity.

**Evaluation.**

- confirmed-leak precision / recall;
- localization accuracy by zone;
- estimated versus measured post-repair energy reduction;
- detection delay;
- maintenance-priority value compared with first-in-first-out repair.

**Promotion gate.** The project should include machine-state or schedule context and at least some confirmed repair events; otherwise it risks confusing production demand with leakage.

## Ideas intentionally not promoted here

Several proposed directions already overlap strongly with current projects:

- compressor acoustic anomaly detection overlaps the existing multimodal motor condition-monitoring benchmark;
- CNC tool-wear prediction is already represented directly;
- generic laser / machining parameter optimization overlaps existing CNC process-quality work and closed-loop setpoint optimization;
- vision-only coating inspection is outside the repository's preferred scope unless images are tied to process telemetry and traceability.

Supply-chain forecasting, warehouse routing, and transport-packaging analytics are valid topics, but they fit the supply-chain / warehouse optimization repositories better than this lab.

## Promotion standard

A candidate becomes a `Ready` project only after it has:

1. a documented source and data license;
2. a reproducible raw-to-model pipeline;
3. physically meaningful train / validation / test boundaries;
4. at least one simple operational baseline;
5. model calibration or uncertainty analysis where decisions depend on scores;
6. an intervention, optimization, or monitoring policy tied to the prediction;
7. tests and deterministic experiment configuration;
8. a README that states both results and methodological limitations.
