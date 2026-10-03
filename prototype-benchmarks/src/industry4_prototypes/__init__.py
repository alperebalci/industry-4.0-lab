"""Reproducible synthetic Industry 4.0 benchmark prototypes."""

from .adhesive import run_adhesive_benchmark
from .compressed_air import run_compressed_air_benchmark
from .material_batch import run_material_batch_benchmark
from .screwdriving import run_screwdriving_benchmark

__all__ = [
    "run_screwdriving_benchmark",
    "run_adhesive_benchmark",
    "run_material_batch_benchmark",
    "run_compressed_air_benchmark",
]
