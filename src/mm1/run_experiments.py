"""Run the full M/M/1 experiment matrix from the TP configuration."""

from __future__ import annotations

import argparse
from pathlib import Path

from src.mm1.experiments import (
    load_experiment_config,
    run_experiments,
    write_experiment_outputs,
)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run all M/M/1 experiments.")
    parser.add_argument(
        "--config",
        default="config/default_parameters.json",
        help="Path to the JSON configuration file.",
    )
    parser.add_argument(
        "--output-dir",
        default="results/mm1/experiments",
        help="Directory where experiment CSV files will be written.",
    )
    args = parser.parse_args()

    config = load_experiment_config(Path(args.config))
    results = run_experiments(config)
    write_experiment_outputs(
        results,
        Path(args.output_dir),
        config.max_queue_probability_length,
    )

    experiment_count = (
        len(config.arrival_rate_factors)
        * len(config.queue_capacities)
        * config.replications
    )
    print("M/M/1 experiments completed")
    print(f"  experiment runs: {experiment_count}")
    print(f"  output directory: {args.output_dir}")
    print("  note: infinite queue cases with rho >= 1 are marked unstable")


if __name__ == "__main__":
    main()
