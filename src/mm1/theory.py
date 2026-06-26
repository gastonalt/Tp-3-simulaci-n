"""Theoretical measures for M/M/1 and finite-capacity M/M/1/K queues."""

from __future__ import annotations

from math import isclose


def _validate_rates(arrival_rate: float, service_rate: float) -> None:
    if arrival_rate <= 0:
        raise ValueError("arrival_rate must be greater than zero")
    if service_rate <= 0:
        raise ValueError("service_rate must be greater than zero")


def mm1_infinite_theory(
    arrival_rate: float,
    service_rate: float,
    max_queue_length: int = 10,
) -> dict[str, object]:
    """Return steady-state metrics for an infinite M/M/1 queue.

    Metrics are only finite when rho < 1. For rho >= 1 the returned
    dictionary marks the model as unstable and leaves steady-state metrics as
    None, which is useful for the TP cases lambda = mu and lambda > mu.
    """

    _validate_rates(arrival_rate, service_rate)
    rho = arrival_rate / service_rate
    stable = rho < 1.0

    result: dict[str, object] = {
        "model": "M/M/1",
        "arrival_rate": arrival_rate,
        "service_rate": service_rate,
        "rho": rho,
        "stable": stable,
        "queue_capacity": None,
    }

    if not stable:
        result.update(
            {
                "average_number_in_system": None,
                "average_number_in_queue": None,
                "average_time_in_system": None,
                "average_time_in_queue": None,
                "server_utilization": None,
                "denial_probability": 0.0,
                "queue_length_probabilities": {},
            }
        )
        return result

    p0 = 1.0 - rho
    queue_length_probabilities = {
        0: p0 + p0 * rho,
    }
    for queue_length in range(1, max_queue_length + 1):
        queue_length_probabilities[queue_length] = p0 * rho ** (queue_length + 1)

    result.update(
        {
            "average_number_in_system": rho / (1.0 - rho),
            "average_number_in_queue": rho**2 / (1.0 - rho),
            "average_time_in_system": 1.0 / (service_rate - arrival_rate),
            "average_time_in_queue": arrival_rate
            / (service_rate * (service_rate - arrival_rate)),
            "server_utilization": rho,
            "denial_probability": 0.0,
            "queue_length_probabilities": queue_length_probabilities,
        }
    )
    return result


def mm1k_theory(
    arrival_rate: float,
    service_rate: float,
    queue_capacity: int,
) -> dict[str, object]:
    """Return steady-state metrics for M/M/1/K with finite waiting room.

    queue_capacity is the number of customers allowed to wait. The total
    system capacity is K = queue_capacity + 1 because one customer may be in
    service.
    """

    _validate_rates(arrival_rate, service_rate)
    if queue_capacity < 0:
        raise ValueError("queue_capacity must be zero or greater")

    total_capacity = queue_capacity + 1
    rho = arrival_rate / service_rate

    if isclose(rho, 1.0):
        state_probabilities = [
            1.0 / (total_capacity + 1) for _ in range(total_capacity + 1)
        ]
    else:
        p0 = (1.0 - rho) / (1.0 - rho ** (total_capacity + 1))
        state_probabilities = [
            p0 * rho**state for state in range(total_capacity + 1)
        ]

    denial_probability = state_probabilities[total_capacity]
    effective_arrival_rate = arrival_rate * (1.0 - denial_probability)
    average_number_in_system = sum(
        state * probability
        for state, probability in enumerate(state_probabilities)
    )
    average_number_in_queue = sum(
        max(state - 1, 0) * probability
        for state, probability in enumerate(state_probabilities)
    )

    if effective_arrival_rate > 0.0:
        average_time_in_system = average_number_in_system / effective_arrival_rate
        average_time_in_queue = average_number_in_queue / effective_arrival_rate
    else:
        average_time_in_system = None
        average_time_in_queue = None

    queue_length_probabilities = {
        0: state_probabilities[0] + state_probabilities[1],
    }
    for queue_length in range(1, queue_capacity + 1):
        queue_length_probabilities[queue_length] = state_probabilities[
            queue_length + 1
        ]

    return {
        "model": "M/M/1/K",
        "arrival_rate": arrival_rate,
        "service_rate": service_rate,
        "rho": rho,
        "stable": True,
        "queue_capacity": queue_capacity,
        "total_system_capacity": total_capacity,
        "state_probabilities": state_probabilities,
        "queue_length_probabilities": queue_length_probabilities,
        "denial_probability": denial_probability,
        "effective_arrival_rate": effective_arrival_rate,
        "average_number_in_system": average_number_in_system,
        "average_number_in_queue": average_number_in_queue,
        "average_time_in_system": average_time_in_system,
        "average_time_in_queue": average_time_in_queue,
        "server_utilization": 1.0 - state_probabilities[0],
    }
