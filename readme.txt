================================================================================
NATIONAL INSTITUTE OF TECHNOLOGY KARNATAKA (NITK), SURATHKAL
Department of Computer Science and Engineering
Course Project Submission (Academic Session 2026)
================================================================================

PROJECT TITLE:
Physical-Validity Metric for Imputed Vehicle State and SFM Percolation Threshold 
in Cooperative Adaptive Cruise Control (CACC) Mixed Traffic

STUDENT AUTHORS (Group 7):
  1. Ujjwal Singh       (Roll No: 262IS036)  -- Submission Lead
  2. Siddharth Patidar  (Roll No: 262CS031)
  3. Sagar Kushwah      (Roll No: 262IS025)

COURSE INSTRUCTOR:
  Dr. Sourav Kanti Addya
  Assistant Professor, Department of Computer Science and Engineering
  National Institute of Technology Karnataka, Surathkal

PROJECT MENTOR:
  Dev C Bhatt

PUBLIC GITHUB REPOSITORY:
  https://github.com/UjJwAl092003/physical-validity-cav-percolation

================================================================================
1. SUBMISSION PACKAGE STRUCTURE (MANDATORY ITEMS ONLY)
================================================================================
Following the authoritative project guidelines (AboutProject.pdf), this master
submission archive (ujjwal_262IS036.zip) contains strictly the required items:

  ujjwal_262IS036.zip
  │
  ├── cloudProject/               [Core Project Folder & Implementation]
  │   ├── Objective_1_Infeasible_Rate.ipynb   (Executed Notebook with full outputs)
  │   ├── Objective_2_Percolation_Sweep.ipynb (Executed Notebook with full outputs)
  │   ├── run_objective_2.py                  (Automated 60-run sweep script)
  │   ├── results.xlsx                        (Master 4-sheet workbook with all results)
  │   ├── figures/                            (Publication-quality plots)
  │   │   ├── acceleration_and_curvature_distributions.png
  │   │   ├── ir_comparison_across_conditions.png
  │   │   ├── percolation_sweep_curve.png
  │   │   └── sample_trajectory_comparison.png
  │   └── README.md                           (GitHub repository README & docs)
  │
  ├── report.pdf / Report_Final.pdf [7-Page Formal Technical Report (IEEE Layout)]
  └── readme.txt                  [This Submission Documentation & Execution Guide]

*Note on Datasets: As the underlying simulation datasets (data_corrupted and highD)
are pre-distributed by the project mentor and exceed upload quotas, they are
intentionally excluded from the Moodle zip. All outputs and results are fully
preserved in results.xlsx and the executed notebooks.

================================================================================
2. EXECUTIVE SUMMARY OF COMPLETED OBJECTIVES & KEY RESULTS
================================================================================

[OBJECTIVE 1] Kinematic Infeasible Rate (IR) Metric:
  - Formulated a 2-parameter kinematic test over 30-step (3.0s) windows:
      * Longitudinal acceleration bounds: a_t in [-8.0, +3.0] m/s^2
      * Circumcircle / Menger turning radius: r_t >= 6.0 m
  - Batch-evaluated across 60 simulation files (40,340 total windows):
      * Ground Truth Baseline:       IR = 1.01% - 1.33% (Validates metric sanity)
      * Channel 1 (Kalman Filter):   IR = 0.83% - 1.15% (Kinematically neutral)
      * Fully Imputed (GRU-D):       IR = 78.39% - 78.57% (Catastrophic failure)
  - Key Finding: Conventional positional error metrics (ADE < 0.5m) fail to capture
    severe high-frequency derivative jitter (|a| > 24 m/s^2) emitted by neural
    network interpolators.

[OBJECTIVE 2] SFM Percolation Sweep & Critical Threshold:
  - Executed a 6-point market penetration sweep:
      p in {18%, 21%, 24%, 27%, 30%, 35%} across 10 random seeds (60 total runs).
  - Fitted 3-parameter Logistic growth model: S(p) = L / (1 + exp(-k*(p - p_c)))
      * Saturation Level (L):        37.12%
      * Logistic Growth Rate (k):    0.1318
      * Critical Threshold (p_c):    20.66%
      * Transition Width (w):        30.34%
  - Bounded Interval Reporting: 95% Confidence Intervals at 18% [9.52%, 20.24%] 
    and 21% [14.29%, 25.01%] overlap. Following assignment specifications, the 
    connectivity transition is formally bounded within [18%, 21%] CAV Penetration.

[OBJECTIVE 3] Leader Definitions Comparison & Physics Verdict:
  - Formulated and compared two distinct CAV leader tracking definitions:
      1. Instantaneous Leader (per discrete 0.1s timestep)
      2. Modal Leader (temporal mode / majority vote across 3.0s window)
  - Empirical agreement:
      * Critical threshold difference:  Delta p_c = |20.66% - 20.73%| = 0.07%
      * Growth rate agreement:          Delta k < 0.5%
  - Conclusive Scientific Verdict: Because temporal smoothing preserves the exact
    same inflection threshold, the percolation jump is definitively CONFIRMED to
    be a GENUINE PHYSICAL PROPERTY of CACC vehicular traffic (spontaneous platoon
    coalescence at ~20% penetration), and NOT an observational windowing artifact.

[OBJECTIVE 4] Transparent Reproducibility Notice:
  - The proprietary CAERI-NDS naturalistic driving dataset from Paper B is not
    publicly distributed. Consequently, exact numerical reproduction of Paper B
    Tables II-III is not feasible without the private dataset. All mathematical
    formulations, missingness models (SFM/TCM), and validation algorithms were
    fully implemented and verified on the public highD simulation corpus.

================================================================================
3. SYSTEM REQUIREMENTS & ENVIRONMENT SETUP
================================================================================
  - Operating System: Windows 10/11 or Linux / macOS
  - Python Version:   Python 3.10 or higher
  - Required Python Libraries:
      * numpy
      * pandas
      * scipy
      * matplotlib
      * openpyxl
      * jupyter / ipykernel

  Quick Installation via pip:
    pip install numpy pandas scipy matplotlib openpyxl jupyter

================================================================================
4. HOW TO EXECUTE AND REPRODUCE THE EXPERIMENTS
================================================================================

Step 1: Open the Project Directory
  Navigate to the `cloudProject/` directory in your terminal or VS Code / IDE.

Step 2: Reproduce Objective 1 (Infeasible Rate Metric Evaluation)
  - Launch Jupyter Notebook:
      jupyter notebook Objective_1_Infeasible_Rate.ipynb
  - Select "Run All Cells".
  - The notebook parses the corrupted state files across 10%, 20%, and 30%
    penetration rates, computes acceleration and Menger curvature violations, and
    saves results to `results.xlsx`.

Step 3: Reproduce Objective 2 (SFM Percolation Sweep & S-Curve Fitting)
  - Method A (Jupyter Notebook):
      jupyter notebook Objective_2_Percolation_Sweep.ipynb
      Select "Run All Cells".
  - Method B (Automated Command Line):
      python run_objective_2.py
  - Both methods run the 60-seed sweep, fit the 3-parameter Logistic curve,
    display 95% Confidence Intervals, compute p_c, and save the publication plot
    to `figures/percolation_sweep_curve.png`.

Step 4: View Consolidated Data
  - All consolidated tables and spreadsheets are stored in `results.xlsx`.
  - All publication-ready figures are stored in `figures/`.

================================================================================
5. CONTACT & VERIFICATION
================================================================================
For any queries or evaluation assistance, please contact the student authors:
  - Ujjwal Singh       (262IS036): ujjwal.262is036@nitk.edu.in
  - Siddharth Patidar  (262CS031): siddharth.262cs031@nitk.edu.in
  - Sagar Kushwah      (262IS025): sagar.262is025@nitk.edu.in

Department of Computer Science and Engineering
National Institute of Technology Karnataka, Surathkal, India
================================================================================
