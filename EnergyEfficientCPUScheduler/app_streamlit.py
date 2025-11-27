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

st.set_page_config(page_title="Energy-Efficient CPU Scheduler", layout="wide")

st.title("⚙️ Energy-Efficient CPU Scheduling Simulator")

st.markdown("""
This tool simulates classic CPU scheduling algorithms and a proposed **Energy-Efficient** scheduler.
You can set processes, choose an algorithm, and compare **energy consumption** and performance metrics.
""")

# =========================
# Sidebar: Inputs
# =========================

st.sidebar.header("Simulation Settings")

algo = st.sidebar.selectbox(
    "Select Algorithm",
    [
        "FCFS",
        "SJF (Non-preemptive)",
        "Priority (Non-preemptive)",
        "Round Robin",
        "Energy-Efficient RR",
    ],
)

quantum = st.sidebar.number_input(
    "Time Quantum (for Round Robin based algorithms)",
    min_value=1,
    max_value=10,
    value=2,
)

st.sidebar.markdown("---")
st.sidebar.subheader("Processes Input")

default_arrivals = "0,2,4,5"
default_bursts = "7,4,1,4"
default_priorities = "2,1,3,2"

arrivals_str = st.sidebar.text_input("Arrival times (comma-separated)", default_arrivals)
bursts_str = st.sidebar.text_input("Burst times (comma-separated)", default_bursts)
priorities_str = st.sidebar.text_input("Priorities (for Priority algo, comma-separated)", default_priorities)

run_button = st.sidebar.button("Run Simulation")

# =========================
# Helper to parse input
# =========================

def parse_int_list(s: str):
    s = s.strip()
    if not s:
        return []
    return [int(x.strip()) for x in s.split(",") if x.strip()]

# =========================
# Main Logic
# =========================

if run_button:
    try:
        arrivals = parse_int_list(arrivals_str)
        bursts = parse_int_list(bursts_str)
        priorities = parse_int_list(priorities_str)

        if not (len(arrivals) == len(bursts)):
            st.error("Number of arrival times and burst times must be equal.")
        else:
            n = len(arrivals)
            if len(priorities) != n:
                # if priorities not matching, default all to 1
                priorities = [1] * n

            processes = [
                Process(f"P{i+1}", arrivals[i], bursts[i], priorities[i])
                for i in range(n)
            ]

            # Choose algorithm
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
            else:
                st.error("Unknown algorithm selected.")
                st.stop()

            # =========================
            # Show Metrics
            # =========================
            st.subheader(f"Results: {result.algorithm}")

            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Avg Waiting Time", f"{result.avg_waiting_time:.2f}")
            col2.metric("Avg Turnaround Time", f"{result.avg_turnaround_time:.2f}")
            col3.metric("Avg Response Time", f"{result.avg_response_time:.2f}")
            col4.metric("CPU Utilization", f"{result.cpu_utilization:.2f}%")
            col5.metric("Total Energy", f"{result.total_energy:.2f} units")

            # =========================
            # Gantt Chart
            # =========================
            st.subheader("Gantt Chart")

            # Map PIDs to y positions
            pids = sorted({e.pid for e in result.gantt if e.pid is not None})
            pid_to_y = {pid: i for i, pid in enumerate(pids)}

            fig, ax = plt.subplots(figsize=(10, 2 + len(pids) * 0.5))
            for entry in result.gantt:
                if entry.pid is None:
                    # Optional: show idle as separate line
                    continue
                y = pid_to_y[entry.pid]
                ax.barh(y, entry.end - entry.start, left=entry.start)
                ax.text(
                    (entry.start + entry.end) / 2,
                    y,
                    entry.pid,
                    va="center",
                    ha="center",
                )
            ax.set_yticks(list(pid_to_y.values()))
            ax.set_yticklabels(list(pid_to_y.keys()))
            ax.set_xlabel("Time")
            ax.set_ylabel("Process")
            ax.grid(True)

            st.pyplot(fig)

    except Exception as e:
        st.error(f"Error while running simulation: {e}")
else:
    st.info("Configure the processes and click **Run Simulation** from the sidebar.")
