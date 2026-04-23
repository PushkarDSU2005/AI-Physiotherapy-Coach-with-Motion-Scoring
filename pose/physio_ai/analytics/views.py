from django.http import HttpResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView

from analytics.services import build_analytics_context, build_dashboard_context
from .models import UserProgress, Report, DailyMetrics


def _pdf_escape(text):
    return str(text).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def _simple_pdf(lines):
    text_commands = ["BT", "/F1 16 Tf", "50 790 Td"]
    first = True
    for line in lines:
        if not first:
            text_commands.append("0 -22 Td")
        text_commands.append(f"({_pdf_escape(line)}) Tj")
        first = False
    text_commands.append("ET")
    stream = "\n".join(text_commands).encode("latin-1", errors="replace")

    objects = [
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj",
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj",
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >> endobj",
        b"4 0 obj << /Length " + str(len(stream)).encode("ascii") + b" >> stream\n" + stream + b"\nendstream endobj",
        b"5 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj",
    ]

    pdf = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for obj in objects:
        offsets.append(len(pdf))
        pdf.extend(obj + b"\n")

    xref_start = len(pdf)
    pdf.extend(f"xref\n0 {len(offsets)}\n".encode("ascii"))
    pdf.extend(b"0000000000 65535 f \n")
    for offset in offsets[1:]:
        pdf.extend(f"{offset:010d} 00000 n \n".encode("ascii"))
    pdf.extend(
        (
            f"trailer << /Size {len(offsets)} /Root 1 0 R >>\n"
            f"startxref\n{xref_start}\n%%EOF"
        ).encode("ascii")
    )
    return bytes(pdf)


class AnalyticsIndexView(TemplateView):
    """Display Analytics dashboard."""
    template_name = 'analytics/index.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(build_analytics_context(self.request.user))
        return context


def export_progress_pdf(request):
    context = build_analytics_context(request.user)
    overview = context["overview"]
    lines = [
        "Physio AI Progress Report",
        f"Average score: {overview['average_score']}",
        f"Best score: {overview['best_score']}",
        f"Total sessions: {overview['total_sessions']}",
        f"Active plans: {overview['active_plans']}",
        "",
        "AI insights:",
    ]
    lines.extend(f"- {insight}" for insight in context["insights"][:6])

    response = HttpResponse(_simple_pdf(lines), content_type="application/pdf")
    response["Content-Disposition"] = 'attachment; filename="physio-ai-progress-report.pdf"'
    return response


class UserProgressView(View):
    """Display user's overall progress."""
    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, 'analytics/not_authenticated.html', status=401)
        
        try:
            progress = UserProgress.objects.get(user=request.user)
        except UserProgress.DoesNotExist:
            progress = None
        
        return render(request, 'analytics/progress.html', {'progress': progress})


class DailyMetricsView(View):
    """Display daily metrics for a user."""
    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, 'analytics/not_authenticated.html', status=401)
        
        daily_metrics = DailyMetrics.objects.filter(user=request.user).order_by('-date')[:30]
        return render(request, 'analytics/daily_metrics.html', {'daily_metrics': daily_metrics})


class ReportListView(View):
    """Display all reports for the user."""
    def get(self, request):
        if not request.user.is_authenticated:
            return render(request, 'analytics/not_authenticated.html', status=401)
        
        reports = Report.objects.filter(user=request.user).order_by('-generated_at')
        return render(request, 'analytics/report_list.html', {'reports': reports})


class ReportDetailView(View):
    """Display a specific report."""
    def get(self, request, report_id):
        try:
            report = Report.objects.get(id=report_id, user=request.user)
            return render(request, 'analytics/report_detail.html', {'report': report})
        except Report.DoesNotExist:
            return render(request, 'analytics/report_not_found.html', status=404)
