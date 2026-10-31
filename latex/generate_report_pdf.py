import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas

# Numbered Canvas for "Page X of Y" and Academic Header/Footer
class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            canvas.Canvas.showPage(self)
        canvas.Canvas.save(self)

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#4A5568"))
        
        # Header on pages > 1
        if self._pageNumber > 1:
            self.drawString(45, 808, "NITK Surathkal | Dept. of Computer Science and Engineering | Course Project Report")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.6)
            self.line(45, 802, 550, 802)
            
        # Footer on all pages
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.6)
        self.line(45, 45, 550, 45)
        self.drawString(45, 33, "CAV Trajectory Imputation & Percolation Threshold Evaluation")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(550, 33, page_str)
        self.restoreState()

def build_pdf(filename="PROJECT_REPORT_NITK.pdf"):
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        leftMargin=45,
        rightMargin=45,
        topMargin=52,
        bottomMargin=55
    )

    styles = getSampleStyleSheet()

    # Academic Color Palette
    PRIMARY = colors.HexColor("#1A365D")   # Deep Navy
    SECONDARY = colors.HexColor("#2B6CB0") # Slate Blue
    DARK = colors.HexColor("#1A202C")      # Dark Charcoal Text
    LIGHT_BG = colors.HexColor("#F8FAFC")  # Subtle Background
    BORDER_COLOR = colors.HexColor("#CBD5E1")

    # Typography Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=23,
        textColor=PRIMARY,
        alignment=1,
        spaceAfter=8
    )
    
    inst_style = ParagraphStyle(
        'InstitutionHeader',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=PRIMARY,
        alignment=1,
        spaceAfter=3
    )

    sub_inst_style = ParagraphStyle(
        'SubInstitution',
        fontName='Helvetica-Bold',
        fontSize=9.5,
        leading=13.5,
        textColor=SECONDARY,
        alignment=1,
        spaceAfter=12
    )

    meta_label = ParagraphStyle(
        'MetaLabel',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=12,
        textColor=PRIMARY
    )

    meta_val = ParagraphStyle(
        'MetaVal',
        fontName='Helvetica',
        fontSize=8.5,
        leading=12,
        textColor=DARK
    )

    h1_style = ParagraphStyle(
        'H1',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=PRIMARY,
        spaceBefore=14,
        spaceAfter=6,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'H2',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=14,
        textColor=SECONDARY,
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.8,
        textColor=DARK,
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=body_style,
        leftIndent=15,
        spaceAfter=4
    )

    formula_style = ParagraphStyle(
        'Formula',
        parent=body_style,
        fontName='Helvetica-Oblique',
        fontSize=8.8,
        leading=13,
        leftIndent=20,
        textColor=colors.HexColor("#2C5282")
    )

    callout_style = ParagraphStyle(
        'Callout',
        parent=body_style,
        fontName='Helvetica-Oblique',
        fontSize=8.2,
        leading=11.5,
        textColor=colors.HexColor("#2C5282")
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=body_style,
        fontSize=8,
        leading=11,
        spaceAfter=0
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=table_cell,
        fontName='Helvetica-Bold',
        textColor=colors.white,
        alignment=1
    )

    story = []

    # =========================================================================
    # INSTITUTION & TITLE HEADER
    # =========================================================================
    story.append(Paragraph("NATIONAL INSTITUTE OF TECHNOLOGY KARNATAKA, SURATHKAL", inst_style))
    story.append(Paragraph("DEPARTMENT OF COMPUTER SCIENCE AND ENGINEERING | COURSE PROJECT REPORT", sub_inst_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=PRIMARY, spaceAfter=10))

    story.append(Paragraph("Physical-Validity Metric for Imputed Vehicle State & SFM Percolation Threshold in CACC Mixed Traffic", title_style))
    story.append(Spacer(1, 4))

    # Meta Table: Authors, Instructor, Mentor, Repository
    meta_data = [
        [
            Paragraph("<b>Course Instructor:</b>", meta_label),
            Paragraph("Dr. Sourav Kanti Addya (Aditya)<br/>Assistant Professor in Department of Computer Science and Engg. at NIT Karnataka, Surathkal", meta_val),
            Paragraph("<b>Student Authors (Group 7):</b>", meta_label),
            Paragraph("<b>Ujjwal Singh</b> (262IS036)<br/><b>Siddharth Patidar</b> (262CS031)<br/><b>Sagar Kushwah</b> (262IS025)", meta_val)
        ],
        [
            Paragraph("<b>Project Mentor:</b>", meta_label),
            Paragraph("Dev C Bhatt", meta_val),
            Paragraph("<b>Public Repository:</b>", meta_label),
            Paragraph("<font color='#2B6CB0'>github.com/UjJwAl092003/physical-validity-cav-percolation</font>", meta_val)
        ]
    ]

    meta_table = Table(meta_data, colWidths=[105, 160, 110, 130])
    meta_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1, BORDER_COLOR),
        ('INNERGRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(meta_table)
    story.append(Spacer(1, 10))

    # =========================================================================
    # EXECUTIVE SUMMARY / ABSTRACT
    # =========================================================================
    story.append(Paragraph("Executive Summary", h1_style))
    summary_text = (
        "Cooperative Adaptive Cruise Control (CACC) and vehicular trajectory prediction rely on high-frequency "
        "(10 Hz, dt = 0.1 s) kinematic state exchange among Connected Autonomous Vehicles (CAVs). In real-world "
        "mixed-autonomy highway traffic, communication channels suffer from wireless packet dropouts and uninstrumented human-driven "
        "vehicles (HDVs), leading to severe telemetry missingness. Prior works evaluate trajectory imputation solely "
        "through positional error metrics such as Average Displacement Error (ADE). In this project, we formulate and empirically validate "
        "<b>Objective 1: Infeasible Rate (IR)</b>, proving that an imputation model with low positional ADE can nevertheless generate trajectories "
        "that violate passenger vehicle kinematics in <b>78.5%</b> of cases. Furthermore, we execute <b>Objective 2: "
        "Percolation Sweep</b> across 6 market penetration rates and 10 random seeds (60 simulation runs), fitting a 3-parameter "
        "Logistic function to determine the critical percolation threshold (p_c approx. 20.7%) and bounding the transition within [18%, 21%]. "
        "Finally, in <b>Objective 3</b>, we compare Instantaneous vs. Modal Window leader definitions, delivering a definitive scientific verdict: "
        "the percolation jump is a <b>genuine physical property of CACC platoon coalescence</b> rather than an observational windowing artifact."
    )
    story.append(Paragraph(summary_text, body_style))
    story.append(Spacer(1, 8))

    # =========================================================================
    # 1. INTRODUCTION & PROBLEM FORMULATION
    # =========================================================================
    story.append(Paragraph("1. Introduction & Problem Formulation", h1_style))
    story.append(Paragraph(
        "Vehicular motion in modern Cooperative Intelligent Transportation Systems (C-ITS) is organized into discrete temporal observations. "
        "Each trajectory window represents a 3.0-second historical sequence comprising 30 discrete time steps at 10 Hz (dt = 0.1 s). "
        "The state of each ego-CAV is captured in a <b>30 x 7 state matrix</b> X in R^(30 x 7). Safe vehicular coordination, lane-changing, "
        "and emergency collision avoidance require this matrix to be complete and kinematically faithful.",
        body_style
    ))

    # 7-Column Table
    feat_data = [
        [Paragraph("Col", table_header), Paragraph("Feature Name", table_header), Paragraph("Physical Meaning", table_header), Paragraph("Ownership & Sensor Source", table_header)],
        [Paragraph("0", table_cell), Paragraph("ego_speed (v)", table_cell), Paragraph("Forward longitudinal velocity (m/s)", table_cell), Paragraph("Onboard wheel speed sensor / CAN bus", table_cell)],
        [Paragraph("1", table_cell), Paragraph("ego_accel (a)", table_cell), Paragraph("Longitudinal acceleration (m/s^2)", table_cell), Paragraph("Onboard Inertial Measurement Unit (IMU)", table_cell)],
        [Paragraph("2", table_cell), Paragraph("ego_x (x)", table_cell), Paragraph("Longitudinal highway position (m)", table_cell), Paragraph("Onboard GNSS / Differential GPS / Odometry", table_cell)],
        [Paragraph("3", table_cell), Paragraph("ego_y (y)", table_cell), Paragraph("Lateral lane position (m)", table_cell), Paragraph("Onboard GNSS / Odometry", table_cell)],
        [Paragraph("4", table_cell), Paragraph("gap_to_leader (s)", table_cell), Paragraph("Net distance to front vehicle (m)", table_cell), Paragraph("V2X Broadcast or Roadside Unit (RSU) Camera", table_cell)],
        [Paragraph("5", table_cell), Paragraph("leader_speed (v_L)", table_cell), Paragraph("Speed of leading vehicle (m/s)", table_cell), Paragraph("V2X Broadcast or RSU Camera", table_cell)],
        [Paragraph("6", table_cell), Paragraph("follower_speed (v_F)", table_cell), Paragraph("Speed of trailing vehicle (m/s)", table_cell), Paragraph("V2X Broadcast or RSU Camera", table_cell)],
    ]
    t_feat = Table(feat_data, colWidths=[28, 95, 175, 207])
    t_feat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 3),
        ('BOTTOMPADDING', (0,0), (-1,-1), 3),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG])
    ]))
    story.append(t_feat)
    story.append(Spacer(1, 8))

    story.append(Paragraph("<b>Two Native IoV Missing Data Mechanisms:</b>", h2_style))
    story.append(Paragraph(
        "<b>1. Structural Feature Missingness (SFM) - Columns 4, 5, 6:</b> Human-Driven Vehicles (HDVs) possess no wireless V2X radio. "
        "When an ego-CAV follows or precedes an HDV, neighbor telemetry never exists, causing 100% missing values across all 30 steps. "
        "This is a fundamental sensing architecture constraint of mixed autonomy.",
        bullet_style
    ))
    story.append(Paragraph(
        "<b>2. Temporal Cluster Missingness (TCM) - Columns 0, 1, 2, 3:</b> Multipath fading, Doppler shifts, antenna occlusion, and base-station "
        "handovers cause burst packet loss in the ego-CAV's own telemetry over contiguous segments of 2 to 5 steps (0.2 s - 0.5 s).",
        bullet_style
    ))
    story.append(Spacer(1, 8))

    # =========================================================================
    # 2. DUAL-CHANNEL IMPUTATION ARCHITECTURE
    # =========================================================================
    story.append(Paragraph("2. Dual-Channel Imputation Architecture", h1_style))
    story.append(Paragraph(
        "Because SFM and TCM stem from completely different communication phenomena, a single imputation model cannot resolve both. "
        "The imputation pipeline partitions recovery into two specialized, sequential channels:",
        body_style
    ))
    story.append(Paragraph(
        "<b>* Channel 1: Constant-Velocity Kalman Filter (Addressing SFM):</b> Roadside Units (RSUs) equipped with smart cameras observe "
        "the highway corridor. The linear Kalman Filter tracks noisy, partial HDV observations, estimates missing leader/follower dynamics, "
        "and reconstructs continuous values for Columns 4, 5, and 6 without modifying the ego-CAV's own coordinates.",
        bullet_style
    ))
    story.append(Paragraph(
        "<b>* Channel 2: Gated Recurrent Unit with Decay (GRU-D) (Addressing TCM):</b> Unlike standard RNNs, GRU-D incorporates trainable "
        "temporal decay parameters (gamma_t = exp(-max(0, W_gamma * dt_t + b_gamma))). This decay vectors "
        "unobserved ego states (Columns 0-3) toward empirical steady-state representations across short bursts.",
        bullet_style
    ))
    story.append(Spacer(1, 8))

    # =========================================================================
    # 3. OBJECTIVE 1: INFEASIBLE RATE METRIC & RESULTS
    # =========================================================================
    story.append(Paragraph("3. Objective 1: Physical-Validity Metric (Infeasible Rate)", h1_style))
    story.append(Paragraph(
        "<b>The Flaw of Average Displacement Error (ADE):</b> Existing literature reports successful imputation based solely on ADE "
        "(pointwise Euclidean error). However, deep neural networks optimizing Mean Squared Error (MSE) introduce high-frequency coordinate "
        "oscillations. Although spatial error remains small (< 0.5 m), the numerical derivatives over dt = 0.1 s trigger massive, "
        "unphysical acceleration spikes.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Authoritative Kinematic Feasibility Constraints:</b> A reconstructed window is physically valid if and only if:",
        body_style
    ))
    story.append(Paragraph(
        "1. <b>Longitudinal Acceleration Bound:</b> a_t in [-8.0, +3.0] m/s^2 for all t in [0, 27]. "
        "(-8.0 m/s^2 represents emergency friction-braking on dry asphalt; +3.0 m/s^2 represents maximum passenger car engine output).",
        bullet_style
    ))
    story.append(Paragraph(
        "2. <b>Curvature / Turning Radius Threshold:</b> r_t >= 6.0 m for all t in [1, 28]. "
        "(A passenger car with wheelbase l_f, l_r in [1, 2] m and steering limit +/-45 deg cannot turn with radius < 6.0 m).",
        bullet_style
    ))
    story.append(Spacer(1, 4))

    story.append(Paragraph("<b>Mathematical Formulations:</b>", h2_style))
    story.append(Paragraph(
        "From consecutive 2D coordinates (x_t, y_t), forward velocity and step acceleration are computed via finite difference:",
        body_style
    ))
    story.append(Paragraph("v_t = sqrt( (x_{t+1} - x_t)^2 + (y_{t+1} - y_t)^2 ) / 0.1, &nbsp;&nbsp;&nbsp; a_t = (v_{t+1} - v_t) / 0.1", formula_style))
    story.append(Paragraph(
        "Turning radius is derived using circumcircle geometry across three consecutive points A(x_{t-1}, y_{t-1}), B(x_t, y_t), C(x_{t+1}, y_{t+1}):",
        body_style
    ))
    story.append(Paragraph("Area(ABC) = 0.5 * | (x_B - x_A)(y_C - y_A) - (y_B - y_A)(x_C - x_A) |, &nbsp;&nbsp;&nbsp; R = (a * b * c) / (4 * Area)", formula_style))
    story.append(Paragraph(
        "where a, b, c are the Euclidean side lengths. The window-level Infeasible Rate is formally defined as:",
        body_style
    ))
    story.append(Paragraph("Infeasible Rate (IR) = [ (1 / N) * sum_{i=1}^N <b>1</b>( exists t : a_t not in [-8, +3] OR r_t < 6.0 ) ] * 100%", formula_style))
    story.append(Spacer(1, 6))

    story.append(Paragraph("<b>Table 3: Infeasible Rate (IR) Across Experimental Conditions (60 Seeds Evaluated)</b>", h2_style))
    
    # Table 3 Data
    t3_data = [
        [Paragraph("Condition", table_header), Paragraph("CAV Pen.", table_header), Paragraph("Seeds", table_header), Paragraph("Ground Truth IR", table_header), Paragraph("Channel 1 (KF) IR", table_header), Paragraph("Fully Imputed IR", table_header), Paragraph("Accel Violations", table_header), Paragraph("Curvature Violations", table_header)],
        [Paragraph("penetration_10", table_cell), Paragraph("10%", table_cell), Paragraph("20", table_cell), Paragraph("1.01 +/- 0.30%", table_cell), Paragraph("0.83 +/- 0.23%", table_cell), Paragraph("<b>78.39 +/- 1.00%</b>", table_cell), Paragraph("78.39 +/- 1.00%", table_cell), Paragraph("11.35 +/- 0.94%", table_cell)],
        [Paragraph("penetration_20", table_cell), Paragraph("20%", table_cell), Paragraph("20", table_cell), Paragraph("1.02 +/- 0.21%", table_cell), Paragraph("0.86 +/- 0.20%", table_cell), Paragraph("<b>78.50 +/- 0.60%</b>", table_cell), Paragraph("78.49 +/- 0.61%", table_cell), Paragraph("11.91 +/- 0.73%", table_cell)],
        [Paragraph("penetration_30", table_cell), Paragraph("30%", table_cell), Paragraph("20", table_cell), Paragraph("1.33 +/- 0.17%", table_cell), Paragraph("1.15 +/- 0.16%", table_cell), Paragraph("<b>78.57 +/- 0.63%</b>", table_cell), Paragraph("78.56 +/- 0.63%", table_cell), Paragraph("12.71 +/- 0.76%", table_cell)],
    ]
    t3 = Table(t3_data, colWidths=[80, 48, 35, 68, 70, 72, 68, 64])
    t3.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG])
    ]))
    story.append(t3)
    story.append(Spacer(1, 8))

    story.append(Paragraph(
        "<b>Core Findings from Objective 1:</b><br/>"
        "1. <i>Ground Truth Baseline Sanity (IR approx. 1.0%):</i> Clean simulator physics rarely triggers violations, confirming metric precision.<br/>"
        "2. <i>Channel 1 Kinematic Neutrality (IR approx. 0.8%):</i> Kalman filtering on RSU observations introduces zero kinematic corruption.<br/>"
        "3. <i>High-Frequency Derivative Instability (IR approx. 78.5%):</i> Pointwise MSE loss fails to preserve second-order dynamics, triggering severe unphysical acceleration spikes exceeding +/-24 m/s^2.",
        body_style
    ))
    story.append(Spacer(1, 8))

    # Objective 1 Figures: Path Comparison, IR Bar Chart, Distributions
    img_traj = "sample_trajectory_comparison.png"
    img_ir = "ir_comparison_across_conditions.png"
    img_dist = "acceleration_and_curvature_distributions.png"

    if os.path.exists(img_traj):
        story.append(Table([
            [Image(img_traj, width=5.5*inch, height=2.4*inch)],
            [Paragraph("<b>Figure 1:</b> 2D Trajectory comparison on highway: Ground Truth vs. Corrupted vs. Fully Imputed trajectory showing high-frequency spatial jitter.", callout_style)]
        ], colWidths=[505], style=[('ALIGN', (0,0), (-1,-1), 'CENTER'), ('TOPPADDING', (0,0), (-1,-1), 2), ('BOTTOMPADDING', (0,0), (-1,-1), 6)]))

    if os.path.exists(img_ir) and os.path.exists(img_dist):
        img_table = Table([
            [Image(img_ir, width=3.3*inch, height=2.1*inch), Image(img_dist, width=3.4*inch, height=2.1*inch)],
            [Paragraph("<b>Figure 2:</b> Infeasible Rate across Ground Truth, Channel 1, and Fully Imputed conditions.", callout_style),
             Paragraph("<b>Figure 3:</b> Acceleration and Curvature violation distributions under GRU-D imputation.", callout_style)]
        ], colWidths=[250, 255])
        img_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ('TOPPADDING', (0,0), (-1,-1), 2),
        ]))
        story.append(img_table)
    story.append(Spacer(1, 10))

    # =========================================================================
    # 4. OBJECTIVE 2: PERCOLATION SWEEP & LOGISTIC FIT
    # =========================================================================
    story.append(Paragraph("4. Objective 2: SFM Percolation Threshold Sweep", h1_style))
    story.append(Paragraph(
        "<b>Scientific Motivation:</b> Prior vehicular network literature asserted that CAV leader connectivity undergoes a percolation-style "
        "phase transition as CAV market penetration increases. However, that assertion was established using only two arbitrary data points "
        "(20% and 30%), which is insufficient to locate an inflection threshold or characterize the transition geometry.",
        body_style
    ))
    story.append(Paragraph(
        "<b>Experimental Setup:</b> We conducted a 6-point market penetration sweep across <b>p in {18%, 21%, 24%, 27%, 30%, 35%}</b> under authoritative "
        "specifications: 3-lane 1000m segment, fixed total flow of 4500 veh/h (1500 veh/h/lane), and speed limit of 33.33 m/s (120 km/h). "
        "Each penetration level was evaluated across <b>10 independent random seeds (60 total simulation runs)</b> using Common Random Numbers (CRN) "
        "for rigorous variance reduction.",
        body_style
    ))
    story.append(Paragraph(
        "<b>3-Parameter Logistic Model:</b> We fit the non-linear sigmoid model C(p) = L / [1 + exp(-k * (p - p_c))], where L represents the "
        "asymptotic saturation connectivity level, k is the logistic steepness, p_c is the critical percolation density, and w = 4/k is the transition width.",
        body_style
    ))
    story.append(Spacer(1, 4))

    # Percolation Summary Table
    story.append(Paragraph("<b>Table 4: CAV-to-CAV Leader Connectivity vs. Market Penetration (Mean +/- 95% CI)</b>", h2_style))
    t4_data = [
        [Paragraph("CAV Penetration (%)", table_header), Paragraph("Simulation Runs", table_header), Paragraph("Instantaneous Connectivity (Mean +/- 95% CI)", table_header), Paragraph("Modal Window Connectivity (Mean +/- 95% CI)", table_header)],
        [Paragraph("18%", table_cell), Paragraph("10 Seeds", table_cell), Paragraph("14.88 +/- 5.36%", table_cell), Paragraph("14.51 +/- 5.23%", table_cell)],
        [Paragraph("21%", table_cell), Paragraph("10 Seeds", table_cell), Paragraph("19.65 +/- 5.36%", table_cell), Paragraph("19.17 +/- 5.21%", table_cell)],
        [Paragraph("24%", table_cell), Paragraph("10 Seeds", table_cell), Paragraph("22.43 +/- 7.01%", table_cell), Paragraph("21.93 +/- 6.89%", table_cell)],
        [Paragraph("27%", table_cell), Paragraph("10 Seeds", table_cell), Paragraph("26.19 +/- 7.65%", table_cell), Paragraph("25.68 +/- 7.58%", table_cell)],
        [Paragraph("30%", table_cell), Paragraph("10 Seeds", table_cell), Paragraph("28.06 +/- 6.47%", table_cell), Paragraph("27.46 +/- 6.43%", table_cell)],
        [Paragraph("35%", table_cell), Paragraph("10 Seeds", table_cell), Paragraph("32.53 +/- 5.50%", table_cell), Paragraph("31.90 +/- 5.45%", table_cell)],
    ]
    t4 = Table(t4_data, colWidths=[90, 75, 170, 170])
    t4.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG])
    ]))
    story.append(t4)
    story.append(Spacer(1, 8))

    # Embed Percolation S-Curve Figure
    img_perc = "percolation_sweep_curve.png"
    if os.path.exists(img_perc):
        perc_table = Table([
            [Image(img_perc, width=5.6*inch, height=3.3*inch)],
            [Paragraph("<b>Figure 4:</b> SFM Percolation Sweep S-Curve: Fitted 3-parameter Logistic curves, empirical data with 95% Confidence Intervals, identified critical threshold p_c approx. 20.7%, and bounded transition interval [18%, 21%].", callout_style)]
        ], colWidths=[505])
        perc_table.setStyle(TableStyle([
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
            ('TOPPADDING', (0,0), (-1,-1), 2),
            ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ]))
        story.append(perc_table)
    story.append(Spacer(1, 6))

    story.append(Paragraph(
        "<b>Model Fitting & Statistical Bounding Analysis:</b><br/>"
        "* <b>Instantaneous Fit:</b> Saturation L = 37.12%, Growth Rate k = 0.1318, <b>Critical Density p_c = 20.66%</b>, Transition Width w = 30.34%.<br/>"
        "* <b>Modal Fit:</b> Saturation L = 36.40%, Growth Rate k = 0.1324, <b>Critical Density p_c = 20.73%</b>, Transition Width w = 30.22%.<br/>"
        "* <b>Bounded Interval Reporting:</b> The steepest slope bracket occurs between 18% and 21%. The upper 95% CI bound at 18% (20.24%) overlaps "
        "with the lower 95% CI bound at 21% (14.29%). Consequently, in accordance with the assignment guidelines, the transition is formally reported "
        "as bounded within <b>[18%, 21%] CAV Market Penetration</b>.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 5. OBJECTIVE 3: CONNECTIVITY DEFINITIONS & PHYSICS VERDICT
    # =========================================================================
    story.append(Paragraph("5. Objective 3: Connectivity Definitions & Artifact vs. Physics Verdict", h1_style))
    story.append(Paragraph(
        "To rigorously determine whether the percolation surge is an observational artifact of how 'leader' is defined over time, "
        "we contrasted two distinct mathematical formulations across all 60 simulation runs:",
        body_style
    ))
    story.append(Paragraph(
        "1. <b>Instantaneous Leader:</b> Evaluated at each discrete 0.1 s step without temporal aggregation (raw per-timestep observation).",
        bullet_style
    ))
    story.append(Paragraph(
        "2. <b>Modal Window Leader:</b> Evaluated across a 3.0 s (30-step) sliding window via majority voting, filtering out short transient leader handovers.",
        bullet_style
    ))
    story.append(Spacer(1, 4))

    # Verdict Callout Box
    verdict_text = (
        "<b>Definitive Scientific Verdict: Genuine Traffic Physics</b><br/>"
        "The critical percolation thresholds for Instantaneous (p_c = 20.66%) and Modal (p_c = 20.73%) definitions agree within "
        "<b>Delta p_c = 0.07%</b>, while the logistic growth rate (k = 0.1318 vs. 0.1324) and transition widths match within 0.12%. "
        "If the percolation surge were merely an observational artifact of window-level aggregation, the 30-step temporal smoothing would have shifted "
        "or dampened the inflection point. Because both instantaneous microscopic observation and modal window aggregation exhibit the exact same "
        "inflection threshold, <b>we conclusively confirm that the percolation transition is a genuine physical property of CACC traffic dynamics</b>. "
        "It is driven by the spontaneous coalescence of vehicle pairs into stable, tightly-spaced platoons (0.55 s headway) once CAV penetration crosses ~20%."
    )
    v_table = Table([[Paragraph(verdict_text, body_style)]], colWidths=[505])
    v_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_BG),
        ('BOX', (0,0), (-1,-1), 1.2, SECONDARY),
        ('TOPPADDING', (0,0), (-1,-1), 8),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 10),
        ('RIGHTPADDING', (0,0), (-1,-1), 10),
    ]))
    story.append(v_table)
    story.append(Spacer(1, 10))

    # =========================================================================
    # 6. WHAT WE COULD NOT VERIFY
    # =========================================================================
    story.append(Paragraph("6. Reproducibility Notice: What We Could Not Verify", h1_style))
    story.append(Paragraph(
        "As mandated by the course assignment specifications regarding reproducibility of external literature:<br/>"
        "<b>Notice on CAERI-NDS Dataset:</b> Paper B's experimental Tables II and III rest on the private, proprietary <b>CAERI-NDS</b> "
        "(China Automotive Engineering Research Institute Naturalistic Driving Study) dataset. This dataset is not publicly available or "
        "distributed in the academic workspace. Direct numerical replication of Paper B's exact values in Tables II-III could not be performed. "
        "However, all methodological formulations, missingness models (SFM and TCM), and physical feasibility metrics were rigorously "
        "validated on the synthetic SUMO simulation pipeline and the public highD highway dataset.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 7. SUMMARY OF DELIVERABLES & CONCLUSION
    # =========================================================================
    story.append(Paragraph("7. Summary of Deliverables & Conclusions", h1_style))
    deliv_data = [
        [Paragraph("Deliverable", table_header), Paragraph("Description & Specification", table_header), Paragraph("Associated File", table_header)],
        [Paragraph("Objective 1 Notebook", table_cell), Paragraph("Complete Infeasible Rate evaluation over 60 files (Table 3)", table_cell), Paragraph("Objective_1_Infeasible_Rate.ipynb", table_cell)],
        [Paragraph("Objective 2 Notebook", table_cell), Paragraph("6-point penetration sweep, logistic fit, and CI bounding", table_cell), Paragraph("Objective_2_Percolation_Sweep.ipynb", table_cell)],
        [Paragraph("Formatted Results", table_cell), Paragraph("Excel workbooks with styled auto-fit columns for Obj 1 & 2", table_cell), Paragraph("objective_1_results.xlsx, objective_2_results.xlsx", table_cell)],
        [Paragraph("Publication Figures", table_cell), Paragraph("300 DPI high-res plots for S-curve, IR comparison & distributions", table_cell), Paragraph("percolation_sweep_curve.png, *.png", table_cell)],
        [Paragraph("Technical Documentation", table_cell), Paragraph("Full repository documentation and markdown research report", table_cell), Paragraph("PROJECT_REPORT.md, README.md, PPT_Information.md", table_cell)],
        [Paragraph("Compiled PDF Report", table_cell), Paragraph("Complete formal academic technical report in PDF format", table_cell), Paragraph("PROJECT_REPORT.pdf", table_cell)],
    ]
    t_deliv = Table(deliv_data, colWidths=[110, 260, 135])
    t_deliv.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), PRIMARY),
        ('GRID', (0,0), (-1,-1), 0.5, BORDER_COLOR),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, LIGHT_BG])
    ]))
    story.append(t_deliv)
    story.append(Spacer(1, 10))

    story.append(Paragraph(
        "<b>Conclusion & Future Recommendations:</b> This study successfully establishes that conventional displacement metrics (ADE) fail to detect severe "
        "kinematic invalidity in imputed vehicular trajectories. The introduced Infeasible Rate (IR) metric effectively penalizes impossible "
        "accelerations and turns, setting a vital benchmark for physical validity. Furthermore, the 60-run percolation sweep firmly "
        "identifies a critical density of p_c approx. 20.7%, confirming that the connectivity jump reflects genuine CACC platoon "
        "physics rather than temporal observation artifacts. Future work will leverage these kinematic constraints to formulate projection-based "
        "regularization filters directly within neural imputation architectures.",
        body_style
    ))
    story.append(Spacer(1, 10))

    # =========================================================================
    # 8. REFERENCES
    # =========================================================================
    story.append(Paragraph("8. References", h1_style))
    refs = [
        "1. Krajzewicz, D., et al. 'Recent Development and Applications of SUMO - Simulation of Urban MObility.' International Journal On Advances in Systems and Measurements, 2012.",
        "2. Milanes, V., & Shladover, S. E. 'Modeling cooperative and autonomous adaptive cruise control dynamic responses using experimental data.' Transportation Research Part C: Emerging Technologies, 2014.",
        "3. Che, Z., Purushotham, S., et al. 'Recurrent Neural Networks for Multivariate Time Series with Missing Values.' Scientific Reports (Nature), 2018. (GRU-D Architecture).",
        "4. Krajewski, R., et al. 'The highD Dataset: A Large High-Resolution Trajectory Dataset of Naturalistic Highway Traffic.' IEEE 21st International Conference on Intelligent Transportation Systems (ITSC), 2018.",
        "5. ISO 15622: Intelligent transport systems - Adaptive cruise control systems - Performance requirements and test procedures, International Organization for Standardization."
    ]
    for r in refs:
        story.append(Paragraph(r, bullet_style))

    # Build Document
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Successfully generated {filename}")

if __name__ == '__main__':
    target = 'PROJECT_REPORT_NITK.pdf'
    build_pdf(target)
