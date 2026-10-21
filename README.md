# Physical Validity Metric for Imputed Vehicle State in CACC Mixed Traffic

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status: Objective 1 Complete](https://img.shields.io/badge/Status-Objective%201%20Verified-brightgreen.svg)]()

This repository implements and validates a physical-validity metric—**Infeasible Rate (IR)**—for reconstructed Connected Autonomous Vehicle (CAV) trajectories in mixed autonomy Cooperative Adaptive Cruise Control (CACC) traffic.

---

## Table of Contents
- [Project Overview](#project-overview)
- [Repository Structure](#repository-structure)
- [Objective 1: Infeasible Rate (IR) Metric](#objective-1-infeasible-rate-ir-metric)
- [Consolidated Results (Table 3)](#consolidated-results-table-3)
- [How to Run the Project](#how-to-run-the-project)
- [File Descriptions](#file-descriptions)
- [Team (Group 7)](#team-group-7)

---

## Project Overview

In mixed-autonomy highway traffic, Connected Autonomous Vehicles (CAVs) exchange motion telemetry (speed, acceleration, coordinates) at $10\text{ Hz}$ ($\Delta t = 0.1\text{ s}$). Existing imputation algorithms reconstruct missing values arising from:
1. **Structural Feature Missingness (SFM):** Uninstrumented human-driven vehicles (HDVs) lacking V2X transmitters.
2. **Temporal Cluster Missingness (TCM):** Burst packet dropouts ($2-5$ steps) in CAV wireless channels.

### The Research Gap
Standard benchmarks evaluate trajectory reconstruction purely via **Average Displacement Error (ADE)**. An imputation model can achieve a low ADE while generating trajectories that violate vehicle kinematics (e.g., accelerations exceeding $\pm 24\text{ m/s}^2$ or turning radii below $6\text{ m}$). **Objective 1** introduces **Infeasible Rate (IR)** to quantify and penalize physically impossible motion.

For the full theoretical derivations and engineering analysis, see [PROJECT_REPORT.md](PROJECT_REPORT.md).

---

## Repository Structure

```text
cloudProject/
├── Objective_1_Infeasible_Rate.ipynb          # Main execution notebook (step-by-step evaluation)
├── PROJECT_REPORT.md                          # In-depth technical engineering & research report
├── README.md                                  # Repository landing page and setup guide
│
├── objective_1_results.xlsx                   # Auto-formatted Excel report (auto-fitted columns)
├── objective_1_summary_table.csv              # Summary results across 3 conditions (Mean ± 95% CI)
├── objective_1_all_seeds_detailed.csv         # Detailed run-by-run results across all 60 seeds
│
├── ir_comparison_across_conditions.png        # Bar chart comparing GT vs Ch1 vs Fully Imputed IR
├── acceleration_and_curvature_distributions.png# Histograms of acceleration & curvature violations
├── sample_trajectory_comparison.png           # 2D path plot comparing Ground Truth vs Imputed
│
├── data_corrupted/                            # Corrupted & pre-imputed dataset from pipeline
│   ├── penetration_10/                        # 20 simulation seeds at 10% CAV penetration
│   ├── penetration_20/                        # 20 simulation seeds at 20% CAV penetration
│   └── penetration_30/                        # 20 simulation seeds at 30% CAV penetration
│
├── highD-dataset-v1.0/                        # Supplementary real-world highway validation data
├── AboutProject.pdf                           # Official project problem statement & constraints
└── IoV_Imputation_Implementation_Plan.pdf     # Reference dual-channel implementation plan
```

---

## Objective 1: Infeasible Rate (IR) Metric

A trajectory window ($30$ steps $= 3.0\text{ s}$) is classified as **Infeasible** if any step violates either authoritative constraint:
1. **Acceleration Limit:** Acceleration falls outside $[-8.0, +3.0]\text{ m/s}^2$:
   $$v_t = \frac{\sqrt{\Delta x_t^2 + \Delta y_t^2}}{0.1}, \quad a_t = \frac{v_{t+1} - v_t}{0.1}$$
2. **Curvature / Turning Radius Limit:** Turning radius drops below $6.0\text{ m}$ ($r < 6\text{ m}$):
   $$R = \frac{a \cdot b \cdot c}{4 \cdot \text{Area}(\triangle ABC)}$$

$$\text{Infeasible Rate (IR)} = \frac{\text{Number of Infeasible Windows}}{\text{Total Windows}} \times 100\%$$

---

## Consolidated Results (Table 3)

Evaluated over all $60$ simulation files ($40,340$ total windows) across $20$ random seeds (Mean $\pm$ 95% Confidence Interval):

| Experimental Condition | CAV Penetration | Evaluated Seeds | Ground Truth IR (%) | Channel 1 (KF) IR (%) | Fully Imputed (GRU-D) IR (%) | Accel Violations (%) | Curvature Violations (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **penetration_10** | $10\%$ | 20 | $1.01 \pm 0.30\%$ | $0.83 \pm 0.23\%$ | $\mathbf{78.39 \pm 1.00\%}$ | $78.39 \pm 1.00\%$ | $11.35 \pm 0.94\%$ |
| **penetration_20** | $20\%$ | 20 | $1.02 \pm 0.21\%$ | $0.86 \pm 0.20\%$ | $\mathbf{78.50 \pm 0.60\%}$ | $78.49 \pm 0.61\%$ | $11.91 \pm 0.73\%$ |
| **penetration_30** | $30\%$ | 20 | $1.33 \pm 0.17\%$ | $1.15 \pm 0.16\%$ | $\mathbf{78.57 \pm 0.63\%}$ | $78.56 \pm 0.63\%$ | $12.71 \pm 0.76\%$ |

### Core Takeaways:
- **Ground Truth ($IR \approx 1.0\%$):** Confirms baseline validity; realistic simulator motion does not trigger false positives.
- **Channel 1 Kalman Filter ($IR \approx 0.8\%$):** Proves that RSU-assisted leader estimation does not perturb ego vehicle kinematics.
- **Fully Imputed Pipeline ($IR \approx 78.5\%$):** Demonstrates that unconstrained GRU-D interpolation produces severe derivative instability (accelerations exceeding $\pm 24\text{ m/s}^2$).

---

## How to Run the Project

### 1. Prerequisites
Ensure you have Python 3.10+ installed. Install the dependencies:
```bash
pip install numpy pandas matplotlib seaborn openpyxl jupyter
```

### 2. Launch the Jupyter Notebook
Open the interactive evaluation notebook:
```bash
jupyter notebook Objective_1_Infeasible_Rate.ipynb
```
Run all cells (`Cell` $\to$ `Run All`). The notebook executes the kinematic formulas, performs unit tests, loops across all 60 files, and displays Table 3.

---

## File Descriptions

| File Name | Purpose |
| :--- | :--- |
| **`Objective_1_Infeasible_Rate.ipynb`** | Main self-contained notebook containing all kinematic functions, sanity tests, batch evaluation loops, and Table 3 generation. |
| **`PROJECT_REPORT.md`** | Complete academic report covering missingness taxonomy, dual-channel architecture, mathematical derivations, and findings. |
| **`objective_1_results.xlsx`** | Excel workbook with auto-fitted columns and formatted styling containing both summary metrics and detailed per-seed data. |
| **`objective_1_summary_table.csv`** | Clean CSV export of Table 3 with Mean $\pm$ 95% Confidence Intervals. |
| **`objective_1_all_seeds_detailed.csv`** | CSV tracking window count and individual violation rates for each of the 60 seed runs (rounded to 2 decimal places). |
| **`ir_comparison_across_conditions.png`** | High-resolution publication bar chart comparing IR across Ground Truth, Channel 1, and Fully Imputed data. |

---

## Team (Group 7)

| Name | Roll No. |
| :--- | :--- |
| **Ujjwal Singh** | 262IS036 |
| **Siddharth Patidar** | 262CS031 |
| **Sagar Kushwah** | 262CS025 |
| **Dev** | 252IS011 |

---

## License
This project is developed for academic research purposes under the MIT License.
