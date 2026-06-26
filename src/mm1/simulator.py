"""Discrete-event simulator for M/M/1 queues."""

from __future__ import annotations

import csv
import math
import random
from collections import defaultdict, deque
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


@dataclass(frozen=True)
class MM1Parameters:
    arrival_rate: float
    service_rate: float
    simulation_time: float
    queue_capacity: int | None = None
    seed: int | None = None


@dataclass
class MM1Result:
    parameters: MM1Parameters
    total_arrivals: int
    accepted_arrivals: int
    rejected_arrivals: int
    completed_customers: int
    average_number_in_system: float
    average_number_in_queue: float
    average_time_in_system: float | None
    average_time_in_queue: float | None
    server_utilization: float
    denial_probability: float
    queue_length_time_probabilities: dict[int, float]
    time_series: list[dict[str, Any]]

    def metrics_row(self) -> dict[str, Any]:
        params = self.parameters
        return {
            "seed": params.seed,
            "arrival_rate": params.arrival_rate,
            "service_rate": params.service_rate,
            "rho": params.arrival_rate / params.service_rate,
            "simulation_time": params.simulation_time,
            "queue_capacity": (
                "infinite" if params.queue_capacity is None else params.queue_capacity
            ),
            "total_arrivals": self.total_arrivals,
            "accepted_arrivals": self.accepted_arrivals,
            "rejected_arrivals": self.rejected_arrivals,
            "completed_customers": self.completed_customers,
            "average_number_in_system": self.average_number_in_system,
            "average_number_in_queue": self.average_number_in_queue,
            "average_time_in_system": self.average_time_in_system,
            "average_time_in_queue": self.average_time_in_queue,
            "server_utilization": self.server_utilization,
            "denial_probability": self.denial_probability,
        }


def simulate_mm1(
    parameters: MM1Parameters,
    record_time_series: bool = True,
) -> MM1Result:
    """Simulate an M/M/1 queue for a fixed horizon."""

    _validate_parameters(parameters)

    rng = random.Random(parameters.seed)
    queue: deque[float] = deque()
    clock = 0.0
    next_arrival = rng.expovariate(parameters.arrival_rate)
    next_departure = math.inf

    server_busy = False
    current_customer_arrival: float | None = None
    current_service_start: float | None = None

    total_arrivals = 0
    accepted_arrivals = 0
    rejected_arrivals = 0
    completed_customers = 0

    area_number_in_system = 0.0
    area_number_in_queue = 0.0
    busy_time = 0.0
    queue_time_by_length: dict[int, float] = defaultdict(float)

    total_time_in_system = 0.0
    total_time_in_queue = 0.0
    time_series: list[dict[str, Any]] = []

    def snapshot(event: str) -> None:
        if not record_time_series:
            return
        queue_length = len(queue)
        time_series.append(
            {
                "time": clock,
                "event": event,
                "customers_in_system": queue_length + int(server_busy),
                "customers_in_queue": queue_length,
                "server_busy": int(server_busy),
                "total_arrivals": total_arrivals,
                "rejected_arrivals": rejected_arrivals,
                "completed_customers": completed_customers,
            }
        )

    def accumulate(until: float) -> None:
        nonlocal area_number_in_system
        nonlocal area_number_in_queue
        nonlocal busy_time
        nonlocal clock

        elapsed = until - clock
        if elapsed < -1e-12:
            raise RuntimeError("simulation clock moved backwards")
        if elapsed <= 0.0:
            clock = until
            return

        queue_length = len(queue)
        system_length = queue_length + int(server_busy)

        area_number_in_system += system_length * elapsed
        area_number_in_queue += queue_length * elapsed
        busy_time += int(server_busy) * elapsed
        queue_time_by_length[queue_length] += elapsed
        clock = until

    snapshot("start")

    while True:
        event_time = min(next_arrival, next_departure)
        if event_time > parameters.simulation_time:
            accumulate(parameters.simulation_time)
            break

        accumulate(event_time)

        if next_departure <= next_arrival:
            if current_customer_arrival is None or current_service_start is None:
                raise RuntimeError("departure scheduled with no customer in service")

            completed_customers += 1
            total_time_in_system += clock - current_customer_arrival
            total_time_in_queue += current_service_start - current_customer_arrival

            if queue:
                current_customer_arrival = queue.popleft()
                current_service_start = clock
                next_departure = clock + rng.expovariate(parameters.service_rate)
                server_busy = True
            else:
                current_customer_arrival = None
                current_service_start = None
                next_departure = math.inf
                server_busy = False

            snapshot("departure")
            continue

        total_arrivals += 1
        next_arrival = clock + rng.expovariate(parameters.arrival_rate)

        if not server_busy:
            accepted_arrivals += 1
            server_busy = True
            current_customer_arrival = clock
            current_service_start = clock
            next_departure = clock + rng.expovariate(parameters.service_rate)
            snapshot("arrival_service_start")
            continue

        if (
            parameters.queue_capacity is None
            or len(queue) < parameters.queue_capacity
        ):
            accepted_arrivals += 1
            queue.append(clock)
            snapshot("arrival_queue")
            continue

        rejected_arrivals += 1
        snapshot("arrival_rejected")

    average_time_in_system = (
        total_time_in_system / completed_customers
        if completed_customers > 0
        else None
    )
    average_time_in_queue = (
        total_time_in_queue / completed_customers
        if completed_customers > 0
        else None
    )

    return MM1Result(
        parameters=parameters,
        total_arrivals=total_arrivals,
        accepted_arrivals=accepted_arrivals,
        rejected_arrivals=rejected_arrivals,
        completed_customers=completed_customers,
        average_number_in_system=area_number_in_system
        / parameters.simulation_time,
        average_number_in_queue=area_number_in_queue
        / parameters.simulation_time,
        average_time_in_system=average_time_in_system,
        average_time_in_queue=average_time_in_queue,
        server_utilization=busy_time / parameters.simulation_time,
        denial_probability=(
            rejected_arrivals / total_arrivals if total_arrivals > 0 else 0.0
        ),
        queue_length_time_probabilities={
            queue_length: duration / parameters.simulation_time
            for queue_length, duration in sorted(queue_time_by_length.items())
        },
        time_series=time_series,
    )


def write_metrics_csv(results: Iterable[MM1Result], path: str | Path) -> None:
    rows = [result.metrics_row() for result in results]
    if not rows:
        return

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=list(rows[0].keys()),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def write_queue_probabilities_csv(
    results: Iterable[MM1Result],
    path: str | Path,
) -> None:
    rows: list[dict[str, Any]] = []
    for result in results:
        params = result.parameters
        for queue_length, probability in result.queue_length_time_probabilities.items():
            rows.append(
                {
                    "seed": params.seed,
                    "arrival_rate": params.arrival_rate,
                    "service_rate": params.service_rate,
                    "queue_capacity": (
                        "infinite"
                        if params.queue_capacity is None
                        else params.queue_capacity
                    ),
                    "queue_length": queue_length,
                    "probability": probability,
                }
            )

    if not rows:
        return

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=list(rows[0].keys()),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)


def write_time_series_csv(result: MM1Result, path: str | Path) -> None:
    if not result.time_series:
        return

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(
            csv_file,
            fieldnames=list(result.time_series[0].keys()),
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(result.time_series)


def _validate_parameters(parameters: MM1Parameters) -> None:
    if parameters.arrival_rate <= 0:
        raise ValueError("arrival_rate must be greater than zero")
    if parameters.service_rate <= 0:
        raise ValueError("service_rate must be greater than zero")
    if parameters.simulation_time <= 0:
        raise ValueError("simulation_time must be greater than zero")
    if parameters.queue_capacity is not None and parameters.queue_capacity < 0:
        raise ValueError("queue_capacity must be zero or greater")
