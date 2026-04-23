const DEFAULT_CONNECTIONS = [
    [11, 12], [11, 13], [13, 15], [12, 14], [14, 16],
    [11, 23], [12, 24], [23, 24], [23, 25], [25, 27],
    [24, 26], [26, 28], [27, 29], [28, 30], [29, 31], [30, 32],
];

const LANDMARK_LABELS = {
    left_shoulder: 11,
    right_shoulder: 12,
    left_elbow: 13,
    right_elbow: 14,
    left_wrist: 15,
    right_wrist: 16,
    left_hip: 23,
    right_hip: 24,
    left_knee: 25,
    right_knee: 26,
    left_ankle: 27,
    right_ankle: 28,
};

class PoseDetector {
    constructor(config = {}) {
        this.config = {
            canvasId: config.canvasId || "poseCanvas",
            videoId: config.videoId || "poseVideo",
            onPose: config.onPose || (() => {}),
            onStatus: config.onStatus || (() => {}),
            videoWidth: config.videoWidth || 960,
            videoHeight: config.videoHeight || 720,
            minDetectionConfidence: config.minDetectionConfidence || 0.6,
            minTrackingConfidence: config.minTrackingConfidence || 0.6,
            modelComplexity: config.modelComplexity || 1,
            motionTrailLength: config.motionTrailLength || 10,
            mirror: config.mirror !== false,
            targetFps: config.targetFps || 20,
            landmarkSmoothing: config.landmarkSmoothing || 0.42,
        };

        this.videoElement = document.getElementById(this.config.videoId);
        this.canvasElement = document.getElementById(this.config.canvasId);
        this.canvasCtx = this.canvasElement?.getContext("2d");
        this.pose = null;
        this.camera = null;
        this.stream = null;
        this.deviceId = null;
        this.isRunning = false;
        this.lastPoseTime = performance.now();
        this.frameCounter = 0;
        this.currentFps = 0;
        this.skeletonHistory = [];
        this.smoothedLandmarks = null;
        this.lastMetrics = null;
        this.animationFrame = null;
    }

    async initialize() {
        if (!this.videoElement || !this.canvasElement) {
            throw new Error("PoseDetector requires both video and canvas elements.");
        }

        this.pose = new Pose({
            locateFile: (file) => `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`,
        });

        this.pose.setOptions({
            modelComplexity: this.config.modelComplexity,
            smoothLandmarks: true,
            enableSegmentation: false,
            minDetectionConfidence: this.config.minDetectionConfidence,
            minTrackingConfidence: this.config.minTrackingConfidence,
        });

        this.pose.onResults(this.onPoseResults.bind(this));
        await this.syncCanvasSize();
    }

    async listCameras() {
        const devices = await navigator.mediaDevices.enumerateDevices();
        return devices.filter((device) => device.kind === "videoinput");
    }

    async startCamera(deviceId = null) {
        this.deviceId = deviceId || this.deviceId;

        this.stream = await navigator.mediaDevices.getUserMedia({
            video: {
                deviceId: this.deviceId ? { exact: this.deviceId } : undefined,
                width: { ideal: this.config.videoWidth },
                height: { ideal: this.config.videoHeight },
                frameRate: { ideal: 30, min: this.config.targetFps },
            },
            audio: false,
        });

        this.videoElement.srcObject = this.stream;
        await this.videoElement.play();
        await this.syncCanvasSize();

        this.camera = new Camera(this.videoElement, {
            width: this.config.videoWidth,
            height: this.config.videoHeight,
            onFrame: async () => {
                if (!this.isRunning) {
                    return;
                }
                await this.pose.send({ image: this.videoElement });
            },
        });

        this.isRunning = true;
        this.camera.start();
    }

    stopCamera() {
        this.isRunning = false;
        if (this.camera) {
            this.camera.stop();
        }
        if (this.stream) {
            this.stream.getTracks().forEach((track) => track.stop());
        }
        if (this.animationFrame) {
            cancelAnimationFrame(this.animationFrame);
        }
    }

    async syncCanvasSize() {
        const width = this.videoElement.videoWidth || this.config.videoWidth;
        const height = this.videoElement.videoHeight || this.config.videoHeight;
        this.canvasElement.width = width;
        this.canvasElement.height = height;
        this.canvasElement.style.width = "100%";
        this.canvasElement.style.height = "100%";
    }

    updateLiveMetrics(metrics) {
        this.lastMetrics = metrics;
    }

    onPoseResults(results) {
        this.frameCounter += 1;
        const now = performance.now();
        const elapsed = now - this.lastPoseTime;
        if (elapsed >= 1000) {
            this.currentFps = Math.round((this.frameCounter * 1000) / elapsed);
            this.lastPoseTime = now;
            this.frameCounter = 0;
            this.config.onStatus({ fps: this.currentFps });
        }

        if (!results.poseLandmarks?.length) {
            this.renderOverlay(null);
            return;
        }

        const smoothedLandmarks = this.smoothLandmarks(results.poseLandmarks);
        this.skeletonHistory.push(smoothedLandmarks);
        this.skeletonHistory = this.skeletonHistory.slice(-this.config.motionTrailLength);

        const angles = this.extractJointAngles(smoothedLandmarks);
        const confidence = this.getConfidenceScore(smoothedLandmarks);
        const payload = {
            landmarks: smoothedLandmarks,
            rawLandmarks: results.poseLandmarks,
            angles,
            confidence,
            fps: this.currentFps,
            calibration: this.getCalibration(smoothedLandmarks),
        };

        this.renderOverlay(smoothedLandmarks, angles);
        this.config.onPose(payload);
    }

    smoothLandmarks(landmarks) {
        if (!this.smoothedLandmarks) {
            this.smoothedLandmarks = landmarks.map((landmark) => ({ ...landmark }));
            return this.smoothedLandmarks;
        }

        const alpha = this.config.landmarkSmoothing;
        this.smoothedLandmarks = landmarks.map((landmark, index) => {
            const previous = this.smoothedLandmarks[index] || landmark;
            return {
                ...landmark,
                x: (landmark.x * alpha) + (previous.x * (1 - alpha)),
                y: (landmark.y * alpha) + (previous.y * (1 - alpha)),
                z: (landmark.z * alpha) + (previous.z * (1 - alpha)),
            };
        });
        return this.smoothedLandmarks;
    }

    renderOverlay(landmarks, angles = {}) {
        const ctx = this.canvasCtx;
        if (!ctx) {
            return;
        }

        ctx.save();
        ctx.clearRect(0, 0, this.canvasElement.width, this.canvasElement.height);

        if (!landmarks) {
            ctx.restore();
            return;
        }

        if (this.config.mirror) {
            ctx.translate(this.canvasElement.width, 0);
            ctx.scale(-1, 1);
        }

        this.drawMotionTrail(ctx);
        this.drawConnections(ctx, landmarks);
        this.drawLandmarks(ctx, landmarks);
        this.drawAngles(ctx, landmarks, angles);
        this.drawCalibrationGuide(ctx, landmarks);

        ctx.restore();
    }

    drawMotionTrail(ctx) {
        if (this.skeletonHistory.length < 2) {
            return;
        }

        const width = this.canvasElement.width;
        const height = this.canvasElement.height;

        this.skeletonHistory.forEach((historyFrame, frameIndex) => {
            const opacity = (frameIndex + 1) / this.skeletonHistory.length;
            ctx.strokeStyle = `rgba(64, 209, 255, ${opacity * 0.18})`;
            ctx.lineWidth = 1 + (opacity * 1.5);
            DEFAULT_CONNECTIONS.forEach(([start, end]) => {
                const startPoint = historyFrame[start];
                const endPoint = historyFrame[end];
                if (!startPoint || !endPoint) {
                    return;
                }
                ctx.beginPath();
                ctx.moveTo(startPoint.x * width, startPoint.y * height);
                ctx.lineTo(endPoint.x * width, endPoint.y * height);
                ctx.stroke();
            });
        });
    }

    drawConnections(ctx, landmarks) {
        const width = this.canvasElement.width;
        const height = this.canvasElement.height;
        DEFAULT_CONNECTIONS.forEach(([start, end]) => {
            const startPoint = landmarks[start];
            const endPoint = landmarks[end];
            if (!startPoint || !endPoint || startPoint.visibility < 0.4 || endPoint.visibility < 0.4) {
                return;
            }
            ctx.strokeStyle = "rgba(111, 255, 199, 0.82)";
            ctx.lineWidth = 3;
            ctx.beginPath();
            ctx.moveTo(startPoint.x * width, startPoint.y * height);
            ctx.lineTo(endPoint.x * width, endPoint.y * height);
            ctx.stroke();
        });
    }

    drawLandmarks(ctx, landmarks) {
        const width = this.canvasElement.width;
        const height = this.canvasElement.height;
        const badJoints = new Set(this.lastMetrics?.badJointNames || []);

        landmarks.forEach((landmark, index) => {
            if (!landmark || landmark.visibility < 0.4) {
                return;
            }
            const jointName = Object.keys(LANDMARK_LABELS).find((key) => LANDMARK_LABELS[key] === index);
            const isBadJoint = jointName && badJoints.has(jointName);
            const radius = isBadJoint ? 8 : 6;
            ctx.fillStyle = isBadJoint ? "rgba(255, 95, 122, 0.95)" : "rgba(120, 255, 171, 0.92)";
            ctx.shadowColor = isBadJoint ? "rgba(255, 95, 122, 0.9)" : "rgba(120, 255, 171, 0.7)";
            ctx.shadowBlur = 16;
            ctx.beginPath();
            ctx.arc(landmark.x * width, landmark.y * height, radius, 0, Math.PI * 2);
            ctx.fill();
        });
        ctx.shadowBlur = 0;
    }

    drawAngles(ctx, landmarks, angles) {
        const width = this.canvasElement.width;
        const height = this.canvasElement.height;
        ctx.font = "600 12px Sora, system-ui, sans-serif";
        ctx.textAlign = "center";

        Object.entries(angles).forEach(([jointName, angle]) => {
            const index = LANDMARK_LABELS[jointName];
            const point = landmarks[index];
            if (!point) {
                return;
            }
            const x = point.x * width;
            const y = (point.y * height) - 18;
            ctx.fillStyle = "rgba(6, 10, 20, 0.82)";
            ctx.beginPath();
            ctx.roundRect(x - 24, y - 12, 48, 22, 10);
            ctx.fill();
            ctx.fillStyle = "rgba(245, 252, 255, 0.95)";
            ctx.fillText(`${Math.round(angle)}°`, x, y + 3);
        });
    }

    drawCalibrationGuide(ctx, landmarks) {
        const calibration = this.getCalibration(landmarks);
        const width = this.canvasElement.width;
        const height = this.canvasElement.height;

        ctx.strokeStyle = calibration.ready ? "rgba(111, 255, 199, 0.5)" : "rgba(255, 190, 92, 0.45)";
        ctx.lineWidth = 2;
        ctx.setLineDash([8, 8]);
        ctx.strokeRect(width * 0.18, height * 0.1, width * 0.64, height * 0.78);
        ctx.setLineDash([]);
    }

    getCalibration(landmarks) {
        const leftShoulder = landmarks[11];
        const rightShoulder = landmarks[12];
        const leftAnkle = landmarks[27];
        const rightAnkle = landmarks[28];
        if (!leftShoulder || !rightShoulder || !leftAnkle || !rightAnkle) {
            return {
                ready: false,
                framing: "center-body",
                distance: "unknown",
                message: "Step into frame so the full body is visible.",
            };
        }

        const shoulderWidth = Math.abs(leftShoulder.x - rightShoulder.x);
        const bodyHeight = Math.abs(((leftShoulder.y + rightShoulder.y) / 2) - ((leftAnkle.y + rightAnkle.y) / 2));
        const centered = Math.abs(((leftShoulder.x + rightShoulder.x) / 2) - 0.5) < 0.1;

        let distance = "good";
        let message = "Perfect distance. Hold still for auto-calibration.";

        if (bodyHeight < 0.45) {
            distance = "too_far";
            message = "Move closer so joints stay readable.";
        } else if (bodyHeight > 0.9) {
            distance = "too_close";
            message = "Take one small step back to fit the full body.";
        } else if (shoulderWidth < 0.12) {
            distance = "angled";
            message = "Turn your body slightly more toward the camera.";
        } else if (!centered) {
            distance = "off_center";
            message = "Shift a little toward the center marker.";
        }

        return {
            ready: centered && distance === "good",
            framing: centered ? "centered" : "shift",
            distance,
            message,
        };
    }

    calculateAngle(p1, p2, p3) {
        const v1 = { x: p1.x - p2.x, y: p1.y - p2.y };
        const v2 = { x: p3.x - p2.x, y: p3.y - p2.y };
        const dotProduct = (v1.x * v2.x) + (v1.y * v2.y);
        const mag1 = Math.hypot(v1.x, v1.y);
        const mag2 = Math.hypot(v2.x, v2.y);
        if (!mag1 || !mag2) {
            return 0;
        }
        const cosine = Math.min(1, Math.max(-1, dotProduct / (mag1 * mag2)));
        return (Math.acos(cosine) * 180) / Math.PI;
    }

    extractJointAngles(landmarks) {
        const angleMap = {
            left_elbow: [11, 13, 15],
            right_elbow: [12, 14, 16],
            left_knee: [23, 25, 27],
            right_knee: [24, 26, 28],
            left_hip: [11, 23, 25],
            right_hip: [12, 24, 26],
            left_shoulder: [13, 11, 23],
            right_shoulder: [14, 12, 24],
            spine: [11, 23, 25],
        };

        const angles = {};
        Object.entries(angleMap).forEach(([jointName, points]) => {
            const [a, b, c] = points.map((index) => landmarks[index]);
            if (a && b && c) {
                angles[jointName] = this.calculateAngle(a, b, c);
            }
        });
        return angles;
    }

    getConfidenceScore(landmarks) {
        const visible = landmarks.filter((landmark) => landmark.visibility !== undefined);
        if (!visible.length) {
            return 0;
        }
        const average = visible.reduce((sum, landmark) => sum + landmark.visibility, 0) / visible.length;
        return Math.round(average * 100);
    }
}

window.PoseDetector = PoseDetector;
