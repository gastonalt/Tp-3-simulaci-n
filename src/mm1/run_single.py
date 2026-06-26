"""Run one M/M/1 simulation using the default TP parameters."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from src.mm1.simulator import (
    MM1Parameters,
    simulate_mm1,
    write_metrics_csv,
    write_queue_probabilities_csv,
    write_time_series_csv,
)
from src.mm1.theory import mm1_infinite_theory, mm1k_theory


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a single M/M/1 simulation.")
    parser.add_argument(
        "--config",
        default="config/default_parameters.json",
        help="Path to the JSON configuration file.",
    )
    parser.add_argument(
        "--arrival-factor",
        type=float,
        default=0.75,
        help="Arrival rate as a factor of service rate.",
    )
    parser.add_argument(
        "--service-rate",
        type=float,
        default=None,
        help="Service rate. Defaults to the config value.",
    )
    parser.add_argument(
        "--simulation-time",
        type=float,
        default=None,
        help="Simulation horizon. Defaults to the config value.",
    )
    parser.add_argument(
        "--queue-capacity",
        default="infinite",
        help="Waiting room capacity: integer, 'infinite', 'inf', or 'none'.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Random seed. Defaults to the config base seed.",
    )
    parser.add_argument(
        "--output-dir",
        default="results/mm1",
        help="Directory where CSV outputs will be written.",
    )
    parser.add_argument(
        "--no-time-series",
        action="store_true",
        help="Skip event-level time series output.",
    )
    args = parser.parse_args()

    config = _load_config(Path(args.config))
    mm1_config = config["mm1"]

    service_rate = (
        args.service_rate
        if args.service_rate is not None
        else float(mm1_config["service_rate"])
    )
    simulation_time = (
        args.simulation_time
        if args.simulation_time is not None
        else float(mm1_config["simulation_time"])
    )
    seed = args.seed if args.seed is not None else int(mm1_config["base_seed"])
    queue_capacity = _parse_queue_capacity(args.queue_capacity)
    arrival_rate = service_rate * args.arrival_factor

    parameters = MM1Parameters(
        arrival_rate=arrival_rate,
        service_rate=service_rate,
        simulation_time=simulation_time,
        queue_capacity=queue_capacity,
        seed=seed,
    )
    result = simulate_mm1(
        parameters,
        record_time_series=not args.no_time_series,
    )

    output_dir = Path(args.output_dir)
    write_metrics_csv([result], output_dir / "mm1_single_metrics.csv")
    write_queue_probabilities_csv(
        [result],
        output_dir / "mm1_single_queue_probabilities.csv",
    )
    if not args.no_time_series:
        write_time_series_csv(result, output_dir / "mm1_single_timeseries.csv")

    theory = (
        mm1_infinite_theory(arrival_rate, service_rate)
        if queue_capacity is None
        else mm1k_theory(arrival_rate, service_rate, queue_capacity)
    )
    _print_summary(result.metrics_row(), theory)


def _load_config(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as config_file:
        return json.load(config_file)


def _parse_queue_capacity(raw_value: str) -> int | None:
    normalized = raw_value.strip().lower()
    if normalized in {"infinite", "inf", "none", "null"}:
        return None
    value = int(normalized)
    if value < 0:
        raise ValueError("queue capacity must be zero or greater")
    return value


def _print_summary(metrics: dict, theory: dict[str, object]) -> None:
    print("M/M/1 single run")
    print(f"  lambda: {metrics['arrival_rate']:.6g}")
    print(f"  mu: {metrics['service_rate']:.6g}")
    print(f"  rho: {metrics['rho']:.6g}")
    print(f"  queue capacity: {metrics['queue_capacity']}")
    print(f"  simulation time: {metrics['simulation_time']:.6g}")
    print(f"  seed: {metrics['seed']}")
    print("")
    print("Simulation metrics")
    print(f"  average number in system: {metrics['average_number_in_system']:.6g}")
    print(f"  average number in queue: {metrics['average_number_in_queue']:.6g}")
    print(f"  average time in system: {metrics['average_time_in_system']:.6g}")
    print(f"  average time in queue: {metrics['average_time_in_queue']:.6g}")
    print(f"  server utilization: {metrics['server_utilization']:.6g}")
    print(f"  denial probability: {metrics['denial_probability']:.6g}")
    print("")
    print("Theoretical reference")
    if not theory.get("stable", True):
        print("  no steady-state reference because rho >= 1")
        return
    print(f"  average number in system: {theory['average_number_in_system']:.6g}")
    print(f"  average number in queue: {theory['average_number_in_queue']:.6g}")
    print(f"  average time in system: {theory['average_time_in_system']:.6g}")
    print(f"  average time in queue: {theory['average_time_in_queue']:.6g}")
    print(f"  server utilization: {theory['server_utilization']:.6g}")
    print(f"  denial probability: {theory['denial_probability']:.6g}")


if __name__ == "__main__":
    main()
