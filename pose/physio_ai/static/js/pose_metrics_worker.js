const DEFAULT_PROFILE = {
    squat: {
        keyJoints: {
            left_knee: [75, 115],
            right_knee: [75, 115],
            left_hip: [65, 120],
            right_hip: [65, 120],
            spine: [70, 105],
        },
        repDriver: "left_knee",
        lowThreshold: 95,
        highThreshold: 150,
    },
    plank: {
        keyJoints: {
            spine: [160, 178],
            left_hip: [160, 178],
            right_hip: [160, 178],
            left_shoulder: [70, 110],
            right_shoulder: [70, 110],
        },
        repDriver: "spine",
        lowThreshold: 165,
        highThreshold: 176,
    },
};

const state = {
    profile: DEFAULT_PROFILE.squat,
    angleHistory: [],
    repState: "up",
    repCount: 0,
};

function average(values) {
    if (!values.length) {
        return 0;
    }
    return values.reduce((sum, value) => sum + value, 0) / values.length;
}

function variance(values) {
    if (values.length < 2) {
        return 0;
    }
    const avg = average(values);
    return average(values.map((value) => Math.pow(value - avg, 2)));
}

function computeBadJoints(angles) {
    const badJointNames = [];
    const jointDiagnostics = [];

    Object.entries(state.profile.keyJoints).forEach(([jointName, [min, max]]) => {
        const value = angles[jointName];
        if (value === undefined || value === null) {
            return;
        }
        const delta = value < min ? min - value : value > max ? value - max : 0;
        if (delta > 0) {
            badJointNames.push(jointName);
            jointDiagnostics.push({
                jointName,
                delta: Math.round(delta * 10) / 10,
                severity: delta > 18 ? "high" : delta > 9 ? "medium" : "low",
            });
        }
    });

    return { badJointNames, jointDiagnostics };
}

function computeRepCount(angles) {
    const driverValue = angles[state.profile.repDriver];
    if (driverValue === undefined || driverValue === null) {
        return state.repCount;
    }

    if (state.repState === "up" && driverValue < state.profile.lowThreshold) {
        state.repState = "down";
    } else if (state.repState === "down" && driverValue > state.profile.highThreshold) {
        state.repState = "up";
        state.repCount += 1;
    }

    return state.repCount;
}

function computeStability(history) {
    const samples = history.slice(-10).map((frame) => frame.formScore);
    return Math.max(0, Math.min(100, 100 - Math.sqrt(variance(samples)) * 5.2));
}

function computeFatigue(history) {
    if (history.length < 8) {
        return 18;
    }

    const earlyMotion = average(history.slice(-8, -4).map((frame) => frame.motionEnergy));
    const lateMotion = average(history.slice(-4).map((frame) => frame.motionEnergy));
    if (!earlyMotion) {
        return 18;
    }
    const slowdown = Math.max(0, ((earlyMotion - lateMotion) / earlyMotion) * 100);
    return Math.min(100, slowdown);
}

function computeAccuracy(angles) {
    const errors = [];
    Object.entries(state.profile.keyJoints).forEach(([jointName, [min, max]]) => {
        const value = angles[jointName];
        if (value === undefined || value === null) {
            return;
        }
        if (value < min) {
            errors.push(min - value);
        } else if (value > max) {
            errors.push(value - max);
        } else {
            errors.push(0);
        }
    });

    return Math.max(0, Math.min(100, 100 - average(errors) * 2.8));
}

function motionEnergy(currentAngles, previousAngles) {
    if (!previousAngles) {
        return 0;
    }
    return Object.keys(currentAngles).reduce((sum, jointName) => {
        const previous = previousAngles[jointName] || 0;
        return sum + Math.abs(currentAngles[jointName] - previous);
    }, 0);
}

onmessage = (event) => {
    const { type, payload } = event.data;

    if (type === "configure") {
        state.profile = DEFAULT_PROFILE[payload.exerciseType] || DEFAULT_PROFILE.squat;
        state.angleHistory = [];
        state.repState = "up";
        state.repCount = 0;
        return;
    }

    if (type !== "pose") {
        return;
    }

    const angles = payload.angles || {};
    const accuracy = computeAccuracy(angles);
    const energy = motionEnergy(angles, state.angleHistory[state.angleHistory.length - 1]?.angles);
    const snapshot = {
        angles,
        formScore: accuracy,
        motionEnergy: energy,
    };

    state.angleHistory.push(snapshot);
    state.angleHistory = state.angleHistory.slice(-40);

    const stability = computeStability(state.angleHistory);
    const fatigue = computeFatigue(state.angleHistory);
    const { badJointNames, jointDiagnostics } = computeBadJoints(angles);
    const repCount = computeRepCount(angles);

    postMessage({
        accuracy: Math.round(accuracy * 10) / 10,
        stability: Math.round(stability * 10) / 10,
        fatigue: Math.round(fatigue * 10) / 10,
        repCount,
        badJointNames,
        jointDiagnostics,
    });
};
