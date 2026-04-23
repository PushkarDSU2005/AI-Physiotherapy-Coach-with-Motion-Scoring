(function () {
    const bootstrap = window.physioCaptureConfig || {};
    const scoreHistory = [];
    let detector = null;
    let worker = null;
    let chart = null;
    let frameNumber = 0;
    let lastSpeechAt = 0;
    let lastServerSyncAt = 0;
    let liveMetrics = {
        accuracy: 0,
        stability: 0,
        fatigue: 0,
        repCount: 0,
        badJointNames: [],
        jointDiagnostics: [],
    };

    function $(id) {
        return document.getElementById(id);
    }

    function setText(id, value) {
        const element = $(id);
        if (element) {
            element.textContent = value;
        }
    }

    function updateMeter(id, value) {
        const fill = document.querySelector(`[data-meter="${id}"]`);
        const label = document.querySelector(`[data-meter-label="${id}"]`);
        if (fill) {
            fill.style.width = `${Math.max(0, Math.min(100, value))}%`;
        }
        if (label) {
            label.textContent = `${Math.round(value)}%`;
        }
    }

    function initializeChart() {
        const canvas = $("liveScoreChart");
        if (!canvas || typeof Chart === "undefined") {
            return;
        }

        chart = new Chart(canvas, {
            type: "line",
            data: {
                labels: [],
                datasets: [
                    {
                        label: "Form score",
                        data: [],
                        borderColor: "#74f0c0",
                        backgroundColor: "rgba(116, 240, 192, 0.18)",
                        fill: true,
                        tension: 0.35,
                        pointRadius: 0,
                        borderWidth: 2,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: false,
                plugins: {
                    legend: { display: false },
                    tooltip: { enabled: false },
                },
                scales: {
                    x: {
                        display: false,
                        grid: { display: false },
                    },
                    y: {
                        min: 0,
                        max: 100,
                        ticks: { color: "rgba(219, 233, 255, 0.55)" },
                        grid: { color: "rgba(255,255,255,0.06)" },
                    },
                },
            },
        });
    }

    function initializeWorker() {
        worker = new Worker("/static/js/pose_metrics_worker.js");
        worker.postMessage({
            type: "configure",
            payload: {
                exerciseType: bootstrap.exerciseType || "squat",
            },
        });

        worker.onmessage = (event) => {
            liveMetrics = event.data;
            detector?.updateLiveMetrics(liveMetrics);
            renderMetrics();
        };
    }

    function renderMetrics() {
        setText("repCount", String(liveMetrics.repCount));
        setText("accuracyValue", `${Math.round(liveMetrics.accuracy)}%`);
        setText("stabilityValue", `${Math.round(liveMetrics.stability)}%`);
        setText("fatigueValue", `${Math.round(liveMetrics.fatigue)}%`);

        updateMeter("accuracy", liveMetrics.accuracy);
        updateMeter("stability", liveMetrics.stability);
        updateMeter("fatigue", liveMetrics.fatigue);

        const jointList = $("jointSignals");
        if (jointList) {
            jointList.innerHTML = "";
            const diagnostics = liveMetrics.jointDiagnostics?.length
                ? liveMetrics.jointDiagnostics
                : [{ jointName: "all joints", severity: "low", delta: 0 }];
            diagnostics.slice(0, 4).forEach((diagnostic) => {
                const chip = document.createElement("div");
                chip.className = `joint-chip severity-${diagnostic.severity}`;
                chip.textContent = diagnostic.delta
                    ? `${diagnostic.jointName.replaceAll("_", " ")} +${Math.round(diagnostic.delta)}°`
                    : "Alignment stable";
                jointList.appendChild(chip);
            });
        }
    }

    function pushScore(score) {
        scoreHistory.push(Math.round(score));
        while (scoreHistory.length > 32) {
            scoreHistory.shift();
        }
        if (!chart) {
            return;
        }
        chart.data.labels = scoreHistory.map((_, index) => index + 1);
        chart.data.datasets[0].data = scoreHistory;
        chart.update();
    }

    function startTimer() {
        const startedAt = Date.now();
        window.setInterval(() => {
            const elapsed = Math.floor((Date.now() - startedAt) / 1000);
            const minutes = String(Math.floor(elapsed / 60)).padStart(2, "0");
            const seconds = String(elapsed % 60).padStart(2, "0");
            setText("sessionTimer", `${minutes}:${seconds}`);
        }, 1000);
    }

    function speakMessage(message, intervalMs = 3200) {
        if (!("speechSynthesis" in window) || !bootstrap.voiceEnabled) {
            return;
        }
        const now = Date.now();
        if ((now - lastSpeechAt) < intervalMs) {
            return;
        }

        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(localizeMessage(message));
        utterance.lang = bootstrap.language === "hi" ? "hi-IN" : "en-IN";
        utterance.rate = 1;
        utterance.pitch = 1;
        window.speechSynthesis.speak(utterance);
        lastSpeechAt = now;
    }

    function localizeMessage(message) {
        if (bootstrap.language !== "hi") {
            return message;
        }

        const dictionary = [
            ["Good job, keep going.", "बहुत अच्छा, ऐसे ही जारी रखें।"],
            ["Lower your hips a little more for better depth.", "और बेहतर गहराई के लिए अपने हिप्स को थोड़ा और नीचे लाएं।"],
            ["Drive your left knee slightly outward.", "अपने बाएं घुटने को थोड़ा बाहर की ओर रखें।"],
            ["Track your right knee over your toes.", "अपने दाएं घुटने को पैर की उंगलियों की दिशा में रखें।"],
            ["Lift your chest and keep the torso more upright.", "अपना सीना ऊपर रखें और धड़ को अधिक सीधा रखें।"],
            ["Pause and correct now.", "रुकें और अभी सुधार करें।"],
            ["Movement speed is dropping. Take a breath and reset before the next rep.", "आपकी गति धीमी हो रही है। अगली रेप से पहले सांस लें और फिर से संतुलित हों।"],
            ["Slow the tempo slightly and stabilize before driving the next rep.", "अगली रेप से पहले गति थोड़ी धीमी करें और शरीर को स्थिर रखें।"],
            ["You're close. Keep the movement controlled and stay aligned.", "आप सही दिशा में हैं। मूवमेंट को नियंत्रित रखें और शरीर की लाइन बनाए रखें।"],
        ];

        let translated = message;
        dictionary.forEach(([english, hindi]) => {
            translated = translated.replaceAll(english, hindi);
        });
        return translated;
    }

    function updateFeedbackPanel(feedback) {
        const message = feedback?.coaching_message || "Move into frame to begin live coaching.";
        setText("coachMessage", message);
        setText("confidenceValue", `${Math.round(feedback?.confidence || 0)}%`);

        const priorityList = $("priorityList");
        if (priorityList) {
            priorityList.innerHTML = "";
            const items = feedback?.prioritized_feedback?.length
                ? feedback.prioritized_feedback
                : [{ severity: "low", message: "Great posture. Maintain the same line." }];
            items.forEach((item) => {
                const element = document.createElement("div");
                element.className = `priority-card severity-${item.severity}`;
                element.innerHTML = `
                    <span class="priority-pill">${item.severity.toUpperCase()}</span>
                    <p>${item.message}</p>
                `;
                priorityList.appendChild(element);
            });
        }

        const adaptive = feedback?.difficulty_adjustment;
        setText(
            "adaptiveAdjustment",
            adaptive ? `${adaptive.action.replaceAll("_", " ")}: ${adaptive.reason}` : "Collecting enough performance history to auto-adjust difficulty."
        );

        const trend = feedback?.injury_risk_trend || "stable";
        setText("riskTrend", trend.toUpperCase());
        speakMessage(message, feedback?.adaptive_feedback_interval_ms || 3200);
    }

    async function syncFrameToServer(payload) {
        if (bootstrap.demoMode) {
            return {
                feedback: {
                    coaching_message: liveMetrics.badJointNames.length
                        ? "Lower your hips slightly and keep the torso upright."
                        : "Good job, keep going.",
                    confidence: payload.confidence,
                    prioritized_feedback: liveMetrics.jointDiagnostics.map((diagnostic) => ({
                        severity: diagnostic.severity,
                        message: `${diagnostic.jointName.replaceAll("_", " ")} needs correction.`,
                    })),
                    adaptive_feedback_interval_ms: 2800,
                    difficulty_adjustment: {
                        action: liveMetrics.accuracy > 85 ? "increase_reps" : "maintain",
                        reason: liveMetrics.accuracy > 85
                            ? "Accuracy is strong enough to add a little more volume."
                            : "Hold the current dose while form stabilizes.",
                    },
                    injury_risk_trend: liveMetrics.fatigue > 40 ? "rising" : "stable",
                },
            };
        }

        const response = await fetch("/sessions/api/upload_pose_frame/", {
            method: "POST",
            credentials: "same-origin",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": bootstrap.csrfToken || "",
            },
            body: JSON.stringify({
                session_exercise_id: bootstrap.sessionExerciseId,
                frame_number: frameNumber,
                landmarks: payload.rawLandmarks.map((landmark) => [
                    landmark.x,
                    landmark.y,
                    landmark.z || 0,
                    landmark.visibility || 0,
                ]),
                exercise_type: bootstrap.exerciseType || "squat",
            }),
        });
        return response.json();
    }

    async function handlePose(payload) {
        frameNumber += 1;
        setText("fpsValue", `${payload.fps || 0}`);
        setText("formScoreValue", `${Math.round(liveMetrics.accuracy || 0)}%`);
        setText("calibrationValue", payload.calibration.ready ? "READY" : payload.calibration.distance.toUpperCase());
        setText("calibrationHint", payload.calibration.message);

        worker.postMessage({
            type: "pose",
            payload: {
                angles: payload.angles,
                fps: payload.fps,
            },
        });

        pushScore(liveMetrics.accuracy || 0);

        const now = Date.now();
        if ((now - lastServerSyncAt) < 900) {
            return;
        }

        lastServerSyncAt = now;
        try {
            const result = await syncFrameToServer(payload);
            if (result?.feedback) {
                updateFeedbackPanel(result.feedback);
            }
        } catch (error) {
            console.error("Live sync failed", error);
        }
    }

    async function setupCameraSelect() {
        const select = $("cameraSelect");
        if (!select) {
            return;
        }

        const cameras = await detector.listCameras();
        select.innerHTML = "";
        cameras.forEach((camera, index) => {
            const option = document.createElement("option");
            option.value = camera.deviceId;
            option.textContent = camera.label || `Camera ${index + 1}`;
            select.appendChild(option);
        });

        select.addEventListener("change", async () => {
            detector.stopCamera();
            await detector.startCamera(select.value);
        });
    }

    async function boot() {
        initializeChart();
        initializeWorker();
        startTimer();
        detector = new window.PoseDetector({
            videoId: "poseVideo",
            canvasId: "poseCanvas",
            onPose: handlePose,
            onStatus: ({ fps }) => setText("fpsValue", `${fps}`),
            targetFps: 20,
        });

        await detector.initialize();
        await setupCameraSelect();
        await detector.startCamera();

        $("coachLanguage")?.addEventListener("change", (event) => {
            bootstrap.language = event.target.value;
        });

        setText("exerciseName", bootstrap.exerciseName || "Bodyweight Squat");
        setText("coachMessage", "Camera is ready. Hold the setup position for auto-calibration.");
        renderMetrics();
    }

    document.addEventListener("DOMContentLoaded", boot);
})();
