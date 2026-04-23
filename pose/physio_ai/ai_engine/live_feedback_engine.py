from collections import defaultdict
from statistics import mean

from django.db.models import Avg

from advanced_features.models import DifficultyAdaptation, InjuryRiskAlert


EXERCISE_PROFILES = {
    "squat": {
        "target_angles": {
            "left_knee": (75, 115),
            "right_knee": (75, 115),
            "left_hip": (65, 120),
            "right_hip": (65, 120),
            "spine": (70, 105),
        },
        "positive_messages": [
            "Good job, keep going.",
            "Depth and control look strong.",
            "Nice rhythm. Stay tall through the chest.",
        ],
        "corrections": {
            "left_knee": "Drive your left knee slightly outward.",
            "right_knee": "Track your right knee over your toes.",
            "left_hip": "Lower your hips a little more for better depth.",
            "right_hip": "Drop your hips slightly while keeping the core braced.",
            "spine": "Lift your chest and keep the torso more upright.",
        },
    },
    "plank": {
        "target_angles": {
            "spine": (160, 178),
            "left_shoulder": (70, 110),
            "right_shoulder": (70, 110),
            "left_hip": (160, 178),
            "right_hip": (160, 178),
        },
        "positive_messages": [
            "Strong line from shoulders to heels.",
            "Core engagement looks good.",
            "Nice hold. Keep breathing steadily.",
        ],
        "corrections": {
            "spine": "Brace your core and avoid letting the lower back dip.",
            "left_hip": "Raise the hips slightly into a straight line.",
            "right_hip": "Raise the hips slightly and keep the glutes engaged.",
            "left_shoulder": "Stack the shoulders more directly over the elbows.",
            "right_shoulder": "Keep shoulders directly above the elbows.",
        },
    },
}


SEVERITY_WEIGHT = {
    "low": 1,
    "medium": 2,
    "high": 3,
    "critical": 4,
}


class LiveFeedbackEngine:
    """
    Context-aware live coaching engine.

    The engine blends real-time pose issues with historical performance and risk
    signals to produce prioritized coaching, adaptive messaging, and lightweight
    auto-progression recommendations.
    """

    def __init__(self, user=None):
        self.user = user

    def generate(self, session_exercise, form_score, confidence, issues, angles=None, history=None):
        history = history or []
        exercise_name = session_exercise.exercise.name.lower().replace(" ", "_")
        profile = EXERCISE_PROFILES.get(exercise_name, EXERCISE_PROFILES.get("squat"))

        prioritized = self._prioritize_issues(issues)
        stability_score = self._stability_score(history)
        fatigue_score = self._fatigue_score(history)
        injury_risk_trend = self._injury_risk_trend(session_exercise)
        adaptation = self._difficulty_adjustment(session_exercise)
        coaching_message = self._coaching_message(
            profile=profile,
            form_score=form_score,
            prioritized=prioritized,
            stability_score=stability_score,
            fatigue_score=fatigue_score,
        )

        return {
            "exercise_type": exercise_name,
            "form_score": round(float(form_score), 1),
            "confidence": round(float(confidence), 1),
            "stability_score": stability_score,
            "fatigue_score": fatigue_score,
            "prioritized_feedback": prioritized,
            "coaching_message": coaching_message,
            "voice_feedback": coaching_message,
            "adaptive_feedback_interval_ms": self._feedback_interval(prioritized, fatigue_score),
            "injury_risk_trend": injury_risk_trend,
            "difficulty_adjustment": adaptation,
            "historical_comparison": self._historical_comparison(session_exercise),
        }

    def _prioritize_issues(self, issues):
        ranked = []
        for issue in issues:
            severity = issue.get("severity", "low")
            ranked.append(
                {
                    "type": issue.get("type", "form_issue"),
                    "joint": issue.get("joint", ""),
                    "severity": severity,
                    "message": issue.get("message", "Adjust your posture."),
                    "priority_score": SEVERITY_WEIGHT.get(severity, 1) * 10,
                }
            )
        ranked.sort(
            key=lambda item: (
                item["priority_score"],
                1 if "knee" in item["joint"] or "spine" in item["joint"] else 0,
            ),
            reverse=True,
        )
        return ranked[:3]

    def _stability_score(self, history):
        if len(history) < 3:
            return 82.0

        values = []
        for frame in history[-12:]:
            frame_score = frame.get("score")
            if frame_score is not None:
                values.append(float(frame_score))
        if len(values) < 3:
            return 82.0

        drift = sum(abs(values[index] - values[index - 1]) for index in range(1, len(values))) / (len(values) - 1)
        return round(max(0.0, min(100.0, 100.0 - (drift * 3.2))), 1)

    def _fatigue_score(self, history):
        if len(history) < 6:
            return 18.0

        early = [frame.get("score", 0) for frame in history[-12:-6] if frame.get("score") is not None]
        late = [frame.get("score", 0) for frame in history[-6:] if frame.get("score") is not None]
        if not early or not late:
            return 18.0

        drop = max(0.0, mean(early) - mean(late))
        return round(min(100.0, drop * 4), 1)

    def _feedback_interval(self, prioritized, fatigue_score):
        if prioritized and prioritized[0]["severity"] in {"high", "critical"}:
            return 1400
        if fatigue_score >= 35:
            return 2200
        return 3200

    def _coaching_message(self, profile, form_score, prioritized, stability_score, fatigue_score):
        if prioritized:
            primary = prioritized[0]
            joint = primary.get("joint", "")
            correction = profile.get("corrections", {}).get(joint, primary["message"])
            if primary["severity"] in {"high", "critical"}:
                return f"Pause and correct now. {correction}"
            return correction

        if fatigue_score >= 35:
            return "Movement speed is dropping. Take a breath and reset before the next rep."

        if stability_score < 72:
            return "Slow the tempo slightly and stabilize before driving the next rep."

        if form_score >= 88:
            return profile["positive_messages"][0]
        if form_score >= 80:
            return profile["positive_messages"][1]
        return "You're close. Keep the movement controlled and stay aligned."

    def _historical_comparison(self, session_exercise):
        historical = (
            session_exercise.__class__.objects.filter(
                session__user=session_exercise.session.user,
                exercise=session_exercise.exercise,
                form_score__isnull=False,
            )
            .exclude(id=session_exercise.id)
            .order_by("-session__start_time")[:5]
        )
        values = [float(item.form_score) for item in historical if item.form_score is not None]
        previous_average = round(mean(values), 1) if values else None
        current_score = float(session_exercise.form_score or 0)
        delta = round(current_score - previous_average, 1) if previous_average is not None else None
        return {
            "previous_average_score": previous_average,
            "delta_vs_previous_average": delta,
            "trend_label": "up" if delta and delta > 0 else "down" if delta and delta < 0 else "stable",
        }

    def _injury_risk_trend(self, session_exercise):
        recent_alerts = InjuryRiskAlert.objects.filter(
            session_exercise__session__user=session_exercise.session.user,
            session_exercise__exercise=session_exercise.exercise,
        ).order_by("-detected_at")[:8]
        if not recent_alerts:
            return "stable"

        score = sum(1 for alert in recent_alerts[:4] if alert.risk_level in {"high", "critical"})
        previous = sum(1 for alert in recent_alerts[4:8] if alert.risk_level in {"high", "critical"})
        if score > previous:
            return "rising"
        if score < previous:
            return "improving"
        return "stable"

    def _difficulty_adjustment(self, session_exercise):
        recommendation = {
            "action": "maintain",
            "reason": "Need more performance data before adapting difficulty.",
        }

        adaptation = DifficultyAdaptation.objects.filter(
            user=session_exercise.session.user,
            exercise=session_exercise.exercise,
        ).first()
        if adaptation:
            return {
                "action": adaptation.recommendation,
                "reason": adaptation.recommendation_reason,
            }

        average_score = (
            session_exercise.__class__.objects.filter(
                session__user=session_exercise.session.user,
                exercise=session_exercise.exercise,
                form_score__isnull=False,
            ).aggregate(avg_score=Avg("form_score"))["avg_score"]
            or 0
        )
        if average_score > 85:
            return {
                "action": "increase_reps",
                "reason": "Recent performance is above 85%, so volume can be progressed.",
            }
        if average_score and average_score < 60:
            return {
                "action": "decrease_reps",
                "reason": "Recent performance is below 60%, so reduce difficulty and emphasize control.",
            }
        return recommendation
