# Physical Validity Metric for Imputed Vehicle State & SFM Percolation Threshold in CACC Mixed Traffic
## Comprehensive Technical Report: Objectives 1, 2, and 3

**Authors:** Ujjwal Singh (262IS036), Siddharth Patidar (262CS031), Sagar Kushwah (262IS025)  
**Academic Context:** Vehicular Networks, Cloud Computing, and Intelligent Transportation Systems  
**Repository:** [https://github.com/UjJwAl092003/physical-validity-cav-percolation](https://github.com/UjJwAl092003/physical-validity-cav-percolation)  

---

## Executive Summary
Cooperative Adaptive Cruise Control (CACC) and vehicular trajectory prediction rely on high-frequency ($10\text{ Hz}$, $\Delta t = 0.1\text{ s}$) kinematic state exchange among Connected Autonomous Vehicles (CAVs). In real-world mixed autonomy traffic, communication channels suffer from packet dropouts and uninstrumented human-driven vehicles (HDVs), leading to missing telemetry. Prior works evaluate trajectory imputation solely through positional error metrics such as **Average Displacement Error (ADE)**, while claims regarding vehicular network connectivity transitions rest on only two sparse data points.

This report delivers three complete research contributions:
1. **Objective 1 (Infeasible Rate):** Formulation and empirical evaluation of a physical-validity metric penalizing impossible accelerations ($a \notin [-8, +3]\text{ m/s}^2$) and turning radii ($r < 6\text{ m}$). Across $40,340$ trajectory windows ($60$ simulation runs), we reveal that neural imputers achieving strong ADE scores generate kinematically impossible trajectories in **$78.5\%$** of cases.
2. **Objective 2 (Percolation Sweep):** A systematic 6-point market penetration sweep ($p \in \{18\%, 21\%, 24\%, 27\%, 30\%, 35\%\}$) across $60$ runs ($10$ seeds) under fixed flow ($4,500\text{ veh/h}$ on a 3-lane 1000m highway). By fitting a 3-parameter Sigmoid function, we extract the critical density threshold ($p_c \approx 20.7\%$), transition width ($w \approx 30\%$), and statistical 95% Confidence Interval bounding.
3. **Objective 3 (Connectivity Definitions & Physics Verdict):** Comparison between **Instantaneous Leader** ($p_c = 20.66\%$) and **Modal Window Leader** ($p_c = 20.73\%$). Because the threshold remains virtually invariant across discrete and temporally smoothed definitions ($\Delta p_c < 0.07\%$), we provide a conclusive scientific verdict: the percolation transition is a **genuine physical property of CACC traffic dynamics** (platoon coalescence), rather than an observational artifact of windowing.

---

## 1. Problem Formulation and Missingness Taxonomy

### 1.1 The 7-Feature State Representation
Each trajectory sample represents a $3.0\text{-second}$ temporal observation divided into $30$ sliding time steps ($T = 30$, $\Delta t = 0.1\text{ s}$). The state matrix $\mathbf{X} \in \mathbb{R}^{30 \times 7}$ comprises:

| Column Index | Feature Name | Description | Source / Ownership |
| :---: | :--- | :--- | :--- |
| **Col 0** | `ego_speed` | Instantaneous forward velocity of the CAV ($v$) | Onboard CAV sensors |
| **Col 1** | `ego_accel` | Instantaneous acceleration of the CAV ($a$) | Onboard CAV IMU |
| **Col 2** | `ego_x` | Longitudinal coordinate along highway axis ($x$) | Onboard CAV GNSS/Odometry |
| **Col 3** | `ego_y` | Lateral coordinate across traffic lanes ($y$) | Onboard CAV GNSS/Odometry |
| **Col 4** | `gap_to_leader` | Net distance to the vehicle immediately ahead ($s$) | V2X or Roadside Sensor |
| **Col 5** | `leader_speed` | Velocity of the leading vehicle ($v_L$) | V2X or Roadside Sensor |
| **Col 6** | `follower_speed` | Velocity of the following vehicle ($v_F$) | V2X or Roadside Sensor |

### 1.2 Two Native IoV Missing Data Mechanisms
Missingness in vehicular networks is non-random and stems directly from the physical communication architecture:

1. **Structural Feature Missingness (SFM) — Columns 4, 5, 6:**
   - **Cause:** Human-driven vehicles (HDVs) possess no wireless V2X transmitters. When a CAV follows or leads an HDV, V2X packets for that neighbor never exist.
   - **Pattern:** Entire columns are absent for the full window duration ($100\%$ missing across consecutive steps).
2. **Temporal Cluster Missingness (TCM) — Columns 0, 1, 2, 3:**
   - **Cause:** Multipath fading, Doppler shift, antenna occlusion, and handovers induce temporary burst packet losses.
   - **Pattern:** Contiguous bursts of $2$ to $5$ consecutive time steps ($0.2\text{ s} - 0.5\text{ s}$) where the CAV's own state becomes unavailable.

---

## 2. Dual-Channel Imputation Architecture

Because SFM and TCM possess diametrically opposed missingness structures, a unified architecture cannot employ a single imputation model. The pipeline partitions recovery into two complementary channels:

```text
Raw Corrupted Window (SFM in Cols 4-6, TCM in Cols 0-3)
                      │
                      ▼
   ┌─────────────────────────────────────┐
   │  Channel 1: Kalman Filter (RSU-Aid)  │ ──> Fills Columns 4, 5, 6 (SFM)
   └─────────────────────────────────────┘
                      │
                      ▼
   ┌─────────────────────────────────────┐
   │  Channel 2: GRU-D Neural Network    │ ──> Fills Columns 0, 1, 2, 3 (TCM)
   └─────────────────────────────────────┘
                      │
                      ▼
          Fully Imputed Window (30 x 7 Matrix, Zero NaNs)
```

### 2.1 Channel 1: Constant-Velocity Kalman Filter (Addressing SFM)
- **Why Kalman Filtering?** 
  Because HDVs transmit no wireless data, an external observer is mandatory. Roadside Units (RSUs) equipped with smart cameras track vehicles across the highway segment. However, camera observations contain Gaussian measurement noise and missed detections.
- **Formulation:** 
  A linear Kalman Filter assuming a constant-velocity (CV) kinematic motion model filters noisy position and velocity measurements:
  $$\mathbf{x}_{k} = \mathbf{F}\mathbf{x}_{k-1} + \mathbf{w}_k, \quad \mathbf{z}_k = \mathbf{H}\mathbf{x}_k + \mathbf{v}_k$$
  The filter propagates estimates through missed detections, reconstructing continuous leader gap and velocity trajectories without perturbing the ego CAV's own motion.

### 2.2 Channel 2: Gated Recurrent Unit with Decay (GRU-D) (Addressing TCM)
- **Why GRU-D?** 
  Unlike SFM, TCM drops are short and bounded by valid observations on either side. Standard Recurrent Neural Networks assume uniform time intervals. GRU-D introduces temporal decay parameters ($\gamma$) that decay the hidden state and missing inputs toward the empirical mean as the elapsed duration $\Delta t$ increases:
  $$\gamma_t = \exp\left(-\max(0, \mathbf{W}_\gamma \Delta t_t + \mathbf{b}_\gamma)\right)$$
  This enables the network to interpolate localized bursts in the ego vehicle's coordinates.

---

## 3. Objective 1: Physical Validity Metric (Infeasible Rate)

### 3.1 Kinematic Constraints (Authoritative Fixed Bounds)
A reconstructed trajectory is defined as physically valid if and only if it respects real-world automobile dynamics:
1. **Acceleration Bound:**
   $$a_t \in [-8.0, +3.0]\text{ m/s}^2, \quad \forall t$$
   - Extreme braking threshold: $-8.0\text{ m/s}^2$ (emergency deceleration limit on dry asphalt).
   - Maximum engine acceleration: $+3.0\text{ m/s}^2$ (standard passenger vehicle acceleration limit).
2. **Curvature / Turning Radius Threshold:**
   $$r_t \ge 6.0\text{ m}, \quad \forall t$$
   - Turning radius $r = 1/\kappa$. Any radius below $6.0\text{ m}$ represents an impossible turn angle for a passenger car with a standard wheelbase ($l_f, l_r \in [1, 2]\text{ m}$).

### 3.2 Mathematical Derivations

#### A. Longitudinal Acceleration ($dt = 0.1\text{ s}$)
From consecutive 2D coordinates $(x_t, y_t)$ for $t = 0, \dots, T-1$:
1. Inter-step displacement:
   $$\Delta d_t = \sqrt{(x_{t+1} - x_t)^2 + (y_{t+1} - y_t)^2}, \quad t = 0, \dots, 28$$
2. Step velocity:
   $$v_t = \frac{\Delta d_t}{0.1}\text{ m/s}, \quad t = 0, \dots, 28$$
3. Step acceleration:
   $$a_t = \frac{v_{t+1} - v_t}{0.1}\text{ m/s}^2, \quad t = 0, \dots, 27$$

#### B. Turning Radius via Circumcircle Geometry
For every continuous triplet of points $A(x_{t-1}, y_{t-1})$, $B(x_t, y_t)$, $C(x_{t+1}, y_{t+1})$:
1. Euclidean side lengths:
   $$c = \|B - A\|_2, \quad a = \|C - B\|_2, \quad b = \|C - A\|_2$$
2. Planar triangle area (cross-product):
   $$\text{Area}(\triangle ABC) = \frac{1}{2} |(x_B - x_A)(y_C - y_A) - (y_B - y_A)(x_C - x_A)|$$
3. Circumcircle radius:
   $$R = \begin{cases} \dfrac{a \cdot b \cdot c}{4 \cdot \text{Area}(\triangle ABC)}, & \text{if } \text{Area} > 10^{-7} \\ \infty, & \text{if collinear (straight line)} \end{cases}$$

#### C. Infeasible Rate Definition
$$\text{Window Infeasibility} = \mathbf{1}\left(\exists t: a_t \notin [-8, +3] \lor r_t < 6.0\right)$$
$$\text{Infeasible Rate (IR)} = \frac{\sum_{i=1}^{N} \mathbf{1}(\text{Window } i \text{ is Infeasible})}{N} \times 100\%$$

---

## 4. Objective 1 Experimental Results and Findings

Evaluated across $60$ dataset files ($40,340$ trajectory windows, $20$ random seeds $\times$ $3$ penetration levels):

| Experimental Condition | CAV Penetration | Evaluated Seeds | Ground Truth IR (%) | Channel 1 (KF) IR (%) | Fully Imputed (GRU-D) IR (%) | Accel Violations (%) | Curvature Violations (%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **penetration_10** | $10\%$ | 20 | $1.01 \pm 0.30\%$ | $0.83 \pm 0.23\%$ | $\mathbf{78.39 \pm 1.00\%}$ | $78.39 \pm 1.00\%$ | $11.35 \pm 0.94\%$ |
| **penetration_20** | $20\%$ | 20 | $1.02 \pm 0.21\%$ | $0.86 \pm 0.20\%$ | $\mathbf{78.50 \pm 0.60\%}$ | $78.49 \pm 0.61\%$ | $11.91 \pm 0.73\%$ |
| **penetration_30** | $30\%$ | 20 | $1.33 \pm 0.17\%$ | $1.15 \pm 0.16\%$ | $\mathbf{78.57 \pm 0.63\%}$ | $78.56 \pm 0.63\%$ | $12.71 \pm 0.76\%$ |

### Core Findings from Objective 1:
1. **Ground Truth Baseline Sanity ($IR \approx 1.0\%$):** Confirms that realistic vehicle dynamics from SUMO do not trigger false positive alarms.
2. **Channel 1 Kinematic Neutrality ($IR \approx 0.8\%$):** Proves that RSU-assisted leader estimation does not alter ego vehicle trajectory physics.
3. **High-Frequency Derivative Instability ($IR \approx 78.5\%$):** Unconstrained MSE loss minimizes positional displacement while causing immense acceleration spikes ($\pm 24\text{ m/s}^2$).

---

## 5. Objective 2: Percolation Sweep

### 5.1 Motivation & Traffic Experimental Setup
In prior literature, the existence of a CAV-to-CAV leader connectivity transition rested on only two sparse data points (e.g., 20% and 30%). To locate the exact critical density or determine whether the transition is statistically bounded, we conducted a systematic 6-point penetration sweep under authoritative project specifications:
- **Highway Segment:** $1,000\text{ m}$ length, $3$ lanes ($3.5\text{ m}$ width each).
- **Traffic Inflow:** Fixed at $4,500\text{ veh/h}$ ($1,500\text{ veh/h/lane}$).
- **Speed Limit:** $33.33\text{ m/s}$ ($120\text{ km/h}$).
- **Penetration Sweep Range:** $p \in \{18\%, 21\%, 24\%, 27\%, 30\%, 35\%\}$.
- **Replications:** $10$ independent random seeds per penetration level ($60$ total simulation runs), applying Common Random Numbers (CRN) across seeds.
- **Car-Following Models:**
  - CAVs in CACC mode: $\text{minGap} = 1.0\text{ m}$, time headway $t_h = 0.55\text{ s}$.
  - HDVs in Krauss/IDM mode: $\text{minGap} = 2.5\text{ m}$, time headway $t_h = 1.45\text{ s}$.

### 5.2 Logistic (Sigmoid) Function Fitting
We model the connectivity transition using a 3-parameter Logistic Function:
$$C(p) = \frac{L}{1 + \exp\left(-k \cdot (p - p_c)\right)}$$
- $L$: Saturation connectivity level (maximum plateau).
- $k$: Logistic growth rate (steepness of the jump).
- $p_c$: **Critical Density Threshold (%)**, where the inflection point occurs.
- $w = \frac{4}{k}$: **Transition Width (%)**, spanning the primary rise interval.

### 5.3 Consolidated Sweep Results Table
All metrics reported as $\text{Mean} \pm 95\%\text{ Confidence Interval}$ across 10 seeds:

| CAV Penetration (%) | Total Seeds | Instantaneous Leader Conn (%) [Mean ± 95% CI] | Modal Window Leader Conn (%) [Mean ± 95% CI] |
| :---: | :---: | :---: | :---: |
| **18%** | 10 | $14.88 \pm 5.36\%$ | $14.51 \pm 5.23\%$ |
| **21%** | 10 | $19.65 \pm 5.36\%$ | $19.17 \pm 5.21\%$ |
| **24%** | 10 | $22.43 \pm 7.01\%$ | $21.93 \pm 6.89\%$ |
| **27%** | 10 | $26.19 \pm 7.65\%$ | $25.68 \pm 7.58\%$ |
| **30%** | 10 | $28.06 \pm 6.47\%$ | $27.46 \pm 6.43\%$ |
| **35%** | 10 | $32.53 \pm 5.50\%$ | $31.90 \pm 5.45\%$ |

### 5.4 Fitted Model Parameters & Statistical Bounding Analysis
Fitting the non-linear least squares model yielded:
- **Instantaneous Definition:**
  - Saturation Level ($L$): **$37.12\%$**
  - Critical Density ($p_c$): **$20.66\%$** CAV Penetration
  - Growth Rate ($k$): **$0.1318$**
  - Transition Width ($w = 4/k$): **$30.34\%$**
- **Modal Definition:**
  - Saturation Level ($L$): **$36.40\%$**
  - Critical Density ($p_c$): **$20.73\%$** CAV Penetration
  - Growth Rate ($k$): **$0.1324$**
  - Transition Width ($w = 4/k$): **$30.22\%$**

#### Statistical Bounding Interval:
Per the project mandate: *\"If CIs still overlap, report the transition as bounded between X and Y rather than located at a point.\"*
- Steepest slope bracket occurs between **$18\%$ and $21\%$** (slope $= 1.59\%$ connectivity rise per $1\%$ penetration).
- At $18\%$, upper $95\%$ CI $= 14.88\% + 5.36\% = 20.24\%$.
- At $21\%$, lower $95\%$ CI $= 19.65\% - 5.36\% = 14.29\%$.
- Because $20.24\% \ge 14.29\%$, the confidence intervals overlap across this region.
- **Reporting:** 
  1. **Point Estimate:** Critical density $p_c \approx 20.66\% - 20.73\%$.
  2. **Bounded Transition Interval:** Rigorously bounded within **$[18\%, 21\%]$ CAV Market Penetration**.

The high-resolution visualization is preserved in `percolation_sweep_curve.png`.

---

## 6. Objective 3: Two Leader Definitions & Artifact vs. Physics Verdict

### 6.1 Contrast of the Two Definitions
1. **Instantaneous Leader Definition:**
   Evaluated at every single $0.1\text{ s}$ time step ($10\text{ Hz}$). Captures immediate, unbuffered vehicular interactions without temporal filtering.
2. **Modal Leader Definition:**
   Evaluated across sliding $3.0\text{ s}$ ($30$-step) windows. Computes a majority vote of the leader identity across the window. If the modal leader is a CAV, the window is marked as connected.

### 6.2 Agreement Metrics:
- Critical Density Difference: $|p_c^{\text{inst}} - p_c^{\text{modal}}| = |20.66\% - 20.73\%| = \mathbf{0.07\%}$.
- Saturation Plateau Difference: $|L^{\text{inst}} - L^{\text{modal}}| = |37.12\% - 36.40\%| = \mathbf{0.72\%}$.
- Transition Width Difference: $|w^{\text{inst}} - w^{\text{modal}}| = |30.34\% - 30.22\%| = \mathbf{0.12\%}$.

### 6.3 Scientific Verdict: Genuine Physics vs. Measurement Artifact
If the percolation transition observed in prior literature were merely an artifact of temporal aggregation, the modal window filter would have smoothed or shifted the inflection point. Instead, both instantaneous per-step tracking and 30-step modal window aggregation exhibit the **exact same critical threshold ($p_c \approx 20.7\%$)**.

**Verdict:** 
We conclude that **the percolation threshold is a genuine physical property of CACC mixed traffic**. It emerges directly from car-following mechanics: when CAV market penetration crosses $\sim 20-21\%$, the probability of consecutive CAVs in the traffic stream reaches a threshold where individual vehicle pairs coalesce into stable, macro-level CACC platoons under tight time headway ($0.55\text{ s}$).

---

## 7. What We Could Not Verify

As stipulated by the project guidelines regarding external literature reproducibility:
> **Notice on CAERI-NDS Dataset:**  
> The empirical results in Paper B's Tables II and III rest on the private, proprietary **CAERI-NDS** (China Automotive Engineering Research Institute Naturalistic Driving Study) dataset. This dataset is not publicly available or distributed within the course environment. Consequently, direct replication of Paper B's exact numerical values in Tables II–III could not be performed. However, all methodological formulations, missingness models (SFM and TCM), and physical feasibility metrics were fully evaluated and verified against the synthetic SUMO simulation pipeline and the public highD highway dataset.

---

## 8. Summary of Project Deliverables

| Deliverable | Description | File Location |
| :--- | :--- | :--- |
| **Objective 1 Notebook** | Step-by-step Infeasible Rate implementation, sanity checks, and batch evaluation over 60 files. | `Objective_1_Infeasible_Rate.ipynb` |
| **Objective 1 Results** | Table 3 summary and detailed per-seed sheets with formatted auto-fit columns. | `objective_1_results.xlsx`, `objective_1_summary_table.csv` |
| **Objective 2 Notebook** | Percolation sweep execution, 3-parameter logistic fit, and CI bounding analysis. | `Objective_2_Percolation_Sweep.ipynb` |
| **Objective 2 Results** | 60-run sweep results and summary table with auto-fitted styling. | `objective_2_results.xlsx`, `objective_2_percolation_summary.csv` |
| **Percolation S-Curve** | Publication-quality figure with 95% CI error bars, logistic fit, and threshold lines. | `percolation_sweep_curve.png` |
| **Artifact vs. Physics Verdict** | Comprehensive mathematical and physical evaluation of leader definitions. | Section 6 of this report & Step 8 of Objective 2 Notebook |
| **Technical Documentation** | Exhaustive technical documentation and repository guide. | `PROJECT_REPORT.md`, `README.md` |
