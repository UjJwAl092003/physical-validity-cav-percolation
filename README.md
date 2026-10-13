# Physical Validity Metric for Imputed Vehicle State and SFM Percolation Threshold in CACC Mixed Traffic

## Team (Group 7)

| Name | Roll No. |
|---|---|
| Ujjwal Singh | 262IS036 |
| Siddharth Patidar | 262CS031 |
| Sagar Kushwah | 262CS025 |
| Dev | 252IS011 |

Contact: devcbhatt.252is011@nitk.edu.in

## Status

We met our project guide on 9th October. Since then we have been reading the problem statement and understanding what has to be built. No results yet. Progress is noted day by day in the log at the bottom.

## What this project is about

Connected autonomous vehicles (CAVs) send their speed, position and acceleration 10 times every second. A predictor uses the last 3 seconds of this data (30 steps) to guess where the vehicle will be in the next 5 seconds (50 steps).

The problem is that most vehicles on the road are normal human driven vehicles (HDVs). They send nothing, so the CAV has no data about them. Also, wireless signals sometimes drop for a few steps, which leaves small gaps in the CAV's own data.

So the data going into the predictor has holes, and the project fills those holes before the prediction happens. This filling of missing data is called imputation.

There are two types of missing data:

| Type | What it means | Where it shows up |
|---|---|---|
| SFM (Structural Feature Missingness) | The vehicle ahead or behind is a human driven one, so its data never existed | Last 3 columns: gap to leader, leader speed, follower speed |
| TCM (Temporal Cluster Missingness) | Signal drops for a short burst of 2 to 5 steps | The CAV's own columns: speed, acceleration, x, y |

Each input window is 30 steps long with 7 columns: ego speed, ego acceleration, ego x, ego y, gap to leader, leader speed, follower speed.

The instructor shared a reference plan that explains the whole pipeline. In short, a roadside camera (RSU) can see human vehicles and a Kalman Filter cleans its readings to fill the SFM columns. A neural network (GRU D) fills the short gaps in the CAV's own data. The predictor is an LSTM. We are using this plan only to understand the problem. We are not building all of it.

## Basic terms

| Term | Meaning |
|---|---|
| Trajectory | The path of a vehicle over time |
| ADE | Average Displacement Error. How far the predicted positions are from the real ones on average. Lower is better |
| CAV | Connected Autonomous Vehicle |
| HDV | Human Driven Vehicle |
| CACC | A system that lets a vehicle follow the one ahead smoothly using wireless communication. It works best when the vehicle ahead is also a CAV |
| Leader | The vehicle right in front |
| Penetration | Percentage of CAVs among all vehicles on the road |
| Percolation | A sudden jump in connectivity when small groups join into big ones as density increases. It looks like an S shaped curve |
| Seed | A random number setting. A different seed gives a different random simulation run |
| 95% CI | Error bar around an average |

## The two gaps we are addressing

**Gap 1: No check for physical validity.**
Right now only position accuracy (ADE) is reported. A method can have a good ADE and still produce motion that no real vehicle could do, like a turn with 2 m radius or braking at 15 m/s². We need a metric that catches this.

**Gap 2: Weak percolation claim.**
The claim is that CAV to CAV leader connectivity jumps suddenly as CAV percentage increases. But this is based on only two data points. Two points always fit a straight line, so they cannot tell us where the jump is, or if there is a jump at all. They also cannot tell us if the jump comes from how we define "leader".

## Fixed parameters

These values are final. If another document gives different numbers, these are the ones to use.

| Parameter | Value |
|---|---|
| Acceleration limits | minus 8 to plus 3 m/s² |
| Steering | up to 45 degrees on either side |
| Wheelbase l_f and l_r | between 1 and 2 m |
| Infeasible turning radius | less than 6 m (radius = 1 / curvature) |
| Traffic flow | 4500 vehicles per hour, 1000 m road, 3 lanes, speed limit 33.33 m/s |

## Objectives

We are currently working on Objectives 1, 2 and 3.

### Objective 1: Infeasible Rate (IR)

This is the main and mandatory objective. We check how many imputed windows are physically impossible. It needs no new simulation and no training, only calculation on outputs that already exist, for all seven E1 conditions.

A window is called infeasible if it breaks either rule:
1. The turning radius goes below 6 m.
2. The acceleration goes outside the range minus 8 to plus 3 m/s².

How we get acceleration from positions (time step dt = 0.1 s):

- speed = distance between two consecutive positions divided by dt
- acceleration = change in speed divided by dt

Example: positions along a straight road are 0, 3.0, 6.0, 9.0 and 11.8 m. Speeds are 30, 30, 30 and 28 m/s. The last step has acceleration (28 minus 30) / 0.1 = minus 20 m/s². That is far below minus 8, so it is infeasible.

How we get turning radius from three consecutive points A, B, C:

radius = (AB × BC × AC) / (4 × area of triangle ABC)

Example: A = (0, 0), B = (1, 0), C = (1, 1). AB = 1, BC = 1, AC = 1.414 and the area is 0.5. So radius = 1.414 / 2 = 0.707 m, which is below 6 m, so it is infeasible.

Infeasible Rate = infeasible windows / total windows. For example, 3 bad windows out of 10 gives IR = 30%.

Why this is useful: a simple interpolation method may have ADE 0.8 m but IR 35%, while a physics aware method may have ADE 1.1 m but IR 2%. Looking at ADE alone would pick the first one, but IR shows that it produces impossible motion.

Before trusting our code, we will run it on the clean SUMO ground truth data. That data comes from real simulated vehicles, so IR should come out close to 0%.

The result goes into Table 3 as a new IR column.

### Objective 2: Percolation sweep

We run the SUMO simulation with CAV percentages of 18, 21, 24, 27, 30 and 35%. Each level is run with 10 different seeds, so 60 runs in total, keeping traffic flow fixed.

Connectivity here means the share of CAVs whose leader is also a CAV.

Small example, one lane with H for human and C for CAV:

Cars from front to back: H C H H C C H C H H

There are 4 CAVs. Only the 6th car has a CAV in front of it, so connectivity is 1 out of 4, which is 25%.

For each level we take the average and a 95% confidence interval. Then we fit a logistic (S shaped) curve to find two things: the critical density (where the jump happens) and the transition width (how sharp the jump is).

If the error bars at the steepest part still overlap, we run 10 more seeds at the two levels around it, only once. If they still overlap after that, we do not claim an exact point. We say the transition lies between X and Y.

### Objective 3: Two definitions of leader

A vehicle's leader can change during a window because of overtaking and lane changes. So we measure connectivity in two ways:

1. **Modal leader:** whichever vehicle was the leader most often in the window.
2. **Instantaneous leader:** the leader at every single time step.

Example: for 5 steps, a CAV's leader is CAV, CAV, Human, Human, Human. With the modal definition, the leader is Human (3 out of 5), so this window counts as not connected. With the instantaneous definition, 2 out of 5 steps had a CAV leader, so it is 40% connected.

How we decide the verdict:
- If the jump shows up at about the same place with both definitions, it is real traffic physics.
- If it shows up with only one, it is an artifact of how we measured. In that case we add a third definition: the fraction of the window that had a CAV leader.

We will write a short verdict at the end.

### Objective 4: Kinematic projection (later)

We will write a function `kinematic_project(state_seq, dt, l_f, l_r)` that fixes an impossible trajectory so that it becomes possible and still ends at the position where the vehicle was actually seen after the gap.

The vehicle is modelled as a bicycle (one front wheel, one rear wheel). The method:
1. Start from the last known state before the gap and move the bicycle model forward step by step, keeping acceleration and steering within limits.
2. Check how far the end point is from the real observation after the gap. This difference is the terminal mismatch.
3. Spread this difference over the gap steps. A step with more room before hitting its limits takes a bigger share.
4. Check again that no step breaks the limits.

Example: a mismatch of 2.0 m over 5 steps with room values 1, 1, 2, 4, 2 gives corrections of 0.2, 0.2, 0.4, 0.8 and 0.4 m, which add up to 2.0 m.

Some gaps cannot be repaired at all, for example a 50 m mismatch within 0.3 seconds. In that case the function should say so clearly and not return a wrong answer silently.

We will test it by taking a feasible trajectory, injecting a violation (like a sudden speed drop or a sharp heading change), and checking that the output has no violations, keeps the same starting point, and leaves already feasible input unchanged. We will also test with wheelbases of 1 m and 2 m.

## Data and tools

Given by the instructor: the highD dataset, a generated dataset where the last three columns are corrupted, and the reference plan PDF.

Tools: SUMO with TraCI, Python 3.10 or above, NumPy, SciPy, Matplotlib, Git.

Raw data files are not uploaded to this repository.

## What we could not verify

Tables II and III of Paper B are based on the private CAERI NDS dataset, which we do not have. So we cannot reproduce or check those tables ourselves.

## Progress log

| Date | What we did |
|---|---|
| 9 Oct 2026 | Met our project guide and received the problem statement. Understood the two gaps and the four objectives. |
| 10 Oct 2026 | Understood Infeasible Rate with worked examples. Understood the percolation sweep, what CAV, CACC, leader and connectivity mean, and the two leader definitions. |
| 11 Oct 2026 | Understood the kinematic projection method and how to test it. Wrote a mail to the mentor with our queries and GitHub ID. |
| 12 Oct 2026 | Read the Moodle submission rules. Read the reference plan (SFM, TCM, RSU, Kalman Filter, GRU D and the existing literature). Wrote this README. |
