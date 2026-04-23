# Physio AI - Frontend Setup Guide

## 📋 Quick Start

### 1. **Access the Frontend**

The pose detector interface is now available at:

```
http://localhost:8000/static/index.html
```

Or if you set up a dedicated URL route (see below):

```
http://localhost:8000/pose-detector/
```

### 2. **Start Using It**

1. Click **"Start Camera"** to activate your webcam
2. Point camera at your body to see pose detection
3. View real-time joint angles on the right panel
4. Click **"Record Session"** to collect data (click again to stop)
5. Data automatically sends to Django API for scoring

---

## 🛠️ Setup Instructions

### Step 1: Update Django URLs

Add the scoring endpoints to your `physio_ai/urls.py`:

```python
from django.urls import path
from api import views_scoring

urlpatterns = [
    # ... existing patterns ...
    
    # Scoring API endpoints
    path('api/score/calculate/', views_scoring.calculate_score, name='calculate_score'),
    path('api/score/landmarks/', views_scoring.score_from_landmarks, name='score_from_landmarks'),
    path('pose-detector/', views_scoring.pose_detector_ui, name='pose_detector'),
]
```

### Step 2: Configure Static Files

Make sure your Django settings (`settings.py`) has static files configured:

```python
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    BASE_DIR / 'static',
]
```

### Step 3: Enable CORS (if needed)

If your frontend and backend are on different domains, add to `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'corsheaders',
    'rest_framework',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    # ...
]

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]
```

Install if needed:
```bash
pip install django-cors-headers
```

### Step 4: Verify Templates

Make sure `templates/` folder exists and is configured in `settings.py`:

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # ...
            ],
        },
    },
]
```

---

## 🎯 How It Works

### Frontend Flow

```
1. User clicks "Start Camera"
   ↓
2. MediaPipe Pose detects body landmarks in real-time
   ↓
3. JavaScript calculates joint angles
   ↓
4. Angles displayed in real-time on the page
   ↓
5. User clicks "Record Session"
   ↓
6. Frontend collects pose data for N frames
   ↓
7. User clicks "Record Session" again to stop
   ↓
8. Data sent via POST to Django API
   ↓
9. AI engine scores the exercise
   ↓
10. Results displayed to user
```

### API Request Format

```json
{
    "exercise_id": 1,
    "frames": [
        {
            "frame_number": 0,
            "timestamp": 1234567890000,
            "angles": {
                "right_shoulder": 45.2,
                "left_shoulder": 44.8,
                "right_elbow": 90.0,
                "left_elbow": 89.5,
                "right_hip": 85.0,
                "left_hip": 85.5,
                "right_knee": 170.0,
                "left_knee": 170.0,
                "right_wrist": 0.0,
                "left_wrist": 0.0,
                "right_ankle": 90.0,
                "left_ankle": 90.0,
                "spine": 170.0,
                "torso_lean": 0.0
            },
            "confidence": 0.95
        },
        ...
    ]
}
```

### API Response Format

```json
{
    "success": true,
    "overall_score": 85.3,
    "form_score": 85.5,
    "consistency_score": 82.0,
    "range_of_motion_score": 92.0,
    "safety_score": 95.0,
    "summary": "Excellent execution! Score: 85.3/100 ⭐⭐⭐",
    "feedback": [
        "Great form!",
        "Stable movements",
        "Perfect range achieved"
    ],
    "recommendations": [
        "Maintain consistency",
        "Keep practicing!"
    ],
    "mistakes": [],
    "metrics": {
        "total_frames": 150,
        "average_confidence": 0.92,
        "rom_achieved": 92.0
    }
}
```

---

## 🎮 Frontend Features

### Real-Time Display

- **Joint Angles**: All 14 joint angles updated per frame
- **Confidence Score**: Overall pose detection confidence (0-100%)
- **FPS**: Frames per second performance metric
- **Landmarks**: Key body points with coordinates
- **Process Time**: How long each frame takes to process

### Visualization

- **Live Pose Skeleton**: Green lines connecting joints
- **Landmarks**: Red dots at joint positions
- **Mirrored View**: Left-right flipped for intuitive mirror effect

### Recording & Scoring

- **Record Button**: Start/stop data collection
- **Auto-Submit**: Data automatically sent to API when recording stops
- **Configurable API**: Change endpoint URL without code changes
- **Results Display**: Scores and feedback shown in alert

---

## 🔧 Customization

### Change Exercise ID

In the frontend, modify the `recordSession()` function:

```javascript
const payload = {
    exercise_id: 5,  // Change this to 1-10
    frames: CONFIG.recordingSession,
    timestamp: new Date().toISOString()
};
```

### Add More Joint Angles

Edit the `joints` object in `extractJointAngles()`:

```javascript
const joints = {
    'neck': { p1: 11, vertex: 0, p3: 12 },  // New joint
    'your_joint': { p1: idx1, vertex: idx2, p3: idx3 },
    // ...
};
```

### Adjust Pose Detection Confidence

Change in the `pose.setOptions()`:

```javascript
pose.setOptions({
    minDetectionConfidence: 0.5,  // 0-1 (higher = stricter)
    minTrackingConfidence: 0.5,   // 0-1 (higher = stricter)
});
```

### Styling

All CSS is in the `<style>` tag. Key variables:

```css
/* Color scheme */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Layout */
grid-template-columns: 1fr 1fr;  /* 2-column on desktop */

/* Responsive */
@media (max-width: 768px) {
    grid-template-columns: 1fr;  /* 1-column on mobile */
}
```

---

## 🐛 Troubleshooting

### Camera Not Starting

**Problem**: "Camera error" message  
**Solution**: 
- Check webcam permissions in browser
- Try refreshing the page
- Make sure HTTPS or localhost
- Try a different browser

### No Pose Detected

**Problem**: "No pose detected" message  
**Solution**:
- Make sure full body is visible
- Improve lighting
- Move closer to camera
- Wear fitted clothing (loose clothes confuse detection)

### API Error

**Problem**: "API error" message  
**Solution**:
- Check API URL is correct
- Make sure Django server is running
- Check browser console for details (F12)
- Verify CORS is configured if on different domain

### Angles Not Updating

**Problem**: Angles display static  
**Solution**:
- Check browser console (F12) for JavaScript errors
- Verify MediaPipe library loaded
- Try refreshing page
- Check if camera stream is active

### Low FPS

**Problem**: FPS shows <15  
**Solution**:
- Close other browser tabs
- Improve laptop performance
- Lower video resolution in code
- Check Internet connection

---

## 📊 Joint Index Reference

MediaPipe Pose uses 33 landmarks. Key indices:

```
0   = Nose
11  = Left Shoulder
12  = Right Shoulder
13  = Left Elbow
14  = Right Elbow
15  = Left Wrist
16  = Right Wrist
23  = Left Hip
24  = Right Hip
25  = Left Knee
26  = Right Knee
27  = Left Ankle
28  = Right Ankle
```

---

## 🚀 Advanced Usage

### Save Recording Locally

```javascript
// Add to recordSession() function
const data = JSON.stringify(CONFIG.recordingSession);
const blob = new Blob([data], { type: 'application/json' });
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = `pose_${Date.now()}.json`;
a.click();
```

### Send to Custom Endpoint

```javascript
const apiUrl = 'https://your-server.com/api/pose/';
```

### Add Real-Time Scoring

```javascript
if (results.poseLandmarks && results.poseLandmarks.length > 0) {
    const angles = extractJointAngles(results.poseLandmarks);
    
    // Add feedback every N frames
    if (CONFIG.frameCount % 30 === 0) {
        checkFormQuality(angles);
    }
}
```

---

## 📱 Browser Compatibility

| Browser | Desktop | Mobile |
|---------|---------|--------|
| Chrome | ✅ | ✅ |
| Firefox | ✅ | ✅ |
| Safari | ✅ | ✅ |
| Edge | ✅ | ✅ |

**Note**: Requires HTTPS or localhost for camera access

---

## 🔐 Privacy

- **No data saved**: Pose data only collected during recording
- **No external calls**: Only sends to your Django server
- **Local processing**: MediaPipe runs locally, not on cloud
- **User control**: Only records when user clicks "Record"

---

## 📚 File Structure

```
physio_ai/
├── static/
│   └── index.html              ← Main UI (this file)
├── api/
│   ├── views_scoring.py        ← API endpoints
│   └── urls.py
├── ai_engine/
│   ├── score_generator.py      ← Scoring engine
│   └── ...
└── settings.py                 ← Django config
```

---

## ✅ Testing Checklist

- [ ] Camera starts and shows video
- [ ] Green skeleton overlays on body
- [ ] Red dots appear at joints
- [ ] FPS shows >15
- [ ] Angles update in real-time
- [ ] Recording button works
- [ ] Data sends to API
- [ ] Score received back
- [ ] Feedback displays

---

## 🆘 Support

**Check these first:**
1. Browser console (F12) - Look for JavaScript errors
2. Django logs - Check for backend errors
3. Network tab (F12) - See API requests/responses
4. This guide - Most issues covered above

**Still stuck?**
- Check firewall settings
- Try different network
- Test on different browser
- Review Django configuration

---

## 🎓 Learning Resources

- [MediaPipe Pose Docs](https://google.github.io/mediapipe/solutions/pose.html)
- [Pose Landmarks](https://google.github.io/mediapipe/solutions/pose#pose-landmark-model-bundle)
- [Web Camera API](https://developer.mozilla.org/en-US/docs/Web/API/WebRTC_API)
- [Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)

---

## 📝 Next Steps

1. ✅ Start the frontend
2. ✅ Test pose detection
3. ✅ Record a session
4. ✅ View results
5. 🎯 Customize exercises
6. 🎯 Integrate with your app
7. 🎯 Deploy to production

---

**Status**: ✅ Ready to Use  
**Last Updated**: April 20, 2026  
**Version**: 1.0.0
