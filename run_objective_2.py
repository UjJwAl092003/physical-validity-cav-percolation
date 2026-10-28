# ==============================================================================
# OBJECTIVE 2: PERCOLATION SWEEP & OBJECTIVE 3: CONNECTIVITY DEFINITIONS
# Characterising the SFM Percolation Threshold in CACC Mixed Traffic
# ==============================================================================

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.optimize import curve_fit

# Configure clean UTF-8 output
sys.stdout.reconfigure(encoding='utf-8')

print("Starting Objective 2 & 3 Simulation and Analysis Pipeline...")

def simulate_percolation_run(p_cav, seed, segment_length=1000.0, duration=150.0, warmup=30.0, dt=0.1, flow_veh_per_h=4500):
    """
    Simulates mixed-autonomy highway traffic on a 3-lane, 1000m segment at fixed flow.
    Authoritative parameters from project specification:
      - Flow: 4500 veh/h (1500 veh/h/lane)
      - Segment length: 1000 m, 3 lanes
      - Speed limit: 33.33 m/s (120 km/h)
      - Acceleration bounds: [-8.0, +3.0] m/s^2
      - CAV CACC car-following: minGap = 1.0 m, t_headway = 0.55 s
      - HDV Krauss/IDM car-following: minGap = 2.5 m, t_headway = 1.45 s
    """
    np.random.seed(seed)
    num_lanes = 3
    flow_per_lane_per_sec = (flow_veh_per_h / num_lanes) / 3600.0
    spawn_prob_per_step = flow_per_lane_per_sec * dt
    
    lanes = [[] for _ in range(num_lanes)]
    veh_id_counter = 0
    
    inst_cav_leader_steps = 0
    inst_any_leader_steps = 0
    
    cav_windows = []
    cav_rolling_history = {}
    
    total_steps = int(duration / dt)
    warmup_steps = int(warmup / dt)
    
    for step in range(total_steps):
        is_measuring = (step >= warmup_steps)
        
        # 1. Inflow: Spawn vehicles across 3 lanes
        for l in range(num_lanes):
            if len(lanes[l]) == 0 or lanes[l][-1]['x'] > 14.0:
                if np.random.random() < spawn_prob_per_step:
                    is_cav = (np.random.random() < p_cav)
                    v_type = 'CAV' if is_cav else 'HDV'
                    
                    veh = {
                        'id': veh_id_counter,
                        'type': v_type,
                        'x': 0.0,
                        'v': 31.0 + np.random.uniform(-1.0, 1.0),
                        'lane': l
                    }
                    lanes[l].append(veh)
                    if is_cav:
                        cav_rolling_history[veh_id_counter] = []
                    veh_id_counter += 1
                    
        # 2. Update Kinematics & Platoon Formation
        for l in range(num_lanes):
            lane_vehs = lanes[l]
            n_vehs = len(lane_vehs)
            
            for i in range(n_vehs):
                veh = lane_vehs[i]
                leader = lane_vehs[i - 1] if i > 0 else None
                
                # Measure connectivity during steady-state
                if veh['type'] == 'CAV' and is_measuring:
                    if leader is not None:
                        inst_any_leader_steps += 1
                        if leader['type'] == 'CAV':
                            inst_cav_leader_steps += 1
                        lead_type = leader['type']
                    else:
                        lead_type = 'none'
                        
                    cav_rolling_history[veh['id']].append(lead_type)
                    # 30-step (3.0s) sliding window
                    if len(cav_rolling_history[veh['id']]) == 30:
                        cav_windows.append(list(cav_rolling_history[veh['id']]))
                        cav_rolling_history[veh['id']].pop(0)
                        
                # Longitudinal Acceleration Dynamics
                if leader is None:
                    accel = min(1.5, (33.33 - veh['v']) / 2.0)
                else:
                    gap = leader['x'] - veh['x'] - 4.5
                    is_cacc_pair = (veh['type'] == 'CAV' and leader['type'] == 'CAV')
                    
                    min_gap = 1.0 if is_cacc_pair else 2.5
                    t_headway = 0.55 if is_cacc_pair else 1.45
                    desired_gap = min_gap + veh['v'] * t_headway
                    
                    # IDM / CACC acceleration
                    accel = 2.0 * (1.0 - (veh['v'] / 33.33)**4 - (desired_gap / max(gap, 0.5))**2)
                    accel = np.clip(accel, -8.0, 3.0)  # Bound by authoritative [-8, +3] m/s^2
                    
                veh['v'] = max(0.0, veh['v'] + accel * dt)
                veh['x'] += veh['v'] * dt
                
            lanes[l] = [v for v in lane_vehs if v['x'] < segment_length]
            
    inst_connectivity = (inst_cav_leader_steps / max(1, inst_any_leader_steps)) * 100.0
    
    modal_connected_count = 0
    total_valid_windows = 0
    for win in cav_windows:
        leaders_in_win = [x for x in win if x != 'none']
        if len(leaders_in_win) > 0:
            total_valid_windows += 1
            if leaders_in_win.count('CAV') > len(leaders_in_win) / 2.0:
                modal_connected_count += 1
                
    modal_connectivity = (modal_connected_count / max(1, total_valid_windows)) * 100.0
    return inst_connectivity, modal_connectivity

penetration_levels = [0.18, 0.21, 0.24, 0.27, 0.30, 0.35]
num_seeds = 10

sweep_records = []
summary_table_data = []

print(f"Executing Percolation Sweep: {len(penetration_levels)} levels x {num_seeds} seeds = 60 simulation runs...")

for p in penetration_levels:
    p_pct = int(round(p * 100))
    inst_runs = []
    modal_runs = []
    
    for s in range(1, num_seeds + 1):
        # Common Random Numbers (CRN) across seeds for rigorous variance reduction
        seed_val = s * 1000
        inst_c, mod_c = simulate_percolation_run(p, seed=seed_val)
        inst_runs.append(inst_c)
        modal_runs.append(mod_c)
        
        sweep_records.append({
            'Penetration (%)': p_pct,
            'Seed': s,
            'Instantaneous_Conn (%)': round(inst_c, 2),
            'Modal_Conn (%)': round(mod_c, 2)
        })
        
    def calc_ci95(data_list):
        mean_val = np.mean(data_list)
        std_val = np.std(data_list, ddof=1)
        ci_val = 1.96 * (std_val / np.sqrt(len(data_list)))
        return mean_val, std_val, ci_val

    inst_mean, inst_std, inst_ci = calc_ci95(inst_runs)
    mod_mean, mod_std, mod_ci = calc_ci95(modal_runs)
    
    summary_table_data.append({
        'Penetration (%)': p_pct,
        'Seeds': num_seeds,
        'Inst_Mean': round(inst_mean, 2),
        'Inst_Std': round(inst_std, 2),
        'Inst_CI95': round(inst_ci, 2),
        'Inst_Reported': f"{inst_mean:.2f} ± {inst_ci:.2f}",
        'Modal_Mean': round(mod_mean, 2),
        'Modal_Std': round(mod_std, 2),
        'Modal_CI95': round(mod_ci, 2),
        'Modal_Reported': f"{mod_mean:.2f} ± {mod_ci:.2f}"
    })
    print(f"  Penetration {p_pct}% -> Inst: {inst_mean:.2f} ± {inst_ci:.2f}%, Modal: {mod_mean:.2f} ± {mod_ci:.2f}%")

df_sweep_all = pd.DataFrame(sweep_records)
df_summary = pd.DataFrame(summary_table_data)

# Save datasets with UTF-8 BOM encoding for seamless Excel rendering
df_summary.to_csv('objective_2_percolation_summary.csv', index=False, encoding='utf-8-sig')
df_sweep_all.to_csv('objective_2_percolation_all_seeds.csv', index=False, encoding='utf-8-sig')
print("Percolation sweep datasets saved to CSV (utf-8-sig).")

# 3-Parameter Logistic Fit
def logistic_model(p, L, k, p0):
    return L / (1.0 + np.exp(-k * (p - p0)))

p_vals = np.array([r['Penetration (%)'] for r in summary_table_data])
y_inst = np.array([r['Inst_Mean'] for r in summary_table_data])
y_modal = np.array([r['Modal_Mean'] for r in summary_table_data])

popt_inst, _ = curve_fit(logistic_model, p_vals, y_inst, p0=[40.0, 0.2, 22.0], bounds=([30.0, 0.05, 18.0], [60.0, 1.0, 32.0]))
L_inst, k_inst, pc_inst = popt_inst
width_inst = 4.0 / k_inst

popt_modal, _ = curve_fit(logistic_model, p_vals, y_modal, p0=[40.0, 0.2, 22.0], bounds=([30.0, 0.05, 18.0], [60.0, 1.0, 32.0]))
L_modal, k_modal, pc_modal = popt_modal
width_modal = 4.0 / k_modal

# Check Steepest Slope and 95% CI Overlap for Bounded Interval reporting
slopes = np.diff(y_inst) / np.diff(p_vals)
max_slope_idx = np.argmax(slopes)
p_lower = p_vals[max_slope_idx]
p_upper = p_vals[max_slope_idx + 1]

ci_lower_high = summary_table_data[max_slope_idx]['Inst_Mean'] + summary_table_data[max_slope_idx]['Inst_CI95']
ci_upper_low = summary_table_data[max_slope_idx + 1]['Inst_Mean'] - summary_table_data[max_slope_idx + 1]['Inst_CI95']
ci_overlap = ci_lower_high >= ci_upper_low

print("\n" + "="*78)
print("PERCOLATION THRESHOLD & TRANSITION PARAMETERS")
print("="*78)
print(f"1. Instantaneous Leader Definition:")
print(f"   - Saturation Level (L)        : {L_inst:.2f}%")
print(f"   - Critical Density (p_c)      : {pc_inst:.2f}% CAV Penetration")
print(f"   - Growth Rate (k)             : {k_inst:.4f}")
print(f"   - Transition Width (4/k)      : {width_inst:.2f}%")
print(f"\n2. Modal Leader Definition:")
print(f"   - Saturation Level (L)        : {L_modal:.2f}%")
print(f"   - Critical Density (p_c)      : {pc_modal:.2f}% CAV Penetration")
print(f"   - Growth Rate (k)             : {k_modal:.4f}")
print(f"   - Transition Width (4/k)      : {width_modal:.2f}%")
print(f"\n3. Statistical Interval & Bounding Analysis:")
print(f"   - Steepest Slope Bracket      : [{p_lower}%, {p_upper}%]")
print(f"   - 95% CI Overlap Detected     : {ci_overlap}")
if ci_overlap:
    print(f"   - Bounded Transition Interval : [{p_lower}%, {p_upper}%] CAV Penetration")
else:
    print(f"   - Critical Density Located At : {pc_inst:.2f}% CAV Penetration")
print("="*78)

# Table Output
table_display = df_summary[['Penetration (%)', 'Seeds', 'Inst_Reported', 'Modal_Reported']].copy()
table_display.columns = ['Penetration (%)', 'Seeds', 'Instantaneous Conn (%) [Mean ± 95% CI]', 'Modal Conn (%) [Mean ± 95% CI]']
print("\n" + "="*85)
print("TABLE: CAV-TO-CAV LEADER CONNECTIVITY VS PENETRATION RATE")
print("="*85)
print(table_display.to_string(index=False))
print("="*85)

# Generate Publication-Quality Figure
plt.figure(figsize=(10, 6.2), dpi=300)
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
p_dense = np.linspace(16, 38, 200)

plt.plot(p_dense, logistic_model(p_dense, *popt_inst), 'b-', linewidth=2.5, 
         label=f'Instantaneous Fit (p_c = {pc_inst:.2f}%, Width = {width_inst:.1f}%)')
plt.plot(p_dense, logistic_model(p_dense, *popt_modal), 'r--', linewidth=2.5, 
         label=f'Modal Fit (p_c = {pc_modal:.2f}%, Width = {width_modal:.1f}%)')

plt.errorbar(p_vals, y_inst, yerr=[r['Inst_CI95'] for r in summary_table_data], 
             fmt='o', color='blue', ecolor='darkblue', elinewidth=2, capsize=5, capthick=1.5,
             markersize=8, label='Instantaneous Empirical Data (Mean ± 95% CI)')
plt.errorbar(p_vals, y_modal, yerr=[r['Modal_CI95'] for r in summary_table_data], 
             fmt='s', color='red', ecolor='darkred', elinewidth=2, capsize=5, capthick=1.5,
             markersize=7, label='Modal Empirical Data (Mean ± 95% CI)')

plt.axvline(pc_inst, color='green', linestyle=':', linewidth=2, label=f'Percolation Threshold p_c ≈ {pc_inst:.2f}%')
plt.axvspan(p_lower, p_upper, color='yellow', alpha=0.15, label=f'Bounded Transition [{p_lower}%, {p_upper}%]')

plt.xlabel('CAV Market Penetration Rate (%)', fontsize=12, fontweight='bold')
plt.ylabel('CAV-to-CAV Leader Connectivity (%)', fontsize=12, fontweight='bold')
plt.title('Percolation Sweep: CAV Connectivity vs Market Penetration in CACC Mixed Traffic', fontsize=13, fontweight='bold')
plt.xlim(16, 38)
plt.ylim(0, 50)
plt.legend(loc='upper left', frameon=True, fontsize=10)
plt.grid(True, linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig('percolation_sweep_curve.png', dpi=300)
plt.close()
print("Saved publication plot: percolation_sweep_curve.png")

# Generate Styled Excel Spreadsheet
with pd.ExcelWriter('objective_2_results.xlsx', engine='openpyxl') as writer:
    df_summary_export = df_summary[['Penetration (%)', 'Seeds', 'Inst_Mean', 'Inst_Std', 'Inst_CI95', 'Inst_Reported',
                                    'Modal_Mean', 'Modal_Std', 'Modal_CI95', 'Modal_Reported']].copy()
    df_summary_export.columns = [
        'Penetration (%)', 'Total Seeds', 
        'Instantaneous Mean (%)', 'Instantaneous Std Dev (%)', 'Instantaneous 95% CI', 'Instantaneous Connectivity (Mean ± 95% CI)',
        'Modal Mean (%)', 'Modal Std Dev (%)', 'Modal 95% CI', 'Modal Connectivity (Mean ± 95% CI)'
    ]
    df_summary_export.to_excel(writer, sheet_name='Summary_Table', index=False)
    
    df_sweep_all_export = df_sweep_all.copy()
    df_sweep_all_export.columns = ['Penetration Level (%)', 'Seed Number', 'Instantaneous Leader Conn (%)', 'Modal Leader Conn (%)']
    df_sweep_all_export.to_excel(writer, sheet_name='All_60_Seeds_Detailed', index=False)
    
    # Auto-adjust column widths
    for sheet in writer.sheets.values():
        for col in sheet.columns:
            max_len = max(len(str(cell.value or '')) for cell in col)
            col_letter = col[0].column_letter
            sheet.column_dimensions[col_letter].width = max(max_len + 5, 16)

print("Excel sheet objective_2_results.xlsx successfully created.")
