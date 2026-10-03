from __future__ import annotations

import argparse
import json

from . import (
    run_adhesive_benchmark,
    run_compressed_air_benchmark,
    run_material_batch_benchmark,
    run_screwdriving_benchmark,
)

RUNNERS = {
    "screwdriving": run_screwdriving_benchmark,
    "adhesive": run_adhesive_benchmark,
    "material-batch": run_material_batch_benchmark,
    "compressed-air": run_compressed_air_benchmark,
}


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run synthetic Industry 4.0 benchmark prototypes."
    )
    parser.add_argument("case", choices=[*RUNNERS, "all"])
    parser.add_argument("--seed", type=int, default=None)
    args = parser.parse_args()

    if args.case == "all":
        out = {name: fn() for name, fn in RUNNERS.items()}
    else:
        fn = RUNNERS[args.case]
        out = fn() if args.seed is None else fn(seed=args.seed)

    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
