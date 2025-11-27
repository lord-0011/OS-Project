# cpu_scheduler_core.py

from dataclasses import dataclass
from typing import List, Dict, Optional

# =========================
# Data Models
# =========================

@dataclass
class Process:
    pid: str
    arrival_time: int
    burst_time: int
    priority: int = 0  # lower number = higher priority

@dataclass
class GanttEntry:
    pid: Optional[str]  # None for idle
    start: int
    end: int
    freq_level: str  # 'low' / 'med' / 'high'

@dataclass
class SimulationResult:
    algorithm: str
    gantt: List[GanttEntry]
    avg_waiting_time: float
    avg_turnaround_time: float
    avg_response_time: float
    cpu_utilization: float
    total_energy: float


# =========================
# Energy Model
# =========================

# You can mention these values in your report
POWER_LEVELS: Dict[str, float] = {
    'low': 10.0,   # e.g., low frequency, low power
    'med': 18.0,   # medium
    'high': 30.0,  # high frequency, high power
}

def always_high_strategy(queue_len: int, time: int, algo: str) -> str:
    """Baseline strategy: always run at high frequency (more energy)."""
    return 'high'

def energy_aware_strategy(queue_len: int, time: int, algo: str) -> str:
    """
    Simple heuristic for energy-efficient scheduling:
    - Few processes waiting -> low frequency.
    - More load -> higher frequency.
    """
    if queue_len <= 2:
        return 'low'
    elif queue_len <= 5:
        return 'med'
    else:
        return 'high'


# =========================
# Metrics Computation
# =========================

def compute_metrics(processes: List[Process], gantt: List[GanttEntry], algo_name: str) -> SimulationResult:
    """
    Compute waiting time, turnaround time, response time,
    CPU utilization, and total energy from Gantt chart.
    """
    # Initialize per-process state
    state = {
        p.pid: {
            'arrival': p.arrival_time,
            'burst': p.burst_time,
            'start': None,
            'completion': None,
            'response': None,
        }
        for p in processes
    }

    # Infer start, completion, response times from Gantt chart
    for entry in gantt:
        if entry.pid is None:
            continue
        st = state[entry.pid]
        if st['start'] is None:
            st['start'] = entry.start
        # last end encountered is completion time
        st['completion'] = entry.end
        if st['response'] is None:
            st['response'] = entry.start

    n = len(processes)
    total_wait = total_turn = total_resp = 0.0

    for p in processes:
        st = state[p.pid]
        completion = st['completion']
        if completion is None:
            # Should not happen, but just in case
            continue
        turnaround = completion - p.arrival_time
        waiting = turnaround - p.burst_time
        response = (st['response'] - p.arrival_time) if st['response'] is not None else waiting
        total_wait += waiting
        total_turn += turnaround
        total_resp += response

    if gantt:
        start_time = gantt[0].start
        end_time = gantt[-1].end
    else:
        start_time = end_time = 0

    busy_time = sum(e.end - e.start for e in gantt if e.pid is not None)
    cpu_util = (busy_time / (end_time - start_time) * 100.0) if end_time > start_time else 0.0

    # Energy = Power * Time for each running segment
    total_energy = 0.0
    for e in gantt:
        if e.pid is None:
            continue
        duration = e.end - e.start
        total_energy += POWER_LEVELS[e.freq_level] * duration

    return SimulationResult(
        algorithm=algo_name,
        gantt=gantt,
        avg_waiting_time=total_wait / n if n else 0.0,
        avg_turnaround_time=total_turn / n if n else 0.0,
        avg_response_time=total_resp / n if n else 0.0,
        cpu_utilization=cpu_util,
        total_energy=total_energy,
    )


# =========================
# FCFS
# =========================

def simulate_fcfs(processes: List[Process], freq_strategy=always_high_strategy) -> SimulationResult:
    procs = sorted(processes, key=lambda p: p.arrival_time)
    time = procs[0].arrival_time if procs else 0
    gantt: List[GanttEntry] = []
    ready: List[Process] = []
    i = 0
    algo_name = "FCFS"

    while i < len(procs) or ready:
        # Add arrived processes to ready queue
        while i < len(procs) and procs[i].arrival_time <= time:
            ready.append(procs[i])
            i += 1

        if not ready:
            # CPU idle till next arrival
            next_arrival = procs[i].arrival_time
            gantt.append(GanttEntry(pid=None, start=time, end=next_arrival, freq_level='low'))
            time = next_arrival
            continue

        current = ready.pop(0)
        start = max(time, current.arrival_time)
        end = start + current.burst_time
        queue_len = len(ready) + 1  # including current
        freq = freq_strategy(queue_len, time, algo_name)
        gantt.append(GanttEntry(pid=current.pid, start=start, end=end, freq_level=freq))
        time = end

    return compute_metrics(processes, gantt, algo_name)


# =========================
# SJF (Non-preemptive)
# =========================

def simulate_sjf(processes: List[Process], freq_strategy=always_high_strategy) -> SimulationResult:
    procs = sorted(processes, key=lambda p: p.arrival_time)
    time = procs[0].arrival_time if procs else 0
    gantt: List[GanttEntry] = []
    ready: List[Process] = []
    i = 0
    algo_name = "SJF (Non-preemptive)"

    while i < len(procs) or ready:
        while i < len(procs) and procs[i].arrival_time <= time:
            ready.append(procs[i])
            i += 1

        if not ready:
            next_arrival = procs[i].arrival_time
            gantt.append(GanttEntry(pid=None, start=time, end=next_arrival, freq_level='low'))
            time = next_arrival
            continue

        # Choose shortest burst time
        ready.sort(key=lambda p: p.burst_time)
        current = ready.pop(0)
        start = max(time, current.arrival_time)
        end = start + current.burst_time
        queue_len = len(ready) + 1
        freq = freq_strategy(queue_len, time, algo_name)
        gantt.append(GanttEntry(pid=current.pid, start=start, end=end, freq_level=freq))
        time = end

    return compute_metrics(processes, gantt, algo_name)


# =========================
# Priority (Non-preemptive)
# =========================

def simulate_priority(processes: List[Process], freq_strategy=always_high_strategy) -> SimulationResult:
    # Lower priority value = higher priority
    procs = sorted(processes, key=lambda p: p.arrival_time)
    time = procs[0].arrival_time if procs else 0
    gantt: List[GanttEntry] = []
    ready: List[Process] = []
    i = 0
    algo_name = "Priority (Non-preemptive)"

    while i < len(procs) or ready:
        while i < len(procs) and procs[i].arrival_time <= time:
            ready.append(procs[i])
            i += 1

        if not ready:
            next_arrival = procs[i].arrival_time
            gantt.append(GanttEntry(pid=None, start=time, end=next_arrival, freq_level='low'))
            time = next_arrival
            continue

        # Choose highest priority (smallest priority number)
        ready.sort(key=lambda p: p.priority)
        current = ready.pop(0)
        start = max(time, current.arrival_time)
        end = start + current.burst_time
        queue_len = len(ready) + 1
        freq = freq_strategy(queue_len, time, algo_name)
        gantt.append(GanttEntry(pid=current.pid, start=start, end=end, freq_level=freq))
        time = end

    return compute_metrics(processes, gantt, algo_name)


# =========================
# Round Robin
# =========================

def simulate_rr(
    processes: List[Process],
    quantum: int = 2,
    freq_strategy=always_high_strategy,
    algo_name: str = "Round Robin"
) -> SimulationResult:
    remaining = {p.pid: p.burst_time for p in processes}
    procs_by_arrival = sorted(processes, key=lambda p: p.arrival_time)
    gantt: List[GanttEntry] = []
    time = procs_by_arrival[0].arrival_time if procs_by_arrival else 0
    ready: List[Process] = []
    i = 0
    completed = set()
    n_total = len(processes)

    while len(completed) < n_total:
        # Add arrivals up to current time
        while i < len(procs_by_arrival) and procs_by_arrival[i].arrival_time <= time:
            ready.append(procs_by_arrival[i])
            i += 1

        if not ready:
            if i < len(procs_by_arrival):
                next_arrival = procs_by_arrival[i].arrival_time
                gantt.append(GanttEntry(pid=None, start=time, end=next_arrival, freq_level='low'))
                time = next_arrival
                continue
            else:
                break  # no more processes
        current = ready.pop(0)
        pid = current.pid
        exec_time = min(quantum, remaining[pid])
        queue_len = len(ready) + 1
        freq = freq_strategy(queue_len, time, algo_name)
        start = time
        end = time + exec_time
        gantt.append(GanttEntry(pid=pid, start=start, end=end, freq_level=freq))
        remaining[pid] -= exec_time
        time = end

        # Add any new arrivals that came during this time slice
        while i < len(procs_by_arrival) and procs_by_arrival[i].arrival_time <= time:
            ready.append(procs_by_arrival[i])
            i += 1

        if remaining[pid] > 0:
            ready.append(current)
        else:
            completed.add(pid)

    return compute_metrics(processes, gantt, algo_name)


# =========================
# Energy-Efficient Algorithm (RR + dynamic frequency)
# =========================

def simulate_energy_efficient(processes: List[Process], quantum: int = 2) -> SimulationResult:
    """
    Proposed algorithm: Round Robin for fairness,
    but frequency selected by energy_aware_strategy (queue-based).
    """
    return simulate_rr(
        processes,
        quantum=quantum,
        freq_strategy=energy_aware_strategy,
        algo_name="Energy-Efficient RR"
    )


# =========================
# Simple CLI Demo (for testing)
# =========================

def run_cli_demo():
    demo_procs = [
        Process("P1", 0, 7, 2),
        Process("P2", 2, 4, 1),
        Process("P3", 4, 1, 3),
        Process("P4", 5, 4, 2),
    ]

    simulations = [
        simulate_fcfs(demo_procs),
        simulate_sjf(demo_procs),
        simulate_priority(demo_procs),
        simulate_rr(demo_procs, quantum=2),
        simulate_energy_efficient(demo_procs, quantum=2),
    ]

    for res in simulations:
        print(f"\n=== {res.algorithm} ===")
        print(f"Avg Waiting Time    : {res.avg_waiting_time:.2f}")
        print(f"Avg Turnaround Time : {res.avg_turnaround_time:.2f}")
        print(f"Avg Response Time   : {res.avg_response_time:.2f}")
        print(f"CPU Utilization     : {res.cpu_utilization:.2f}%")
        print(f"Total Energy        : {res.total_energy:.2f} units")

if __name__ == "__main__":
    run_cli_demo()
