# JavaScript Pose Detection - Quick Reference

## 📚 Files Created

```
static/
├── index.html              ← Full-featured UI
├── example.html            ← Simple example
└── js/
    └── pose_detector.js    ← Reusable module
```

---

## 🚀 Quick Start (3 ways)

### Option 1: Use Full UI (Recommended for beginners)
```
Open: http://localhost:8000/static/index.html
Click: Start Camera → Record Session → View Results
```

### Option 2: Use Simple Example
```
Open: http://localhost:8000/static/example.html
Click: Start Camera → Record (5s) → Export Data
```

### Option 3: Use JavaScript Module (For developers)
```javascript
// Import in your HTML:
<script src="/static/js/pose_detector.js"></script>

// Use in your code:
const detector = new PoseDetector({...});
await detector.startCamera();
```

---

## 🔧 PoseDetector Module API

### Constructor
```javascript
const detector = new PoseDetector({
    canvasId: 'canvas',                    // Required: Canvas element ID
    videoId: 'video',                      // Optional: Video element ID
    modelComplexity: 1,                    // 0=light, 1=full (default)
    minDetectionConfidence: 0.5,           // 0-1
    minTrackingConfidence: 0.5,            // 0-1
    videoWidth: 640,                       // Default video width
    videoHeight: 480,                      // Default video height
    onPose: (landmarks, angles, confidence, procTime) => {},  // Callback
    onError: (error) => { console.error(error); }             // Error handler
});
```

### Methods

**Start/Stop**
```javascript
await detector.startCamera();              // Start webcam
detector.stopCamera();                     // Stop webcam
detector.destroy();                        // Cleanup
```

**Data Collection**
```javascript
detector.clearHistory();                   // Clear recorded frames
detector.poseHistory;                      // Get all recorded frames
detector.getHistory(10);                   // Get last N frames
detector.exportHistory();                  // Get JSON string
```

**Analysis**
```javascript
detector.getFPS();                         // Get current FPS
detector.getStatistics();                  // Get avg/min/max/std for each joint
detector.getLandmark(0);                   // Get specific landmark
```

**API**
```javascript
const result = await detector.sendToAPI(
    'http://localhost:8000/api/score/calculate/',
    exercise_id = 1
);
```

---

## 📐 Angle Calculation

### How It Works
```
For three points (A, B, C):
1. Create vectors: v1 = A-B, v2 = C-B
2. Calculate dot product: dot = v1·v2
3. Get magnitudes: mag1 = |v1|, mag2 = |v2|
4. Get cosine: cos = dot / (mag1 * mag2)
5. Get angle: angle = arccos(cos) * 180/π
```

### Supported Joints (14 total)
```javascript
{
    'right_shoulder': 45.2,    // Right arm angle
    'left_shoulder': 44.8,
    'right_elbow': 90.0,       // Elbow bend
    'left_elbow': 89.5,
    'right_hip': 85.0,         // Hip angle
    'left_hip': 85.5,
    'right_knee': 170.0,       // Knee angle
    'left_knee': 170.0,
    'right_wrist': 0.0,        // Wrist angle
    'left_wrist': 0.0,
    'right_ankle': 90.0,       // Ankle angle
    'left_ankle': 90.0,
    'spine': 170.0,            // Spine angle
    'torso_lean': 0.0          // Torso lean
}
```

### Add Custom Joint
```javascript
// In extractJointAngles() method:
const joints = {
    'custom_joint': { p1: 11, vertex: 23, p3: 25 },  // New joint
    // p1, vertex, p3 are MediaPipe landmark indices
};

// Landmark indices:
0=Nose, 11=L_Shoulder, 12=R_Shoulder, 13=L_Elbow, 14=R_Elbow,
15=L_Wrist, 16=R_Wrist, 23=L_Hip, 24=R_Hip, 25=L_Knee, 26=R_Knee,
27=L_Ankle, 28=R_Ankle, 30=L_FootIndex, 32=R_FootIndex
```

---

## 📤 API Integration

### Send Data to Django
```javascript
const result = await detector.sendToAPI(
    'http://localhost:8000/api/score/calculate/',
    exercise_id = 1
);

console.log(result);
// {
//   overall_score: 85.3,
//   form_score: 85.5,
//   consistency_score: 82.0,
//   range_of_motion_score: 92.0,
//   safety_score: 95.0,
//   summary: "Great job!",
//   feedback: [...],
//   recommendations: [...],
//   metrics: {...}
// }
```

### Expected Request Format
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
                ...
            },
            "confidence": 0.95
        },
        ...
    ]
}
```

---

## 💾 Data Format

### Recorded Frame
```javascript
{
    timestamp: 1234567890,           // Milliseconds
    landmarks: [                     // 33 MediaPipe landmarks
        {
            x: 0.5,                  // 0-1 (normalized)
            y: 0.5,
            z: 0,                    // Depth
            visibility: 0.95         // Confidence 0-1
        },
        ...
    ],
    angles: {                        // Calculated angles
        "right_shoulder": 45.2,
        ...
    },
    confidence: 95                   // 0-100%
}
```

### Statistics Output
```javascript
{
    totalFrames: 150,
    avgConfidence: 92,
    jointStats: {
        right_shoulder: {
            average: 45.2,
            min: 40.5,
            max: 50.3,
            stddev: 3.2,
            samples: 150
        },
        ...
    }
}
```

---

## 🎯 Common Patterns

### Pattern 1: Real-time Display
```javascript
const detector = new PoseDetector({
    canvasId: 'canvas',
    onPose: (landmarks, angles, confidence) => {
        document.getElementById('score').textContent = confidence + '%';
    }
});
await detector.startCamera();
```

### Pattern 2: Data Collection
```javascript
detector.clearHistory();
// Collect for 10 seconds
setTimeout(() => {
    const data = detector.exportHistory();
    console.log(data);
}, 10000);
```

### Pattern 3: Statistics
```javascript
const stats = detector.getStatistics();
for (const [joint, data] of Object.entries(stats.jointStats)) {
    console.log(`${joint}: ${data.average}° (±${data.stddev}°)`);
}
```

### Pattern 4: Condition Detection
```javascript
const angles = detector.poseHistory[detector.poseHistory.length - 1]?.angles;

if (angles && angles.right_knee < 90) {
    console.log('Knee is bent less than 90°');
}
```

### Pattern 5: Trigger Action
```javascript
detector.clearHistory();

// Record when shoulder angle > 90°
let triggered = false;
setTimeout(() => {
    const stats = detector.getStatistics();
    if (stats.jointStats.right_shoulder.average > 90) {
        console.log('Shoulder raised!');
        triggered = true;
    }
}, 2000);
```

---

## 🔍 Debugging

### Check if Working
```javascript
// In browser console:
detector.getFPS()                      // Should be > 15
detector.poseHistory.length            // Should increase
detector.getStatistics()               // Should have data
```

### Enable Logging
```javascript
// Patch onResults to log:
const origOnResults = detector.onPoseResults;
detector.onPoseResults = function(results) {
    console.log('Landmarks:', results.poseLandmarks.length);
    return origOnResults.call(this, results);
};
```

### Check Landmarks
```javascript
const landmark = detector.getLandmark(0);  // Nose
console.log(landmark);
// { x: 0.5, y: 0.5, z: 0, visibility: 0.95 }
```

---

## ⚡ Performance

### FPS by Device
```
Desktop (high-end):    30+ FPS
Laptop (mid-range):    15-25 FPS
Mobile (good phone):   10-20 FPS
```

### Optimization Tips
```javascript
// 1. Reduce model complexity
modelComplexity: 0,              // Instead of 1

// 2. Lower confidence threshold
minDetectionConfidence: 0.3,     // Instead of 0.5

// 3. Reduce video resolution
videoWidth: 480,                 // Instead of 640
videoHeight: 360,

// 4. Disable smoothing for speed
// (Edit pose_detector.js)
```

---

## 🐛 Troubleshooting

| Problem | Solution |
|---------|----------|
| Camera won't start | Check permissions, use HTTPS or localhost |
| No pose detected | Improve lighting, wear fitted clothes, full body visible |
| Low FPS | Lower resolution, reduce model complexity |
| Angles are 0 | Check landmarks are being detected |
| API error 400 | Check exercise_id is valid (1-10) |
| CORS error | Enable CORS in Django settings |

---

## 📱 Browser Compatibility

| Browser | Desktop | Mobile | Notes |
|---------|---------|--------|-------|
| Chrome | ✅ | ✅ | Best support |
| Firefox | ✅ | ✅ | Good support |
| Safari | ✅ | ✅ | iOS 14+ |
| Edge | ✅ | ✅ | Full support |

---

## 🔗 External Resources

**MediaPipe Pose:**
- https://google.github.io/mediapipe/solutions/pose.html
- https://github.com/google/mediapipe

**Landmarks:**
- https://google.github.io/mediapipe/solutions/pose#pose-landmark-model-bundle

**JavaScript APIs:**
- https://developer.mozilla.org/en-US/docs/Web/API/MediaDevices/getUserMedia
- https://developer.mozilla.org/en-US/docs/Web/API/Canvas_API
- https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API

---

## 💡 Tips

1. **Always test with webcam first** - Debug issues before sending to API
2. **Use console.log()** - Check what data you're getting
3. **Test API separately** - Use Postman to verify endpoint
4. **Cache MediaPipe model** - First load is slower (~3-5s)
5. **Handle errors gracefully** - Users may deny camera access
6. **Test on mobile** - Pose detection is slower on phones

---

## 📝 Example: Custom Integration

```javascript
// 1. Create detector
const detector = new PoseDetector({
    canvasId: 'myCanvas',
    onPose: handlePose
});

// 2. Define handler
function handlePose(landmarks, angles, confidence, procTime) {
    console.log(`FPS: ${detector.getFPS()}`);
    console.log(`Confidence: ${confidence}%`);
    
    // Your custom logic here
    if (angles.right_knee > 90) {
        console.log('Knee bent!');
    }
}

// 3. Start
await detector.startCamera();

// 4. Record & analyze
detector.clearHistory();
setTimeout(async () => {
    const stats = detector.getStatistics();
    console.log('Stats:', stats);
    
    // 5. Send to API
    const result = await detector.sendToAPI(apiUrl, 1);
    console.log('Score:', result.overall_score);
}, 5000);
```

---

**Last Updated**: April 20, 2026  
**Version**: 1.0.0  
**Status**: ✅ Production Ready
