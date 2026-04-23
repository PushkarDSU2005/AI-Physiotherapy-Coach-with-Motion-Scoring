import json
from collections import Counter, defaultdict
from datetime import timedelta

from django.contrib.auth.models import AnonymousUser
from django.db.models import Avg
from django.utils import timezone

from advanced_features.models import DifficultyAdaptation, InjuryRiskAlert
from analytics.models import DailyMetrics, Report, UserProgress
from sessions.models import Session, SessionExercise
from therapy_plans.models import TherapyPlan, WeeklyExercise
from users.models import UserProfile


COLOR_SCALE = {
    "excellent": "emerald",
    "good": "amber",
    "warning": "rose",
}


def _safe_user(user):
    if not user or isinstance(user, AnonymousUser) or not getattr(user, "is_authenticated", False):
        return None
    return user


def _score_band(score):
    if score >= 85:
        return "excellent"
    if score >= 70:
        return "good"
    return "warning"


def _session_exercise_score(session_exercise):
    if session_exercise.form_score is not None:
        return float(session_exercise.form_score)

    pose_average = session_exercise.pose_analyses.aggregate(avg_score=Avg("form_score"))["avg_score"]
    return round(float(pose_average or 0), 1)


def _session_exercise_stability(session_exercise):
    confidence_average = session_exercise.pose_analyses.aggregate(avg_conf=Avg("confidence_level"))["avg_conf"]
    return round(float(confidence_average or 0), 1)


def _user_card(user):
    if not user:
        return {
            "name": "Demo Patient",
            "age": 28,
            "gender": "Recovery",
            "avatar_initial": "DP",
            "fitness_level": "adaptive",
        }

    try:
        profile = user.profile
    except UserProfile.DoesNotExist:
        profile = None

    first_name = user.first_name or user.username
    avatar_initial = "".join(part[0] for part in first_name.split()[:2]).upper() or user.username[:2].upper()
    return {
        "name": first_name.title(),
        "age": getattr(profile, "age", None) or 29,
        "gender": "Adaptive Care",
        "avatar_initial": avatar_initial,
        "fitness_level": getattr(profile, "fitness_level", "adaptive"),
    }


def _demo_dashboard_context():
    score_timeline = [
        {"label": "Mon", "score": 74},
        {"label": "Tue", "score": 78},
        {"label": "Wed", "score": 81},
        {"label": "Thu", "score": 84},
        {"label": "Fri", "score": 87},
        {"label": "Sat", "score": 86},
        {"label": "Sun", "score": 89},
    ]
    exercise_mix = [
        {"exercise": "Squat Therapy", "count": 8, "average_score": 86},
        {"exercise": "Shoulder Mobility", "count": 6, "average_score": 82},
        {"exercise": "Hip Stability", "count": 4, "average_score": 79},
    ]
    weakness_heatmap = [
        {"joint": "Knee", "score": 72, "trend": -2.5, "severity": "warning"},
        {"joint": "Hip", "score": 79, "trend": 1.2, "severity": "good"},
        {"joint": "Shoulder", "score": 88, "trend": 2.0, "severity": "excellent"},
        {"joint": "Lumbar", "score": 76, "trend": -0.4, "severity": "good"},
    ]
    weekly_trends = [
        {"week": "W1", "accuracy": 71, "stability": 66, "fatigue": 32},
        {"week": "W2", "accuracy": 75, "stability": 70, "fatigue": 29},
        {"week": "W3", "accuracy": 80, "stability": 76, "fatigue": 26},
        {"week": "W4", "accuracy": 86, "stability": 83, "fatigue": 22},
    ]
    return {
        "user": _user_card(None),
        "summary": {
            "average_score": 83.4,
            "best_score": 92.0,
            "total_sessions": 18,
            "active_plans": 2,
            "risk_trend": "down",
            "accuracy_rate": 88,
            "streak_days": 5,
        },
        "hero_alert": {
            "title": "AI coach sees steady improvement",
            "message": "Knee alignment risk is trending down while squat depth and stability are improving week over week.",
            "tone": "good",
        },
        "score_timeline": score_timeline,
        "exercise_mix": exercise_mix,
        "weakness_heatmap": weakness_heatmap,
        "weekly_trends": weekly_trends,
        "recent_sessions": [
            {
                "date": "2026-04-21",
                "exercise": "Bodyweight Squat",
                "score": 89,
                "stability": 86,
                "fatigue": 18,
                "status": "Excellent",
            },
            {
                "date": "2026-04-20",
                "exercise": "Shoulder Raise",
                "score": 84,
                "stability": 81,
                "fatigue": 24,
                "status": "Improving",
            },
        ],
        "insights": [
            "Increase reps for squat therapy because your last three sessions averaged above 85%.",
            "Lumbar stability dips near the last third of sessions, suggesting mild fatigue accumulation.",
            "Shoulder mobility accuracy improves when tempo stays under 2.5 seconds per rep.",
        ],
    }


def build_dashboard_context(user):
    user = _safe_user(user)
    if not user:
        return _demo_dashboard_context()

    session_exercises = list(
        SessionExercise.objects.filter(session__user=user)
        .select_related("session", "exercise")
        .prefetch_related("pose_analyses")
        .order_by("-session__start_time")
    )
    if not session_exercises:
        return _demo_dashboard_context()

    scores = []
    timeline_buckets = defaultdict(list)
    exercise_buckets = defaultdict(list)

    for item in session_exercises:
        score = _session_exercise_score(item)
        if not score:
            continue
        session_date = item.session.start_time.date().isoformat()
        scores.append(score)
        timeline_buckets[session_date].append(score)
        exercise_buckets[item.exercise.name].append(score)

    avg_score = round(sum(scores) / len(scores), 1) if scores else 0
    best_score = round(max(scores), 1) if scores else 0

    last_14_days = timezone.now().date() - timedelta(days=13)
    score_timeline = []
    current_date = last_14_days
    while current_date <= timezone.now().date():
        day_scores = timeline_buckets.get(current_date.isoformat(), [])
        score_timeline.append(
            {
                "label": current_date.strftime("%d %b"),
                "score": round(sum(day_scores) / len(day_scores), 1) if day_scores else 0,
            }
        )
        current_date += timedelta(days=1)

    exercise_mix = [
        {
            "exercise": name,
            "count": len(values),
            "average_score": round(sum(values) / len(values), 1),
        }
        for name, values in sorted(
            exercise_buckets.items(),
            key=lambda entry: (len(entry[1]), sum(entry[1]) / len(entry[1])),
            reverse=True,
        )[:6]
    ]

    alerts = list(
        InjuryRiskAlert.objects.filter(session_exercise__session__user=user)
        .order_by("-detected_at")[:50]
    )
    joint_counter = Counter()
    joint_risk = defaultdict(list)
    for alert in alerts:
        label = (alert.joint_name or "unknown").replace("_", " ").title()
        joint_counter[label] += 1
        joint_risk[label].append(100 - min(float(alert.severity_score), 100))

    weakness_heatmap = []
    for joint, count in joint_counter.most_common(6):
        risk_scores = joint_risk[joint]
        weakness_heatmap.append(
            {
                "joint": joint,
                "score": round(sum(risk_scores) / len(risk_scores), 1),
                "trend": round(-(count / max(len(alerts), 1)) * 10, 1),
                "severity": _score_band(round(sum(risk_scores) / len(risk_scores), 1)),
            }
        )

    if not weakness_heatmap:
        issue_counter = Counter()
        issue_scores = defaultdict(list)
        for item in session_exercises[:20]:
            for analysis in item.pose_analyses.all():
                for issue in analysis.issues_detected or []:
                    label = str(issue).replace("_", " ").title()
                    issue_counter[label] += 1
                    issue_scores[label].append(float(analysis.form_score))
        for joint, _ in issue_counter.most_common(6):
            values = issue_scores[joint] or [avg_score]
            weakness_heatmap.append(
                {
                    "joint": joint,
                    "score": round(sum(values) / len(values), 1),
                    "trend": -1.0,
                    "severity": _score_band(round(sum(values) / len(values), 1)),
                }
            )

    weekly_trends = []
    for week_start_offset in range(21, -1, -7):
        start = timezone.now().date() - timedelta(days=week_start_offset + 6)
        end = timezone.now().date() - timedelta(days=week_start_offset)
        weekly_items = [
            item for item in session_exercises
            if start <= item.session.start_time.date() <= end
        ]
        week_scores = [_session_exercise_score(item) for item in weekly_items if _session_exercise_score(item)]
        week_stability = [_session_exercise_stability(item) for item in weekly_items if _session_exercise_stability(item)]
        weekly_trends.append(
            {
                "week": f"{start.strftime('%d %b')}",
                "accuracy": round(sum(week_scores) / len(week_scores), 1) if week_scores else 0,
                "stability": round(sum(week_stability) / len(week_stability), 1) if week_stability else 0,
                "fatigue": max(0, round(100 - (sum(week_stability) / len(week_stability)), 1)) if week_stability else 0,
            }
        )

    active_plans = TherapyPlan.objects.filter(user=user, status="active").count()
    streak_days = 0
    day_pointer = timezone.now().date()
    completed_dates = {item.session.start_time.date() for item in session_exercises}
    while day_pointer in completed_dates:
        streak_days += 1
        day_pointer -= timedelta(days=1)

    risk_trend = "down"
    if len(alerts) >= 6:
        recent = len([alert for alert in alerts[:3]])
        previous = len([alert for alert in alerts[3:6]])
        if recent > previous:
            risk_trend = "up"

    latest_items = session_exercises[:6]
    recent_sessions = [
        {
            "date": item.session.start_time.strftime("%Y-%m-%d"),
            "exercise": item.exercise.name,
            "score": round(_session_exercise_score(item), 1),
            "stability": round(_session_exercise_stability(item), 1),
            "fatigue": max(0, round(100 - _session_exercise_stability(item), 1)),
            "status": "Excellent" if _session_exercise_score(item) >= 85 else "Needs focus",
        }
        for item in latest_items
    ]

    adaptations = list(
        DifficultyAdaptation.objects.filter(user=user)
        .select_related("exercise")
        .order_by("-updated_at")[:3]
    )
    insights = []
    for adaptation in adaptations:
        action = adaptation.recommendation.replace("_", " ").title()
        insights.append(
            f"{adaptation.exercise.name}: {action} because the last sessions averaged {adaptation.average_score:.1f} with {adaptation.trend} momentum."
        )

    if not insights:
        weakest = weakness_heatmap[0]["joint"] if weakness_heatmap else "movement quality"
        insights = [
            f"Priority focus area is {weakest.lower()} because it shows the most repeated correction signals.",
            "Auto-adjust intensity when exercise averages stay above 85% for three sessions in a row.",
            "Use stability drops near the end of sessions as an early fatigue marker for rest guidance.",
        ]

    hero_tone = "good" if avg_score >= 80 else "warning"
    hero_alert = {
        "title": "Live performance is trending up" if hero_tone == "good" else "AI coach recommends a lighter recovery block",
        "message": (
            f"Average form score is {avg_score} across {len(session_exercises)} recorded exercise blocks. "
            f"{'Risk signals are declining and consistency is improving.' if risk_trend == 'down' else 'Recent risk signals increased, so technique should be prioritized before volume.'}"
        ),
        "tone": hero_tone,
    }

    return {
        "user": _user_card(user),
        "summary": {
            "average_score": avg_score,
            "best_score": best_score,
            "total_sessions": Session.objects.filter(user=user).count(),
            "active_plans": active_plans,
            "risk_trend": risk_trend,
            "accuracy_rate": round(avg_score, 1),
            "streak_days": streak_days,
        },
        "hero_alert": hero_alert,
        "score_timeline": score_timeline,
        "exercise_mix": exercise_mix,
        "weakness_heatmap": weakness_heatmap[:6],
        "weekly_trends": weekly_trends,
        "recent_sessions": recent_sessions,
        "insights": insights,
    }


def build_therapy_context(user):
    user = _safe_user(user)
    if not user:
        return {
            "overview": {
                "total_plans": 4,
                "active_plans": 2,
                "completion_rate": 78,
                "readiness_score": 84,
            },
            "plan_cards": [
                {
                    "title": "Knee Recovery Sprint",
                    "injury_type": "Patellofemoral tracking",
                    "status": "active",
                    "duration_weeks": 6,
                    "progress_score": 68,
                    "goals": ["Reduce pain", "Restore squat depth"],
                    "precautions": ["Avoid deep loaded flexion"],
                }
            ],
            "weekly_schedule": [],
        }

    plans = list(TherapyPlan.objects.filter(user=user).order_by("-updated_at"))
    weekly_schedule = []
    active_plan_ids = [plan.id for plan in plans[:3]]
    assignments = WeeklyExercise.objects.filter(therapy_plan_id__in=active_plan_ids).order_by(
        "week_number", "day_of_week", "order"
    )
    for assignment in assignments[:12]:
        weekly_schedule.append(
            {
                "week": assignment.week_number,
                "day": assignment.get_day_of_week_display(),
                "exercise": assignment.exercise_name,
                "dose": f"{assignment.sets} x {assignment.reps}",
                "duration_minutes": assignment.duration_minutes,
                "rest_seconds": assignment.rest_seconds,
                "rest_day": assignment.is_rest_day,
            }
        )

    readiness_base = build_dashboard_context(user)["summary"]["average_score"]
    return {
        "overview": {
            "total_plans": len(plans),
            "active_plans": len([plan for plan in plans if plan.status == "active"]),
            "completion_rate": round(
                sum(plan.progress_score for plan in plans) / len(plans), 1
            ) if plans else 0,
            "readiness_score": round(min(100, readiness_base + 4), 1),
        },
        "plan_cards": [
            {
                "title": plan.title or f"{plan.injury_type.title()} Recovery Plan",
                "injury_type": plan.injury_type,
                "status": plan.status,
                "duration_weeks": plan.duration_weeks,
                "progress_score": round(plan.progress_score, 1),
                "goals": plan.goals[:3],
                "precautions": plan.precautions[:2],
            }
            for plan in plans[:4]
        ],
        "weekly_schedule": weekly_schedule,
    }


def build_analytics_context(user):
    user = _safe_user(user)
    dashboard = build_dashboard_context(user)
    if not user:
        report_count = 6
    else:
        report_count = Report.objects.filter(user=user).count()

    heatmap_rows = []
    for row in dashboard["weakness_heatmap"]:
        heatmap_rows.append(
            {
                "joint": row["joint"],
                "score": row["score"],
                "severity": row["severity"],
            }
        )

    return {
        "overview": dashboard["summary"],
        "score_timeline": dashboard["score_timeline"],
        "weekly_trends": dashboard["weekly_trends"],
        "heatmap_rows": heatmap_rows,
        "insights": dashboard["insights"],
        "report_count": report_count,
        "export_ready": report_count > 0,
    }


def context_json(payload):
    return json.dumps(payload)
