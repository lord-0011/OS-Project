# ⚙️ Energy-Efficient CPU Scheduling Algorithm
### A DVFS-Aware Scheduling Approach for Mobile & Embedded Systems

This project implements an **Energy-Efficient CPU Scheduling Algorithm** designed to minimize power consumption **without compromising performance**, especially for **mobile and embedded devices** where battery life and thermal limits are critical.

The project includes simulation of classic CPU scheduling algorithms and a proposed **Dynamic DVFS-Aware Priority Round Robin (DDPRR)** algorithm. A Streamlit-based GUI is provided to visualize scheduling behavior, energy usage, and performance comparison.

---

## 🚀 Features

- Simulation of standard CPU schedulers:
  - **FCFS**
  - **SJF (Non-preemptive)**
  - **Priority (Non-preemptive)**
  - **Round Robin**
- **Proposed Energy-Efficient Algorithm**
  - DVFS-based dynamic frequency scaling (Low / Medium / High)
  - Adjusts CPU frequency based on system load and priority
  - Reduces energy consumption while maintaining turnaround & response time
- Real-time visualization:
  - Gantt chart execution timeline
  - Comparison tables for performance metrics
  - Energy usage bar chart
- GUI built using **Streamlit + Matplotlib**

---

## 🎯 Project Objective

To design a CPU scheduling algorithm that **reduces CPU energy usage** without significantly degrading performance metrics, enabling **power-efficient scheduling** suitable for **smartphones, IoT devices, wearables, and embedded systems**.

---

## 🧠 Real-World Relevance

Modern processors support **Dynamic Voltage and Frequency Scaling (DVFS)**. By adapting CPU frequency based on system workload, devices can:
- Save battery power when idle or lightly loaded
- Maintain performance when multiple or high-priority tasks run

This simulation models real OS power management behavior used in:
- Android & iOS schedulers
- ARM big.LITTLE architectures
- Wearable & IoT processors

---

## 🏗️ System Architecture
