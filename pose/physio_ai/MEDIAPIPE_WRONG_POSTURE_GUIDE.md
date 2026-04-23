# MediaPipe & Wrong Posture Detection - Visual Guide

## 📊 COMPLETE DATA FLOW: From Pose Capture to Wrong Posture Alerts

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          LIVE EXERCISE SESSION                              │
└─────────────────────────────────────────────────────────────────────────────┘

1️⃣  USER STARTS EXERCISE
    └─ URL: /sessions/<id>/start/
    └─ Opens: templates/sessions/pose_capture.html
    └─ Initializes: MediaPipe + Webcam

2️⃣  REAL-TIME POSE CAPTURE
    
    ┌─────────────────────────────────────────────────────┐
    │  BROWSER (Client-Side)                              │
    │                                                     │
    │  📹 HTML5 Canvas                                    │
    │  ├─ getUserMedia() → Webcam stream                  │
    │  ├─ Canvas rendering                                │
    │  └─ 30 FPS continuous                               │
    │                                                     │
    │  🤖 MediaPipe Pose (JavaScript)                     │
    │  ├─ Load model weights                              │
    │  ├─ Input: Video frame (30 FPS)                     │
    │  ├─ Output: 33 body landmarks                       │
    │  └─ Latency: ~100ms per frame                       │
    │                                                     │
    │  🎨 Draw Skeleton                                   │
    │  ├─ Draw 33 joints                                  │
    │  ├─ Draw connections (limbs)                        │
    │  ├─ Color: Green (safe) / Red (danger)              │
    │  └─ Display on canvas overlay                       │
    │                                                     │
    │  📤 Send to Server (Every 30 frames ~1 sec)         │
    │  └─ JSON: {detected_joints, timestamp, frame_num}   │
    └─────────────────────────────────────────────────────┘
                            │
                            ↓ (HTTP POST)
    
3️⃣  SERVER-SIDE PROCESSING
    
    ┌─────────────────────────────────────────────────────┐
    │  DJANGO BACKEND                                     │
    │                                                     │
    │  📨 Receive pose data at:                           │
    │  POST /api/sessions/upload_pose_frame/              │
    │                                                     │
    │  📊 Process in: sessions/pose_processor.py          │
    │  ├─ Extract landmarks (33 points)                   │
    │  ├─ Calculate joint angles:                         │
    │  │  • Knee angle (hip-knee-ankle)                   │
    │  │  • Shoulder angle (elbow-shoulder-hip)           │
    │  │  • Hip angle, Ankle, Elbow, etc.                 │
    │  │                                                  │
    │  ├─ Check against safety profiles:                  │
    │  │  └─ JointSafetyProfile table                     │
    │  │     └─ Lookup: exercise_type + joint_name        │
    │  │     └─ Compare: current_angle vs safe_range      │
    │  │                                                  │
    │  └─ Calculate form score (0-100):                   │
    │     └─ Based on how close to ideal form             │
    │                                                     │
    │  ⚠️ Generate alerts if issues:                      │
    │  advanced_features/posture_analyzer.py              │
    │  ├─ CRITICAL (15°+ over): risk_level='critical'     │
    │  ├─ HIGH (5-15° over): risk_level='high'            │
    │  ├─ MEDIUM (<5° over): risk_level='medium'          │
    │  ├─ LOW (normal): risk_level='low'                  │
    │  └─ Create InjuryRiskAlert record in DB             │
    │                                                     │
    │  💾 Store in database:                              │
    │  ├─ PoseAnalysis (ai_engine_poseanalysis table)     │
    │  │  ├─ frame_number                                 │
    │  │  ├─ detected_joints (JSON)                       │
    │  │  ├─ form_score                                   │
    │  │  ├─ issues_detected                              │
    │  │  └─ recommendations                              │
    │  │                                                  │
    │  └─ InjuryRiskAlert (advanced_features table)       │
    │     ├─ alert_type                                   │
    │     ├─ risk_level                                   │
    │     ├─ joint_name                                   │
    │     ├─ current_angle                                │
    │     ├─ safe_range_min/max                           │
    │     ├─ severity_score                               │
    │     └─ recommendation                               │
    │                                                     │
    │  📲 Return response:                                │
    │  {                                                  │
    │    "form_score": 78,                                │
    │    "alerts": [{                                     │
    │      "alert_type": "joint_angle",                   │
    │      "risk_level": "critical",                      │
    │      "joint": "left_knee",                          │
    │      "current_angle": 135,                          │
    │      "safe_range": [0, 120],                        │
    │      "exceeded_by": 15,                             │
    │      "recommendation": "Reduce knee bend..."        │
    │    }]                                               │
    │  }                                                  │
    └─────────────────────────────────────────────────────┘
                            │
                            ↓ (HTTP Response)

4️⃣  REAL-TIME ALERT DISPLAY (Browser)
    
    ┌─────────────────────────────────────────────────────┐
    │  LIVE ALERT ON SCREEN                               │
    │                                                     │
    │  If alert received:                                 │
    │  ┌─────────────────────────────────────────────┐    │
    │  │ 🔴 CRITICAL ALERT!                          │    │
    │  │ Left Knee: 135° (Safe: 0-120°)              │    │
    │  │ ⚠️  REDUCE YOUR KNEE BEND IMMEDIATELY!      │    │
    │  │                                             │    │
    │  │ [Acknowledge] [Stop Exercise] [Details]     │    │
    │  └─────────────────────────────────────────────┘    │
    │                                                     │
    │  Also updates skeleton:                             │
    │  ├─ Color affected joint RED                        │
    │  ├─ Draw warning circle around joint                │
    │  └─ Add text annotation                             │
    │                                                     │
    │  Continue: If user ignores, keep monitoring        │
    └─────────────────────────────────────────────────────┘

5️⃣  AFTER EXERCISE COMPLETES
    
    ┌─────────────────────────────────────────────────────┐
    │  SESSION ANALYSIS & REPORT                          │
    │                                                     │
    │  1. Aggregate all PoseAnalysis frames:              │
    │     ├─ Calculate average form score                 │
    │     ├─ Count frame-by-frame scores                  │
    │     ├─ Identify worst frames                        │
    │     └─ Track improvement/decline                    │
    │                                                     │
    │  2. Aggregate all InjuryRiskAlerts:                 │
    │     ├─ Group by alert type                          │
    │     ├─ Calculate total severity                     │
    │     ├─ Count frames with issues                     │
    │     └─ Identify patterns (e.g., knees always bad)   │
    │                                                     │
    │  3. Generate AIFeedback:                            │
    │     ├─ What went well (positive areas)              │
    │     ├─ What to improve (problem areas)              │
    │     ├─ Priority recommendations                     │
    │     └─ Next session suggestions                     │
    │                                                     │
    │  4. Create Session Report:                          │
    │     url: /sessions/<id>/report/                     │
    │     template: templates/sessions/session_report.html│
    └─────────────────────────────────────────────────────┘

6️⃣  REPORT PAGE DISPLAYS WRONG POSTURES
    
    ┌─────────────────────────────────────────────────────┐
    │  SESSION REPORT                                     │
    │  (After completing exercise)                        │
    │                                                     │
    │  ✅ Form Score: 78/100                              │
    │  ⏱️ Duration: 2:45                                   │
    │  📊 Reps: 12                                        │
    │                                                     │
    │  ⚠️  WRONG POSTURES DETECTED (4):                   │
    │                                                     │
    │  🔴 CRITICAL - Left Knee Hyperextension            │
    │  ├─ Frames: 12, 45, 89                              │
    │  ├─ Angle: 135° (Safe: 0-120°)                     │
    │  ├─ Exceeded by: 15°                                │
    │  ├─ Severity: 80/100                                │
    │  ├─ Occurred: 3 times                               │
    │  ├─ 📈 Trend: Getting better (was 142°, now 135°)  │
    │  └─ 💡 How to fix:                                  │
    │     "Keep knees slightly bent, don't lock them      │
    │      at the top of the movement"                    │
    │                                                     │
    │  🟠 HIGH - Forward Torso Lean                       │
    │  ├─ Frames: 34                                      │
    │  ├─ Angle: 25° (Safe: 0-15°)                       │
    │  ├─ Severity: 65/100                                │
    │  └─ 💡 How to fix:                                  │
    │     "Keep torso upright, shift weight to heels"     │
    │                                                     │
    │  🟡 MEDIUM - Feet Turned Inward                     │
    │  └─ 💡 How to fix:                                  │
    │     "Point feet slightly outward (5-10°)"           │
    │                                                     │
    │  🟢 LOW - Slight Weight Imbalance                   │
    │  └─ 💡 How to fix:                                  │
    │     "Keep weight equal on both sides"               │
    │                                                     │
    │  [View Frame-by-Frame] [Video Replay] [Export PDF]  │
    └─────────────────────────────────────────────────────┘

7️⃣  DASHBOARD SHOWS WRONG POSTURE TRENDS
    
    ┌─────────────────────────────────────────────────────┐
    │  DASHBOARD - Wrong Posture Summary                  │
    │  url: /users/dashboard/                             │
    │                                                     │
    │  🔴 Critical Issues (Need Attention):               │
    │  ├─ Knee Hyperextension (5 sessions)                │
    │  │  └─ Last: 2 hours ago                            │
    │  ├─ Shoulder Elevation (3 sessions)                 │
    │  └─ Spinal Rotation (2 sessions)                    │
    │                                                     │
    │  ⚠️  Recurring Issues:                               │
    │  ├─ Forward Lean (8 sessions, 64% of workouts)      │
    │  └─ Weight Asymmetry (4 sessions)                   │
    │                                                     │
    │  📈 Improving Trends:                               │
    │  ├─ Ankle Position: ✓ Fixed                         │
    │  └─ Hip Stability: ↗ Getting better                 │
    │                                                     │
    │  💪 Ready to Progress:                              │
    │  └─ Squat: Form consistently good (85+%)            │
    │     [Increase Difficulty] [Try Variation]           │
    │                                                     │
    │  [View All Alerts] [Export Report] [Get Coaching]   │
    └─────────────────────────────────────────────────────┘

8️⃣  ADMIN PANEL - THERAPIST VIEW
    
    ┌─────────────────────────────────────────────────────┐
    │  /admin/advanced_features/injuryriskalert/          │
    │                                                     │
    │  List all user alerts:                              │
    │  ┌──────────────────────────────────────────────┐   │
    │  │ User        │ Alert           │ Risk   │ When    │   │
    │  ├──────────────────────────────────────────────┤   │
    │  │ admin       │ Joint Angle     │ 🔴 HI  │ 2h ago  │   │
    │  │ john_doe    │ ROM Excess      │ 🟠 MED │ 1h ago  │   │
    │  │ jane_smith  │ Asym. Weight    │ 🟡 LO  │ 30m ago │   │
    │  │ bob_wilson  │ Compression     │ 🔴 CRIT│ 5m ago! │   │
    │  └──────────────────────────────────────────────┘   │
    │                                                     │
    │  Click alert to see:                                │
    │  ├─ Detailed joint angles                           │
    │  ├─ Video frame capture                             │
    │  ├─ Recommended correction                          │
    │  ├─ Patient's response                              │
    │  └─ Historical trend for this alert type            │
    │                                                     │
    │  Therapist can:                                     │
    │  ├─ Add notes/coaching                              │
    │  ├─ Request re-training video                       │
    │  ├─ Modify exercise program                         │
    │  └─ Export data for telehealth session              │
    └─────────────────────────────────────────────────────┘
```

---

## 🗂️ DATABASE TABLES FOR WRONG POSTURE TRACKING

```
┌──────────────────────────────────────────────────────────────┐
│  ai_engine_poseanalysis (ONE FRAME = ONE ROW)                │
├──────────────────────────────────────────────────────────────┤
│ id │ session_ex_id │ frame │ form_score │ detected_joints    │
├────┼───────────────┼───────┼────────────┼──────────────────┤
│ 1  │ 5             │ 1     │ 85.2       │ {landmarks JSON} │
│ 2  │ 5             │ 2     │ 82.1       │ {landmarks JSON} │
│ 3  │ 5             │ 3     │ 78.5       │ {landmarks JSON} │
│ 4  │ 5             │ 4     │ 76.8       │ {landmarks JSON} │
│ 5  │ 5             │ 5     │ 72.3       │ {landmarks JSON} │ ← Wrong knee!
│ 6  │ 5             │ 6     │ 80.1       │ {landmarks JSON} │
└────┴───────────────┴───────┴────────────┴──────────────────┘

┌────────────────────────────────────────────────────────────────────┐
│  advanced_features_injuryriskalert (ONE ALERT = ONE ROW)            │
├────────────────────────────────────────────────────────────────────┤
│ id │ user_id │ session_ex │ joint_name  │ current_angle │ severity │
├────┼─────────┼────────────┼─────────────┼───────────────┼──────────┤
│ 1  │ 1       │ 5          │ left_knee   │ 135.0         │ 65       │
│ 2  │ 1       │ 5          │ right_hip   │ 92.0          │ 40       │
│ 3  │ 2       │ 8          │ left_shoulder│ 105.0        │ 50       │
│ 4  │ 3       │ 12         │ spine_flex  │ 65.0          │ 75       │
└────┴─────────┴────────────┴─────────────┴───────────────┴──────────┘

┌──────────────────────────────────────────────────────────────┐
│  advanced_features_jointsafetyprofile (DEFINES SAFE RANGES)  │
├──────────────────────────────────────────────────────────────┤
│ exercise │ joint           │ safe_min │ safe_max │ risk_level │
├──────────┼─────────────────┼──────────┼──────────┼────────────┤
│ squat    │ knee_flexion    │ 0°       │ 120°     │ conservative
│ squat    │ spine_flexion   │ 0°       │ 45°      │ conservative
│ press    │ elbow_extension │ 0°       │ 180°     │ standard
│ deadlift │ hip_flexion     │ -30°     │ 90°      │ standard
│ squat    │ ankle_flexion   │ -15°     │ 45°      │ conservative
└──────────┴─────────────────┴──────────┴──────────┴────────────┘
```

---

## 🎯 KEY FILES FOR WRONG POSTURE SYSTEM

```
physio_ai/
├── 📄 MODELS (Database)
│   ├── ai_engine/models.py
│   │   ├── PoseAnalysis ← Each frame analysis
│   │   └── AIFeedback ← Session feedback
│   │
│   └── advanced_features/models.py
│       ├── InjuryRiskAlert ← WRONG POSTURE ALERTS!
│       ├── JointSafetyProfile ← Safe angle ranges
│       └── DifficultyAdaptation ← Auto progression

├── 📡 API ENDPOINTS (To Create)
│   └── sessions/
│       ├── api_views.py
│       │   └── POST /api/sessions/upload_pose_frame/ ← Receives pose data
│       │
│       └── pose_processor.py
│           ├── process_video_frame() ← MediaPipe processing
│           ├── calculate_joint_angle()
│           └── check_safety_ranges()

├── 🎨 TEMPLATES (User Interface)
│   ├── sessions/
│   │   ├── pose_capture.html ← Live webcam (TO CREATE)
│   │   └── session_report.html ← Results with wrong postures (TO CREATE)
│   │
│   └── alerts/
│       └── alert_display.html ← Alert widget (TO CREATE)

├── 📱 FRONTEND JS
│   └── static/js/
│       └── pose_capture.js ← MediaPipe client (TO CREATE)

└── 📊 ANALYTICS (Reports)
    └── templates/
        ├── analytics/posture_trends.html
        └── dashboard/alerts_widget.html
```

---

## 📋 SUMMARY: Where Wrong Posture Appears

| Location | What's Shown | When |
|----------|-------------|------|
| **Live Capture** | 🔴 Red skeleton joints + Alert popup | During exercise |
| **Session Report** | Detailed list of wrong postures with angles & fixes | After exercise completes |
| **Dashboard** | Summary of recurring issues & trends | Always visible |
| **Admin Panel** | All user alerts, therapist notes | For therapist/coach |
| **Notifications** | Push alerts on critical issues | Real-time |
| **Mobile App** | Real-time alerts + history | During/after exercise |

