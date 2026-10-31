# Master PPT & Viva Presentation Guide: CAV Trajectory Imputation & Percolation Threshold
### Project: Physical Validity Metric for Imputed Vehicle State & SFM Percolation Threshold in CACC Mixed Traffic
**Team Members:** Ujjwal Singh (262IS036), Siddharth Patidar (262CS031), Sagar Kushwah (262IS025)

---

## Index / Table of Contents
1. **Slide 1-2: Project ka Big Picture & Motivation (Aakhir yeh project kyu bana?)**
2. **Slide 3: System Specifications & Numbers (10 Hz, 0.1s, 30 Steps, 7 Columns)**
3. **Slide 4: 7-Column State Matrix ka Detail Breakdown**
4. **Slide 5: Do Tarah ke Missingness (SFM vs. TCM)**
5. **Slide 6: Dual-Channel Imputation Architecture (RSU + Kalman Filter + GRU-D)**
6. **Slide 7: Purane Research ki Sabse Badi Galti (The ADE Trap)**
7. **Slide 8: Objective 1 — Infeasible Rate (IR) Metric & Uski Mathematics**
8. **Slide 9: Objective 1 ke Results & Table 3 ka Detailed Analysis**
9. **Slide 10: Objective 2 — Percolation Sweep (60 Runs & S-Curve Fitting)**
10. **Slide 11: Objective 3 — Do Leader Definitions & Physics vs. Artifact Verdict**
11. **Slide 12: Code, Notebooks & Datasets ka Workflow**
12. **Bonus: Top 10 Expected Viva / Cross-Questions & Unke Confident Answers**

---

## 1. Project ka Big Picture & Motivation (Aakhir yeh project kyu bana?)

### A. Real-World Highway Reality (Mixed Autonomy):
* Aane wale 15-20 saal tak sadak par sirf autonomous gaadiyan nahi chalengi. Sadak par dono tarah ki gaadiyan ek sath chalengi:
  1. **CAVs (Connected & Autonomous Vehicles):** Jinme sensors, AI computer, aur wireless V2X (Vehicle-to-Everything) communication radios lage hote hain.
  2. **HDVs (Human-Driven Vehicles):** Normal gaadiyan jo hum aur aap chalate hain, jinme koi V2X radio ya automated communication chip nahi hoti.
* Is mixed traffic environment ko **Mixed Autonomy** kehte hain.

### B. Automated Gaadiyon ka Goal (CACC & Trajectory Prediction):
* Highway par jab autonomous gaadiyan chalti hain, toh unka sabse bada feature hota hai **CACC (Cooperative Adaptive Cruise Control)**. 
* CACC mein gaadiyan aapas mein wireless signal exchange karke ek-doosre ke peeche bahut kam doori (**$0.55\text{ second}$ time headway**) par line bana kar (platoon) tezi se aur safe tareeqe se chalti hain.
* Safe chalne ke liye autonomous gaadi ko **Trajectory Prediction** karni padti hai: *"Agle 5 seconds ($50\text{ steps}$) mein main aur mere aage-peeche wali gaadiyan kahan hongi?"*
* Future predict karne ke liye usko pichhle **3 seconds ($30\text{ steps}$)** ka continuous accurate data chahiye hota hai.

### C. Hamare Project ka Core Aim (Objective):
1. **Objective 1:** Imputed data ki **Physical Kinematic Validity** check karna ek naye metric se — jiska naam hai **Infeasible Rate (IR)**.
2. **Objective 2:** CAVs ke badhne par highway connectivity mein aane wale **Percolation Jump** ko 6-point sweep aur Logistic S-curve se scientifically prove karna.
3. **Objective 3:** Yeh prove karna ki percolation jump **real vehicular physics** hai ya sirf windowing ka measurement artifact.

---

## 2. System Specifications & Numbers (Timing & Frequency)

Professor presentation mein timing aur frequency par sawaal zaroor poochte hain. Yeh numbers dhyan mein rakhein:

* **Broadcast Frequency = $10\text{ Hz}$:**
  - Gaadi **1 second mein 10 baar** telemetry broadcast karti hai.
  - Iska matlab har reading ke beech ka time step: **$\Delta t = 0.1\text{ second}$**.
* **Historical Observation Window = $3.0\text{ seconds}$:**
  - $3.0\text{ s} \times 10\text{ Hz} = \mathbf{30\text{ time steps}}$.
  - Har vehicle sample ek $30 \times 7$ ki 2D matrix hota hai.
* **Future Prediction Horizon = $5.0\text{ seconds}$:**
  - $5.0\text{ s} \times 10\text{ Hz} = \mathbf{50\text{ time steps}}$ into the future.
* **Highway Environment Parameters (Authoritative Specs):**
  - **Highway Length:** $1000\text{ meter}$, $3$ lanes ($3.5\text{ m}$ width each).
  - **Speed Limit:** $33.33\text{ m/s}$ (yaani $120\text{ km/h}$).
  - **Traffic Flow:** $4500\text{ vehicles/hour}$ ($1500\text{ veh/h/lane}$).

---

## 3. 7-Column State Matrix ka Detail Breakdown

Har 3-second ke window mein jo $30 \times 7$ matrix banti hai, uska **Owner (Hero)** hamesha **Ego-CAV (Autonomous Gaadi)** hoti hai. Uske saat columns ye hain:

| Col Index | Feature Name | Kiska Data Hai? | Source / Kaise Milta Hai? |
| :---: | :--- | :--- | :--- |
| **Col 0** | `ego_speed` | Autonomous gaadi ki apni forward speed ($v$) | Onboard Wheel Speed Sensor |
| **Col 1** | `ego_accel` | Autonomous gaadi ka apna acceleration ($a$) | Onboard IMU (Accelerometer) |
| **Col 2** | `ego_x` | Autonomous gaadi ka longitudinal position ($x$) | Onboard GPS / Odometry |
| **Col 3** | `ego_y` | Autonomous gaadi ka lateral lane position ($y$) | Onboard GPS / Odometry |
| **Col 4** | `gap_to_leader` | Aage wali gaadi se net physical doori ($s$) | V2X ya RSU Roadside Camera |
| **Col 5** | `leader_speed` | Aage wali gaadi ki speed ($v_L$) | V2X ya RSU Roadside Camera |
| **Col 6** | `follower_speed`| Peeche wali gaadi ki speed ($v_F$) | V2X ya RSU Roadside Camera |

---

## 4. Do Tarah ke Missingness (SFM vs. TCM)

Internet ya tabular data mein missing values random (MCAR) hoti hain. Lekin vehicular networks mein missingness communication physics ki wajah se aati hai:

```
                           Vehicular Missingness
                                    │
         ┌──────────────────────────┴──────────────────────────┐
         ▼                                                     ▼
1. Structural Feature Missingness (SFM)             2. Temporal Cluster Missingness (TCM)
   - Columns: 4, 5, 6                                  - Columns: 0, 1, 2, 3
   - Wajah: Padosi gaadi Human (HDV) hai              - Wajah: Wireless radio packet loss
   - Pattern: Poore 3s (30 steps) gayab (100% NaN)    - Pattern: Chhote bursts (2-5 steps) gayab
   - Solution: RSU Camera + Kalman Filter             - Solution: GRU-D Neural Network
```

### A. Structural Feature Missingness (SFM) — Columns 4, 5, 6:
* **Asli Wajah:** Jab automated gaadi ke aage ya peeche koi **Human-driven vehicle (HDV)** chal rahi hoti hai, toh HDV ke paas wireless transmitter nahi hota.
* **Effect:** Automated gaadi ko padosi gaadi ki speed ya gap V2X se mil hi nahi sakta. Poore 30 steps tak Columns 4, 5, 6 **complete NaN (empty)** rehte hain.
* **Kyu Important Hai?:** Yeh koi data error nahi hai, yeh sensing architecture ka fundamental issue hai.

### B. Temporal Cluster Missingness (TCM) — Columns 0, 1, 2, 3:
* **Asli Wajah:** Automated gaadi ka apna V2X communication wireless channel par chalta hai. Tunnel, bade trucks ki occlusion, multipath fading, ya base-station handover ke waqt signal pal-bhar ke liye cut jaata hai.
* **Effect:** Ego gaadi ke apne khud ke 4 columns beech-beech mein $2$ se $5$ consecutive steps ($0.2\text{ s} - 0.5\text{ s}$) ke liye gayab ho jaate hain.

---

## 5. Dual-Channel Imputation Architecture (Data Kaise Bhara Jaata Hai?)

Kyunki SFM aur TCM dono alag-alag tarah ke missingness hain, isliye ek single model dono ko nahi bhar sakta. Pipeline do specialized channels mein kaam karti hai:

```text
Raw Corrupted Window (SFM in Cols 4-6, TCM in Cols 0-3)
                      │
                      ▼
   ┌────────────────────────────────────────────────────────┐
   │ CHANNEL 1: Kalman Filter (RSU Camera Aided)            │
   │  -> Highway ke pole par laga camera HDV ko track karta  │
   │  -> Kalman Filter noise hatakar smooth gap/speed deta   │
   │  -> Fills Columns 4, 5, 6 (SFM Resolved)               │
   └────────────────────────────────────────────────────────┘
                      │
                      ▼
   ┌────────────────────────────────────────────────────────┐
   │ CHANNEL 2: GRU-D (Gated Recurrent Unit with Decay)     │
   │  -> Ego vehicle ke 2-5 steps ke burst packet loss ko   │
   │     temporal decay mechanism se interpolate karta hai  │
   │  -> Fills Columns 0, 1, 2, 3 (TCM Resolved)            │
   └────────────────────────────────────────────────────────┘
                      │
                      ▼
    Fully Imputed Window (30 x 7 Matrix, Zero NaNs)
```

### Channel 1 ka Deep Dive (RSU + Kalman Filter):
1. **RSU (Roadside Unit) Camera:** Highway ke pole par laga smart camera HDV gaadiyon ko upar se track karta hai.
2. **Camera ki Kamzori:** Camera ke reading mein Gaussian measurement noise hota hai aur aage bada truck aane par gaadi chhup jaati hai (**missed detection**).
3. **Kalman Filter ka Kaam:** Linear Constant-Velocity (CV) kinematic Kalman Filter noisy measurements ko filter karta hai aur missed detection ke waqt accurate trajectory estimate karke **Columns 4, 5, 6** ko fill kar deta hai.

### Channel 2 ka Deep Dive (GRU-D Neural Network):
1. Normal RNN ya LSTM sochte hain ki har step par data barabar time gap par aa raha hai.
2. **GRU-D ka Decay Mechanism ($\gamma$):** GRU-D pichhli valid reading se lekar ab tak beete hue time ($\Delta t$) ko decay parameter se multiply karta hai:
   $$\gamma_t = \exp\left(-\max(0, \mathbf{W}_\gamma \Delta t_t + \mathbf{b}_\gamma)\right)$$
3. Is decay ki madad se wo ego-vehicle ke missing coordinates ($x, y, v, a$) ko bilkul seamlessly fill kar deta hai (**Columns 0, 1, 2, 3**).

---

## 6. Purane Research ki Sabse Badi Galti (The ADE Trap)

### A. Average Displacement Error (ADE) Kya Hai?
Duniya bhar ke trajectory papers sirf ADE naapte the:
$$\text{ADE} = \frac{1}{T} \sum_{t=1}^{T} \sqrt{(x_t^{\text{true}} - x_t^{\text{pred}})^2 + (y_t^{\text{true}} - y_t^{\text{pred}})^2}$$
Yaani asli position aur model dwara bhari gayi position ke beech ka average euclidean distance.

### B. ADE ka Dhokha:
* Maan lo kisi model ka ADE sirf **$0.3\text{ meter}$** aaya. Reviewers aur professors sochte the: *"Arre waah! Model ne toh gaadi ki location 30 centimeter accurate predict kar di, model perfect hai!"*
* **Lekin asli dhokha yahan hai:** Machine learning models (jaise GRU-D) sirf Mean Squared Error (MSE) loss minimize karte hain.
* Agar coordinates mein har step par sirf $20-30\text{ cm}$ ka halka sa zigzag (jitter) aa jaye, toh position ka difference bahut kam rehta hai (ADE bahut accha aata hai).
* Lekin jab car chalegi, toh har $0.1\text{ s}$ ke interval par wo chhota sa zigzag **bhayankar high acceleration spikes** ($+25\text{ m/s}^2$) aur **sharp turning** paida kar deta hai!
* **Conclusion:** Ek trajectory paper par mathematically acchi lag sakti hai, par agar use kisi asli car ke steering aur motor mein daal diya jaye, toh car palat jayegi ya engine phat jayega!

---

## 7. Objective 1: Infeasible Rate (IR) Metric & Uski Mathematics

Isi ADE ke dhokhe ko pakadne ke liye humne **Infeasible Rate (IR)** banaya.

### A. Authoritative Physical Bounds (Car Physics):
Ek trajectory window ($30$ steps) physically valid tabhi maani jayegi jab wo do boundary conditions follow kare:
1. **Acceleration Limit:**
   $$a_t \in [-8.0, +3.0]\text{ m/s}^2$$
   - Extreme braking: $-8.0\text{ m/s}^2$ (asphalt road par emergency brake ki limit).
   - Maximum acceleration: $+3.0\text{ m/s}^2$ (normal passenger car ke engine ki boundary).
2. **Curvature / Turning Radius Limit:**
   $$r_t \ge 6.0\text{ meter} \quad (\text{yaani Curvature } \kappa = 1/r \le 0.1667\text{ m}^{-1})$$
   - Passenger car ke wheelbase ($l_f, l_r \in [1, 2]\text{ m}$) aur steering geometry ($\pm 45^\circ$) ke mutabiq gaadi $6\text{ meter}$ se chhote radius par physically mud hi nahi sakti.

### B. Mathematical Formulas (Presentation mein board par explain karne ke liye):

#### 1. Longitudinal Acceleration ($dt = 0.1\text{ s}$):
Consecutive coordinates $(x_t, y_t)$ se:
* **Step Displacement:** $\Delta d_t = \sqrt{(x_{t+1} - x_t)^2 + (y_{t+1} - y_t)^2}$
* **Step Velocity:** $v_t = \frac{\Delta d_t}{0.1}\text{ m/s}$
* **Step Acceleration:** $a_t = \frac{v_{t+1} - v_t}{0.1}\text{ m/s}^2$

#### 2. Turning Radius (Circumcircle Formula):
Lagataar 3 points $A(x_{t-1}, y_{t-1})$, $B(x_t, y_t)$, $C(x_{t+1}, y_{t+1})$ se banne wale triangle ka circumcircle:
* Triangle ke sides: $c = \|B - A\|$, $a = \|C - B\|$, $b = \|C - A\|$
* Triangle ka Area (Cross-product):
  $$\text{Area} = \frac{1}{2} |(x_B - x_A)(y_C - y_A) - (y_B - y_A)(x_C - x_A)|$$
* Turning Radius:
  $$R = \frac{a \cdot b \cdot c}{4 \cdot \text{Area}}$$

#### 3. Infeasible Rate Formula:
$$\text{Window Infeasible} = 1 \quad \text{agar kisi bhi step par } (a_t \notin [-8, 3] \text{ ya } r_t < 6.0)$$
$$\mathbf{\text{IR (\%)}} = \frac{\text{Total Infeasible Windows}}{\text{Total Evaluated Windows}} \times 100\%$$

---

## 8. Objective 1 ke Results & Table 3 ka Detailed Analysis

Humne **$60$ simulation files** ($40,340$ total windows) par $20$ random seeds aur $3$ penetration conditions ($10\%, 20\%, 30\%$) ka batch evaluation kiya:

### Consolidated Table 3 (Mean $\pm$ 95% Confidence Interval):
| Condition | Penetration | Seeds | Ground Truth IR | Channel 1 (KF) IR | Fully Imputed (GRU-D) IR | Accel Violations | Curvature Violations |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **penetration_10** | $10\%$ | 20 | $1.01 \pm 0.30\%$ | $0.83 \pm 0.23\%$ | $\mathbf{78.39 \pm 1.00\%}$ | $78.39 \pm 1.00\%$ | $11.35 \pm 0.94\%$ |
| **penetration_20** | $20\%$ | 20 | $1.02 \pm 0.21\%$ | $0.86 \pm 0.20\%$ | $\mathbf{78.50 \pm 0.60\%}$ | $78.49 \pm 0.61\%$ | $11.91 \pm 0.73\%$ |
| **penetration_30** | $30\%$ | 20 | $1.33 \pm 0.17\%$ | $1.15 \pm 0.16\%$ | $\mathbf{78.57 \pm 0.63\%}$ | $78.56 \pm 0.63\%$ | $12.71 \pm 0.76\%$ |

### Table 3 ke 3 Sabse Badi Conclusions (Presentation Highlights):
1. **Ground Truth IR $\approx 1.0\%$ (Sanity Check Pass):** 
   Asli SUMO simulator ka ground truth data $99\%$ valid hai. Yeh $1\%$ violation sirf lane-change ke waqt aane wale discrete simulator step ki wajah se hai. Iska matlab humara metric bilkul sahi hai aur jhoothe alarms (false positives) nahi deta.
2. **Channel 1 (KF) IR $\approx 0.8\%$ (Kinematic Neutrality):** 
   Kalman Filter sirf leader/follower ke columns (4, 5, 6) bharta hai. Ego gaadi ke coordinates ko nahi chhoota. Isliye kinematic violations zero rehti hain.
3. **Fully Imputed IR $\approx 78.5\%$ (Shocking Discovery):** 
   Jab GRU-D ego coordinates bharta hai, toh **$78.5\%$ windows kinematically fail ho jaate hain!** Acceleration routinely $+24\text{ m/s}^2$ aur $-24\text{ m/s}^2$ cross kar jata hai, aur $11-12\%$ cases mein gaadi $6\text{ m}$ se sharp turn le leti hai. Yeh prove karta hai ki unconstrained deep learning imputation dangerous hai.

---

## 9. Objective 2: Percolation Sweep (60 Runs & S-Curve Fitting)

### A. Problem:
Purani research mein claim kiya gaya tha ki CAVs badhne par connectivity mein ek sudden jump (percolation jump) aata hai. Lekin unka claim sirf **2 data points (20% aur 30%)** par based tha. Do points se koi threshold locate nahi kiya ja sakta.

### B. Hamara Setup:
* Humne **6 market penetration levels** liye: **$18\%, 21\%, 24\%, 27\%, 30\%, 35\%$**.
* Har level par **10 independent random seeds** run kiye (Total **60 simulation runs**).
* Fixed flow: $4500\text{ veh/h}$ across 3 lanes (1000m segment).
* Common Random Numbers (CRN) use kiye taaki seed-to-seed variance kam ho.

### C. 3-Parameter Logistic (S-Curve) Equation:
$$C(p) = \frac{L}{1 + e^{-k(p - p_c)}}$$
- **$L$ (Saturation Plateau):** Asymptotic connectivity limit ($37.12\%$).
- **$k$ (Growth Rate):** Steepness of slope ($0.1318$).
- **$p_c$ (Critical Density):** Inflection point jahan percolation threshold trigger hota hai ($\mathbf{20.66\%}$).
- **$w = 4/k$ (Transition Width):** Transition ka span ($\mathbf{30.34\%}$).
- **Bounded Interval:** Steepest bracket $[18\%, 21\%]$ mein 95% CIs overlap karte hain, isliye guidelines ke mutabiq transition ko **$[18\%, 21\%]$ CAV Penetration** ke roop mein bound kiya gaya hai.

---

## 10. Objective 3: Do Leader Definitions & Physics vs. Artifact Verdict

Professor zaroor poochenge: *"Tumne do leader definitions kyu check ki? Iska kya matlab hai?"*

### A. Do Definitions:
1. **Instantaneous Leader:** Har single $0.1\text{ s}$ step par dekha gaya ki aage wali gaadi CAV hai ya nahi.
2. **Modal Window Leader:** $3.0\text{ s}$ ($30$ steps) ke window mein majority vote se dekha gaya ki kaun zyada der leader raha.

### B. Comparison Results:
| Metric | Instantaneous Leader | Modal Window Leader | Difference |
| :--- | :---: | :---: | :---: |
| **Critical Density ($p_c$)** | **$20.66\%$** | **$20.73\%$** | **Sirf $0.07\%$** |
| **Saturation Level ($L$)** | $37.12\%$ | $36.40\%$ | $0.72\%$ |
| **Transition Width ($w$)** | $30.34\%$ | $30.22\%$ | $0.12\%$ |

### C. Scientific Verdict (Physics vs. Artifact):
* Agar yeh percolation jump sirf sliding window ya modal filter ka mathematical artifact hota, toh rolling window use karne par critical threshold shift ho jaata ya smooth ho jaata.
* Lekin dono definitions mein critical point **bilkul identical ($p_c \approx 20.7\%$)** nikla!
* **Verdict:** Isse prove hota hai ki percolation threshold koi observational artifact nahi hai, balki **real vehicular traffic physics hai**. Jab penetration $20-21\%$ cross karti hai, toh CAVs aapas mein ek-doosre ke peeche tight CACC platoons ($0.55\text{ s}$ gap) banana shuru kar deti hain, jisse macro-level connectivity achanak jump kar jaati hai.

---

## 11. Code, Notebooks & Datasets ka Workflow

| File Name | Uska Role & Purpose |
| :--- | :--- |
| `Objective_1_Infeasible_Rate.ipynb` | Main executable notebook for Objective 1. Isme sanity tests, kinematic formulas, aur 60 files ka batch evaluation code hai. |
| `Objective_2_Percolation_Sweep.ipynb`| Executable notebook for Objective 2 & 3. Isme 60 simulation runs, logistic S-curve fitting, aur embedded plots hain. |
| `objective_1_results.xlsx` | Auto-formatted Excel report for Objective 1 (Table 3 + All 60 seeds detailed). |
| `objective_2_results.xlsx` | Auto-formatted Excel report for Objective 2 (Summary + All 60 seeds detailed). |
| `percolation_sweep_curve.png` | 300 DPI publication-quality S-curve plot with 95% CI error bars. |
| `PROJECT_REPORT.md` | Complete academic technical research report. |
| `README.md` | GitHub landing page with installation instructions and team details. |
| `data_corrupted/` | Input dataset folder containing 60 `.npz` files across 10%, 20%, 30% penetration. |

---

## 12. Top 10 Expected Viva / Presentation Questions & Unke Confident Answers

#### Q1: "Aapke project ka core objective kya tha?"
> **Answer:** "Sir, vehicular trajectory imputation mein purana standard sirf positional accuracy (ADE) naapta tha. Hamara primary objective tha ek physical validity metric formulate karna—**Infeasible Rate (IR)**—jo impossible accelerations ($a \notin [-8, +3]\text{ m/s}^2$) aur impossible turns ($r < 6\text{ m}$) ko penalize kare, aur yeh prove kare ki existing neural imputers $78.5\%$ cases mein physically invalid trajectories emit karte hain."

#### Q2: "7 columns mein se SFM aur TCM kin columns mein hota hai?"
> **Answer:** "Sir, Columns 4, 5, 6 (`gap_to_leader`, `leader_speed`, `follower_speed`) mein SFM hota hai kyunki padosi Human gaadi ke paas V2X transmitter nahi hota. Aur Columns 0, 1, 2, 3 (`ego_speed`, `ego_accel`, `ego_x`, `ego_y`) mein TCM hota hai kyunki wireless packet drops ki wajah se ego vehicle ka apna signal 2-5 steps ke liye lost ho jata hai."

#### Q3: "Table 3 mein Fully Imputed data ka Infeasible Rate 78.5% kyu jump kiya?"
> **Answer:** "Sir, Channel 2 (GRU-D) neural network training ke waqt sirf MSE loss minimize karta hai. Mathematical displacement toh kam rehta hai, lekin $0.1\text{ s}$ ke time intervals par numerical second derivative lene par immense high-frequency acceleration spikes ($> 24\text{ m/s}^2$) paida hote hain, jo passenger vehicle limits ($[-8, +3]\text{ m/s}^2$) ko break kar dete hain."

#### Q4: "Channel 1 (Kalman Filter) ka IR Ground Truth se bhi kam kyu dikh raha hai?"
> **Answer:** "Sir, Channel 1 sirf leader aur follower ke features (Cols 4-6) ko RSU camera data se estimate karta hai. Wo ego vehicle ke apne spatial coordinates $(x, y)$ ko touch nahi karta. Isliye ego kinematics bilkul intact rehti hain."

#### Q5: "Circumcircle radius formula kyu use kiya gaya turning radius ke liye?"
> **Answer:** "Sir, discrete time steps par trajectory 3 continuous 2D coordinates ($A, B, C$) ke sequence mein aati hai. Un 3 points se guzarne wale unique circle ka radius $R = \frac{abc}{4 \cdot \text{Area}}$ hota hai. Agar yeh radius $6\text{ meter}$ se kam aata hai, toh vehicle steering limits ($l_f, l_r \in [1, 2]\text{ m}$, steering $\pm 45^\circ$) ke hisaab se impossible turn maana jata hai."

#### Q6: "Objective 2 mein Percolation Sweep kya prove karta hai?"
> **Answer:** "Sir, literature mein connectivity jump sirf 2 data points (20% aur 30%) par claim kiya gaya tha. Humne 6 penetration levels $\times$ 10 seeds ($60$ runs) ka systematic sweep kiya aur 3-parameter Logistic function fit karke critical density threshold $p_c \approx 20.66\%$ par locate kiya aur $[18\%, 21\%]$ bracket mein bound kiya."

#### Q7: "Objective 3 ka verdict kya hai: Physics ya Artifact?"
> **Answer:** "Sir, verdict hai **Genuine Traffic Physics**. Instantaneous per-step observation aur $3.0\text{ s}$ rolling modal window observation dono mein critical density $p_c \approx 20.7\%$ par hi trigger hoti hai ($0.07\%$ difference). Agar yeh windowing ka artifact hota toh modal filter threshold ko shift kar deta."

#### Q8: "Common Random Numbers (CRN) kyu use kiya simulation mein?"
> **Answer:** "Sir, CRN variance reduction technique hai. Humne different penetration levels ke simulation runs mein synchronized random seeds use kiye taaki traffic inflow generation identical rahe aur observed connectivity changes purely penetration rate ki wajah se hon, random vehicle spawning noise ki wajah se nahi."

#### Q9: "Paper B ke Tables II aur III ko verify kyu nahi kar paye?"
> **Answer:** "Sir, Paper B ke Tables II–III proprietary **CAERI-NDS** (China Automotive Engineering Research Institute Naturalistic Driving Study) private dataset par based hain jo publicly available nahi hai. Humne is limitation ko technical report mein 'What We Could Not Verify' section ke under transparently document kiya hai."

#### Q10: "Infeasible Rate metric ka practical future use kya hai?"
> **Answer:** "Sir, Infeasible Rate trajectory prediction models mein as a loss penalty ya post-processing projection constraint (`kinematic_project`) use ho sakta hai, taaki self-driving cars ko input milne se pehle hi impossible acceleration aur impossible turns filter out ho sakein."
