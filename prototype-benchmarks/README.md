# Industry 4.0 Synthetic Prototype Benchmarks

Four runnable prototypes for manufacturing analytics problems that were identified as useful additions to the Industry 4.0 Lab but do not yet have a redistributable real-factory dataset in this repository.

They are intentionally labelled **synthetic prototypes**, not completed industrial case studies. Their purpose is to make the data contracts, leakage-safe validation logic, baselines, decision layers, and tests executable before real telemetry is available.

## Cases

| Case | Problem | Baseline | Prototype method | Split discipline |
|---|---|---|---|---|
| Screwdriving | Detect risky fastening cycles from torque-angle context | Final torque only | Random-forest defect risk from signature features | Future production lots |
| Adhesive dispensing | Detect bead/process anomalies | Pressure only | Multivariate Isolation Forest | Future material batches |
| Material batch adaptation | Adjust setpoints to incoming material variation | Fixed nominal recipe | Quality surrogate + constrained grid search | Future raw-material batches |
| Compressed air | Detect and prioritize leaks | Raw flow threshold concept | Contextual expected-demand models + residual ranking | Pre-leak training, future-time evaluation |

## Install

```bash
cd prototype-benchmarks
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Run

```bash
python -m industry4_prototypes all
python -m industry4_prototypes screwdriving
python -m industry4_prototypes adhesive
python -m industry4_prototypes material-batch
python -m industry4_prototypes compressed-air
```

## Test

```bash
pytest -q
```

## What each prototype demonstrates

### Adaptive screwdriving

The generator creates production lots with material shift and gradual tool wear. The defect mechanism depends on seating slope, rundown angle, snug torque, environment, and wear; final torque alone is intentionally weak. Evaluation holds out later lots, so cycles from the same lot are never scattered across train and test.

The code reports ROC AUC, average precision, Brier score, and the gain over a final-torque-only model.

### Adhesive dispensing anomaly detection

The synthetic process contains three anomaly modes: restriction, pulsation, and robot/path deviation. A pressure-only detector cannot reliably capture all three. The multivariate detector uses pressure, flow, material temperature, humidity, and path error while fitting only known-normal training beads.

The benchmark reports average precision against a future-batch holdout.

### Material-batch-aware setpoint adaptation

Incoming batches vary in tensile strength, thickness, and hardness. A random-forest quality surrogate is trained on earlier batches and evaluated on unseen future batches. A constrained grid search then proposes temperature and line-speed settings that reduce predicted absolute quality deviation while penalizing large movement away from the nominal recipe.

This is decision support only. With real production data, any setpoint recommendation would require engineering limits, designed experiments, and controlled validation before closed-loop use.

### Compressed-air leak prioritization

The synthetic plant has three zones with production-dependent demand and two future leaks. Expected air demand is learned only from an earlier healthy period. Persistent positive residuals are converted into zone-hour alarms and cumulative loss estimates for maintenance prioritization.

The benchmark reports precision, recall, and whether the highest-loss zone is a true leaker.

## Boundaries

- All measurements are generated; none are BSH or other proprietary factory data.
- Numerical benchmark scores are regression checks for the synthetic fixtures, not evidence of plant performance.
- Models are deliberately classical and inspectable. The main engineering point is data linkage, split design, baselines, and the decision layer.
- When a suitable real dataset is added, the synthetic generator should remain as a CI fixture while the headline benchmark moves to the real-data pipeline.
