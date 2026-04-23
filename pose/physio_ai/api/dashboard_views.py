from rest_framework.decorators import api_view
from rest_framework.response import Response

from analytics.services import build_analytics_context, build_dashboard_context


@api_view(["GET"])
def get_dashboard_metrics(request):
    context = build_dashboard_context(request.user)
    summary = context["summary"]
    return Response(
        {
            "average_score": summary["average_score"],
            "best_score": summary["best_score"],
            "total_sessions": summary["total_sessions"],
            "active_plans": summary["active_plans"],
            "accuracy_rate": summary["accuracy_rate"],
            "streak_days": summary["streak_days"],
            "risk_trend": summary["risk_trend"],
            "insights": context["insights"],
        }
    )


@api_view(["GET"])
def get_chart_data(request):
    context = build_analytics_context(request.user)
    return Response(
        {
            "score_timeline": context["score_timeline"],
            "weekly_trends": context["weekly_trends"],
            "heatmap_rows": context["heatmap_rows"],
            "report_count": context["report_count"],
        }
    )
