"""Experiment orchestration and summaries for M/M/1 simulations."""

from __future__ import annotations

import json
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from src.common.csv_utils import write_rows_csv
from src.common.statistics import (
    confidence_interval_half_width,
    mean,
    percent_error,
    sample_stdev,
)
from src.mm1.simulator import MM1Parameters, MM1Result, simulate_mm1
from src.mm1.theory import mm1_infinite_theory, mm1k_theory

METRICS = [
    "average_number_in_system",
    "average_number_in_queue",
    "average_time_in_system",
    "average_time_in_queue",
    "server_utilization",
    "denial_probability",
]


@dataclass(frozen=True)
class ExperimentConfig:
    service_rate: float
    arrival_rate_factors: list[float]
    queue_capacities: list[int | None]
    simulation_time: float
    replications: int
    base_seed: int
    max_queue_probability_length: int


def load_experiment_config(path: str | Path) -> ExperimentConfig:
    with Path(path).open("r", encoding="utf-8") as config_file:
        config = json.load(config_file)["mm1"]

    return ExperimentConfig(
        service_rate=float(config["service_rate"]),
        arrival_rate_factors=[
            float(factor) for factor in config["arrival_rate_factors"]
        ],
        queue_capacities=config["queue_capacities"],
        simulation_time=float(config["simulation_time"]),
        replications=int(config["replications"]),
        base_seed=int(config["base_seed"]),
        max_queue_probability_length=int(
            config.get("max_queue_probability_length", 20)
        ),
    )


def run_experiments(config: ExperimentConfig) -> list[MM1Result]:
    results: list[MM1Result] = []
    for capacity_index, queue_capacity in enumerate(config.queue_capacities):
        for factor_index, arrival_factor in enumerate(config.arrival_rate_factors):
            arrival_rate = config.service_rate * arrival_factor
            for replication in range(config.replications):
                seed = _replication_seed(
                    config.base_seed,
                    capacity_index,
                    factor_index,
                    replication,
                )
                parameters = MM1Parameters(
                    arrival_rate=arrival_rate,
                    service_rate=config.service_rate,
                    simulation_time=config.simulation_time,
                    queue_capacity=queue_capacity,
                    seed=seed,
                )
                results.append(
                    simulate_mm1(parameters, record_time_series=False)
                )
    return results


def build_run_rows(results: list[MM1Result]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    replication_by_experiment: dict[tuple[float, str], int] = defaultdict(int)
    for result in results:
        row = result.metrics_row()
        key = (
            row["rho"],
            str(row["queue_capacity"]),
        )
        row["arrival_factor"] = row["rho"]
        row["queue_model"] = _queue_model(result.parameters.queue_capacity)
        row["replication"] = replication_by_experiment[key]
        row["theoretical_status"] = _theoretical_status(result.parameters)
        replication_by_experiment[key] += 1
        rows.append(row)
    return rows


def build_summary_rows(results: list[MM1Result]) -> tuple[
    list[dict[str, Any]],
    list[dict[str, Any]],
]:
    groups = _group_results(results)
    wide_rows: list[dict[str, Any]] = []
    long_rows: list[dict[str, Any]] = []

    for key, grouped_results in sorted(groups.items(), key=_group_sort_key):
        arrival_factor, queue_capacity_label = key
        params = grouped_results[0].parameters
        theory = theoretical_reference(params)
        theoretical_status = _theoretical_status(params)

        base_row: dict[str, Any] = {
            "arrival_factor": arrival_factor,
            "arrival_rate": params.arrival_rate,
            "service_rate": params.service_rate,
            "rho": params.arrival_rate / params.service_rate,
            "queue_capacity": queue_capacity_label,
            "queue_model": _queue_model(params.queue_capacity),
            "simulation_time": params.simulation_time,
            "replications": len(grouped_results),
            "theoretical_status": theoretical_status,
        }
        wide_row = dict(base_row)

        for metric in METRICS:
            values = [
                getattr(result, metric)
                for result in grouped_results
                if getattr(result, metric) is not None
            ]
            metric_mean = mean(values)
            metric_stdev = sample_stdev(values)
            metric_ci = confidence_interval_half_width(values)
            theory_value = theory.get(metric)
            metric_error = percent_error(
                metric_mean,
                theory_value if isinstance(theory_value, float) else None,
            )

            wide_row[f"{metric}_mean"] = metric_mean
            wide_row[f"{metric}_stdev"] = metric_stdev
            wide_row[f"{metric}_ci95_half_width"] = metric_ci
            wide_row[f"{metric}_theory"] = theory_value
            wide_row[f"{metric}_error_percent"] = metric_error

            long_row = dict(base_row)
            long_row.update(
                {
                    "metric": metric,
                    "mean": metric_mean,
                    "stdev": metric_stdev,
                    "ci95_half_width": metric_ci,
                    "theory": theory_value,
                    "error_percent": metric_error,
                }
            )
            long_rows.append(long_row)

        wide_rows.append(wide_row)

    return wide_rows, long_rows


def build_queue_probability_rows(
    results: list[MM1Result],
    max_queue_length: int,
) -> list[dict[str, Any]]:
    groups = _group_results(results)
    rows: list[dict[str, Any]] = []

    for key, grouped_results in sorted(groups.items(), key=_group_sort_key):
        arrival_factor, queue_capacity_label = key
        params = grouped_results[0].parameters
        theory = theoretical_reference(params)
        theory_probabilities = theory.get("queue_length_probabilities") or {}

        queue_lengths = range(0, max_queue_length + 1)
        for queue_length in queue_lengths:
            values = [
                result.queue_length_time_probabilities.get(queue_length, 0.0)
                for result in grouped_results
            ]
            probability_mean = mean(values)
            theory_value = (
                theory_probabilities.get(queue_length)
                if isinstance(theory_probabilities, dict)
                else None
            )
            rows.append(
                {
                    "arrival_factor": arrival_factor,
                    "arrival_rate": params.arrival_rate,
                    "service_rate": params.service_rate,
                    "rho": params.arrival_rate / params.service_rate,
                    "queue_capacity": queue_capacity_label,
                    "queue_model": _queue_model(params.queue_capacity),
                    "queue_length": queue_length,
                    "mean_probability": probability_mean,
                    "stdev": sample_stdev(values),
                    "ci95_half_width": confidence_interval_half_width(values),
                    "theory": theory_value,
                    "error_percent": percent_error(
                        probability_mean,
                        theory_value
                        if isinstance(theory_value, float)
                        else None,
                    ),
                    "theoretical_status": _theoretical_status(params),
                }
            )

        tail_values = [
            sum(
                probability
                for queue_length, probability
                in result.queue_length_time_probabilities.items()
                if queue_length > max_queue_length
            )
            for result in grouped_results
        ]
        rows.append(
            {
                "arrival_factor": arrival_factor,
                "arrival_rate": params.arrival_rate,
                "service_rate": params.service_rate,
                "rho": params.arrival_rate / params.service_rate,
                "queue_capacity": queue_capacity_label,
                "queue_model": _queue_model(params.queue_capacity),
                "queue_length": f">{max_queue_length}",
                "mean_probability": mean(tail_values),
                "stdev": sample_stdev(tail_values),
                "ci95_half_width": confidence_interval_half_width(tail_values),
                "theory": None,
                "error_percent": None,
                "theoretical_status": _theoretical_status(params),
            }
        )

    return rows


def theoretical_reference(parameters: MM1Parameters) -> dict[str, Any]:
    if parameters.queue_capacity is None:
        return mm1_infinite_theory(
            parameters.arrival_rate,
            parameters.service_rate,
        )
    return mm1k_theory(
        parameters.arrival_rate,
        parameters.service_rate,
        parameters.queue_capacity,
    )


def write_experiment_outputs(
    results: list[MM1Result],
    output_dir: str | Path,
    max_queue_probability_length: int,
) -> None:
    output_path = Path(output_dir)
    wide_rows, long_rows = build_summary_rows(results)
    write_rows_csv(build_run_rows(results), output_path / "mm1_runs.csv")
    write_rows_csv(wide_rows, output_path / "mm1_summary.csv")
    write_rows_csv(long_rows, output_path / "mm1_summary_long.csv")
    write_rows_csv(
        build_queue_probability_rows(results, max_queue_probability_length),
        output_path / "mm1_queue_probabilities.csv",
    )


def _group_results(
    results: list[MM1Result],
) -> dict[tuple[float, str], list[MM1Result]]:
    groups: dict[tuple[float, str], list[MM1Result]] = defaultdict(list)
    for result in results:
        params = result.parameters
        key = (
            params.arrival_rate / params.service_rate,
            _queue_capacity_label(params.queue_capacity),
        )
        groups[key].append(result)
    return groups


def _group_sort_key(
    item: tuple[tuple[float, str], list[MM1Result]],
) -> tuple[float, int]:
    (arrival_factor, queue_capacity_label), _ = item
    if queue_capacity_label == "infinite":
        return arrival_factor, -1
    return arrival_factor, int(queue_capacity_label)


def _queue_capacity_label(queue_capacity: int | None) -> str:
    return "infinite" if queue_capacity is None else str(queue_capacity)


def _queue_model(queue_capacity: int | None) -> str:
    return "M/M/1" if queue_capacity is None else "M/M/1/K"


def _theoretical_status(parameters: MM1Parameters) -> str:
    if parameters.queue_capacity is not None:
        return "finite_capacity_steady_state"
    if parameters.arrival_rate < parameters.service_rate:
        return "infinite_capacity_steady_state"
    return "infinite_capacity_unstable_no_steady_state"


def _replication_seed(
    base_seed: int,
    capacity_index: int,
    factor_index: int,
    replication: int,
) -> int:
    return base_seed + capacity_index * 10000 + factor_index * 100 + replication
