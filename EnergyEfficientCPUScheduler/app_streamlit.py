# app_streamlit.py

import streamlit as st
import matplotlib.pyplot as plt

from cpu_scheduler_core import (
    Process,
    simulate_fcfs,
    simulate_sjf,
    simulate_priority,
    simulate_rr,
    simulate_energy_efficient,
)

st.set_page_config(page_title="Energy-Efficient CPU Scheduling Simulator", layout="wide")

st.title("⚙️ Energy-Efficient CPU Scheduling Simulator")

st.markdown("""
This tool simulates classic CPU scheduling algorithms and a proposed **Energy-Efficient** scheduler.
You can compare performance metrics such as **waiting time, turnaround time, CPU utilization, and energy usage**.
""")

# Sidebar Inputs
st.sidebar.header("Simulation Settings")

algo = st.sidebar.selectbox(
    "Select Algorithm (for individual run)",
    [
        "FCFS",
        "SJF (Non-preemptive)",
        "Priority (Non-preemptive)",
        "Round Robin",
        "Energy-Efficient RR",
    ],
)

quantum = st.sidebar.number_input(
    "Time Quantum (for RR / EE-RR)",
    min_value=1,
    max_value=10,
    value=2,
)

st.sidebar.subheader("Processes Input")

arrivals_str = st.sidebar.text_input("Arrival times", "0,2,4,5")
bursts_str = st.sidebar.text_input("Burst times", "7,4,1,4")
priorities_str = st.sidebar.text_input("Priorities", "2,1,3,2")

run_button = st.sidebar.button("Run Selected Algorithm")
compare_button = st.sidebar.button("Compare All Algorithms")

def parse_list(text):
    return [int(x.strip()) for x in text.split(",")]

# MAIN LOGIC
if run_button or compare_button:
    arrivals = parse_list(arrivals_str)
    bursts = parse_list(bursts_str)
    priorities = parse_list(priorities_str)

    if len(arrivals) != len(bursts):
        st.error("Arrival and Burst count must match!")
        st.stop()
    if len(priorities) != len(arrivals):
        priorities = [1] * len(arrivals)

    processes = [
        Process(f"P{i+1}", arrivals[i], bursts[i], priorities[i])
        for i in range(len(arrivals))
    ]

# ================================
# INDIVIDUAL RUN MODE
# ================================
if run_button:
    if algo == "FCFS":
        result = simulate_fcfs(processes)
    elif algo == "SJF (Non-preemptive)":
        result = simulate_sjf(processes)
    elif algo == "Priority (Non-preemptive)":
        result = simulate_priority(processes)
    elif algo == "Round Robin":
        result = simulate_rr(processes, quantum=quantum)
    elif algo == "Energy-Efficient RR":
        result = simulate_energy_efficient(processes, quantum=quantum)

    st.subheader(f"🔧 Results for {result.algorithm}")

    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Avg Waiting Time", f"{result.avg_waiting_time:.2f}")
    col2.metric("Avg Turnaround Time", f"{result.avg_turnaround_time:.2f}")
    col3.metric("Avg Response Time", f"{result.avg_response_time:.2f}")
    col4.metric("CPU Utilization", f"{result.cpu_utilization:.2f}%")
    col5.metric("Total Energy", f"{result.total_energy:.2f} units")

    st.subheader("📍 Gantt Chart")
    fig, ax = plt.subplots(figsize=(10, 3))
    pids = sorted({e.pid for e in result.gantt if e.pid})
    pid_map = {p: i for i, p in enumerate(pids)}

    for entry in result.gantt:
        if entry.pid:
            ax.barh(pid_map[entry.pid], entry.end - entry.start, left=entry.start)
            ax.text((entry.start + entry.end) / 2, pid_map[entry.pid], entry.pid,
                    ha='center', va='center')

    ax.set_yticks(list(pid_map.values()))
    ax.set_yticklabels(pids)
    ax.set_xlabel("Time")
    ax.grid(True)
    st.pyplot(fig)

# ================================
# COMPARISON MODE
# ================================
if compare_button:
    results = [
        simulate_fcfs(processes),
        simulate_sjf(processes),
        simulate_priority(processes),
        simulate_rr(processes, quantum=quantum),
        simulate_energy_efficient(processes, quantum=quantum),
    ]

    st.subheader("📊 Algorithm Performance Comparison")

    # Build table
    data = {
        "Algorithm": [r.algorithm for r in results],
        "Avg Waiting Time": [round(r.avg_waiting_time, 2) for r in results],
        "Avg Turnaround Time": [round(r.avg_turnaround_time, 2) for r in results],
        "Avg Response Time": [round(r.avg_response_time, 2) for r in results],
        "CPU Utilization (%)": [round(r.cpu_utilization, 2) for r in results],
        "Total Energy": [round(r.total_energy, 2) for r in results],
    }
    st.table(data)

    # Identify winners
    best_turn = min(results, key=lambda r: r.avg_turnaround_time)
    best_energy = min(results, key=lambda r: r.total_energy)

    st.success(f"🏆 Fastest Algorithm (Min Turnaround Time): **{best_turn.algorithm}**")
    st.success(f"⚡ Most Energy Efficient: **{best_energy.algorithm}**")

    st.subheader("⚡ Energy Usage Comparison")
    fig, ax = plt.subplots()
    ax.bar([r.algorithm for r in results], [r.total_energy for r in results])
    ax.set_ylabel("Energy (units)")
    ax.set_xlabel("Algorithm")
    ax.set_title("Energy Consumption Comparison")
    st.pyplot(fig)
