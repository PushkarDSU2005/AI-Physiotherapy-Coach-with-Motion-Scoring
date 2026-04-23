(function () {
    function readJsonScript(id) {
        const element = document.getElementById(id);
        return element ? JSON.parse(element.textContent) : [];
    }

    function axisStyle() {
        return {
            ticks: { color: "rgba(219, 233, 255, 0.58)" },
            grid: { color: "rgba(255,255,255,0.06)" },
        };
    }

    function makeChart(nodeId, config) {
        const element = document.getElementById(nodeId);
        if (!element || typeof Chart === "undefined") {
            return null;
        }
        return new Chart(element, config);
    }

    function buildScoreTimeline() {
        const timeline = readJsonScript("score-timeline-data");
        makeChart("scoreTimelineChart", {
            type: "line",
            data: {
                labels: timeline.map((row) => row.label),
                datasets: [
                    {
                        data: timeline.map((row) => row.score),
                        borderColor: "#45dbbf",
                        backgroundColor: "rgba(69, 219, 191, 0.18)",
                        fill: true,
                        borderWidth: 2,
                        pointRadius: 0,
                        tension: 0.35,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: axisStyle(),
                    y: { ...axisStyle(), min: 0, max: 100 },
                },
            },
        });
    }

    function buildExerciseMix() {
        const exerciseMix = readJsonScript("exercise-mix-data");
        makeChart("exerciseMixChart", {
            type: "bar",
            data: {
                labels: exerciseMix.map((row) => row.exercise),
                datasets: [
                    {
                        label: "Sessions",
                        data: exerciseMix.map((row) => row.count),
                        backgroundColor: ["#45dbbf", "#75b8ff", "#ffbb73", "#ff6f91", "#9d8cff", "#f7f0a5"],
                        borderRadius: 12,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: { legend: { display: false } },
                scales: {
                    x: axisStyle(),
                    y: axisStyle(),
                },
            },
        });
    }

    function buildWeeklyTrends() {
        const weekly = readJsonScript("weekly-trends-data");
        makeChart("weeklyTrendsChart", {
            type: "line",
            data: {
                labels: weekly.map((row) => row.week),
                datasets: [
                    {
                        label: "Accuracy",
                        data: weekly.map((row) => row.accuracy),
                        borderColor: "#45dbbf",
                        backgroundColor: "rgba(69, 219, 191, 0.12)",
                        tension: 0.35,
                    },
                    {
                        label: "Stability",
                        data: weekly.map((row) => row.stability),
                        borderColor: "#75b8ff",
                        backgroundColor: "rgba(117, 184, 255, 0.1)",
                        tension: 0.35,
                    },
                    {
                        label: "Fatigue",
                        data: weekly.map((row) => row.fatigue),
                        borderColor: "#ffbb73",
                        backgroundColor: "rgba(255, 187, 115, 0.08)",
                        tension: 0.35,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        labels: { color: "rgba(219, 233, 255, 0.7)" },
                    },
                },
                scales: {
                    x: axisStyle(),
                    y: { ...axisStyle(), min: 0, max: 100 },
                },
            },
        });
    }

    document.addEventListener("DOMContentLoaded", () => {
        buildScoreTimeline();
        buildExerciseMix();
        buildWeeklyTrends();
    });
})();
