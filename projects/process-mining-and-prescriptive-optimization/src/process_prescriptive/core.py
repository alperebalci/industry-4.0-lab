from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from itertools import product
from math import factorial
from random import Random
from statistics import mean
from typing import Iterable, Mapping


@dataclass(frozen=True)
class Event:
    case_id: str
    activity: str
    start_time: datetime
    end_time: datetime

    def __post_init__(self) -> None:
        if self.end_time < self.start_time:
            raise ValueError("event end_time cannot precede start_time")


@dataclass(frozen=True)
class ActivityStats:
    count: int
    mean_service_hours: float
    mean_observed_wait_hours: float
    arrival_rate_per_hour: float


@dataclass(frozen=True)
class ProcessSummary:
    direct_follows: Mapping[tuple[str, str], int]
    variants: Mapping[tuple[str, ...], int]
    activity_stats: Mapping[str, ActivityStats]
    cases: int


@dataclass(frozen=True)
class ResourcePlan:
    servers: Mapping[str, int]
    extra_servers: Mapping[str, int]
    expected_weighted_wait_hours: float


def _group_cases(events: Iterable[Event]) -> dict[str, list[Event]]:
    grouped: dict[str, list[Event]] = defaultdict(list)
    for event in events:
        grouped[event.case_id].append(event)
    for case_events in grouped.values():
        case_events.sort(key=lambda e: (e.start_time, e.end_time, e.activity))
    return dict(grouped)


def discover_process(events: Iterable[Event]) -> ProcessSummary:
    events = list(events)
    if not events:
        raise ValueError("event log is empty")

    grouped = _group_cases(events)
    direct_follows: Counter[tuple[str, str]] = Counter()
    variants: Counter[tuple[str, ...]] = Counter()
    service: dict[str, list[float]] = defaultdict(list)
    waits: dict[str, list[float]] = defaultdict(list)

    for case_events in grouped.values():
        variants[tuple(e.activity for e in case_events)] += 1
        previous_end = None
        for i, event in enumerate(case_events):
            service[event.activity].append(
                (event.end_time - event.start_time).total_seconds() / 3600.0
            )
            wait = 0.0
            if previous_end is not None:
                wait = max(
                    0.0,
                    (event.start_time - previous_end).total_seconds() / 3600.0,
                )
                direct_follows[(case_events[i - 1].activity, event.activity)] += 1
            waits[event.activity].append(wait)
            previous_end = event.end_time

    start = min(e.start_time for e in events)
    end = max(e.start_time for e in events)
    horizon_hours = max((end - start).total_seconds() / 3600.0, 1e-6)

    stats = {}
    for activity in sorted(service):
        stats[activity] = ActivityStats(
            count=len(service[activity]),
            mean_service_hours=mean(service[activity]),
            mean_observed_wait_hours=mean(waits[activity]),
            arrival_rate_per_hour=len(service[activity]) / horizon_hours,
        )

    return ProcessSummary(
        direct_follows=dict(direct_follows),
        variants=dict(variants),
        activity_stats=stats,
        cases=len(grouped),
    )


def _mmc_wait_hours(arrival_rate: float, service_rate: float, servers: int) -> float:
    """Expected queue wait for an M/M/c approximation (Erlang C)."""
    if servers < 1:
        raise ValueError("servers must be >= 1")
    if arrival_rate <= 0:
        return 0.0
    if service_rate <= 0:
        return float("inf")

    offered = arrival_rate / service_rate
    rho = arrival_rate / (servers * service_rate)
    if rho >= 1.0:
        return 1e6

    normalizer = sum(offered**n / factorial(n) for n in range(servers))
    tail = offered**servers / (factorial(servers) * (1.0 - rho))
    p0 = 1.0 / (normalizer + tail)
    p_wait = tail * p0
    return p_wait / (servers * service_rate - arrival_rate)


def _allocation_vectors(n: int, budget: int):
    for vector in product(range(budget + 1), repeat=n):
        if sum(vector) <= budget:
            yield vector


def optimize_resources(
    summary: ProcessSummary,
    current_servers: Mapping[str, int],
    budget: int,
    activity_weights: Mapping[str, float] | None = None,
) -> ResourcePlan:
    """Allocate a small integer server budget using an exact enumeration oracle."""
    if budget < 0:
        raise ValueError("budget must be non-negative")
    activities = sorted(summary.activity_stats)
    for activity in activities:
        if current_servers.get(activity, 0) < 1:
            raise ValueError(f"missing positive server count for {activity}")

    weights = activity_weights or {}
    best = None
    best_vector = None

    for vector in _allocation_vectors(len(activities), budget):
        objective = 0.0
        for activity, extra in zip(activities, vector):
            s = summary.activity_stats[activity]
            mu = 1.0 / max(s.mean_service_hours, 1e-9)
            wait = _mmc_wait_hours(
                s.arrival_rate_per_hour,
                mu,
                current_servers[activity] + extra,
            )
            weight = float(weights.get(activity, s.count))
            objective += weight * wait
        if best is None or objective < best:
            best = objective
            best_vector = vector

    assert best is not None and best_vector is not None
    extras = {a: int(x) for a, x in zip(activities, best_vector)}
    servers = {a: int(current_servers[a] + extras[a]) for a in activities}
    return ResourcePlan(
        servers=servers,
        extra_servers=extras,
        expected_weighted_wait_hours=float(best),
    )


def generate_synthetic_log(
    cases: int = 120,
    seed: int = 2026,
    interarrival_minutes: float = 8.0,
    servers: Mapping[str, int] | None = None,
) -> list[Event]:
    """Generate a reproducible order-to-ship event log with optional rework."""
    if cases < 1:
        raise ValueError("cases must be positive")
    rng = Random(seed)
    servers = dict(
        servers
        or {
            "Receive": 2,
            "Inspect": 1,
            "Rework": 1,
            "Pack": 1,
            "Ship": 2,
        }
    )
    means = {
        "Receive": 10.0,
        "Inspect": 18.0,
        "Rework": 24.0,
        "Pack": 16.0,
        "Ship": 8.0,
    }
    availability: dict[str, list[datetime]] = {}
    origin = datetime(2026, 1, 5, 8, 0, 0)
    for activity, count in servers.items():
        if count < 1:
            raise ValueError("all server counts must be positive")
        availability[activity] = [origin] * count

    events: list[Event] = []
    arrival = origin
    for case_number in range(cases):
        if case_number:
            arrival += timedelta(
                minutes=rng.expovariate(1.0 / interarrival_minutes)
            )
        route = ["Receive", "Inspect"]
        if rng.random() < 0.18:
            route.append("Rework")
        route.extend(["Pack", "Ship"])

        ready = arrival
        for activity in route:
            pool = availability[activity]
            idx = min(range(len(pool)), key=pool.__getitem__)
            start = max(ready, pool[idx])
            duration = rng.expovariate(1.0 / means[activity])
            end = start + timedelta(minutes=duration)
            pool[idx] = end
            events.append(
                Event(
                    case_id=f"CASE-{case_number:04d}",
                    activity=activity,
                    start_time=start,
                    end_time=end,
                )
            )
            ready = end
    return events


def mean_cycle_time_hours(events: Iterable[Event]) -> float:
    grouped = _group_cases(events)
    if not grouped:
        raise ValueError("event log is empty")
    values = []
    for case_events in grouped.values():
        start = min(e.start_time for e in case_events)
        end = max(e.end_time for e in case_events)
        values.append((end - start).total_seconds() / 3600.0)
    return mean(values)
