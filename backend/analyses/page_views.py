from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count

from .models import AnalysisJob, PersonPrediction


@login_required
def index(request):
    return render(request, "analyses/index.html")


@staff_member_required
def dashboard(request):

    status_counts = dict(
        AnalysisJob.objects.values_list("status")
        .annotate(count=Count("id"))
    )

    action_counts = dict(
        PersonPrediction.objects.values_list("action_label")
        .annotate(count=Count("id"))
    )

    status_labels = [
        code for code, label in AnalysisJob.STATUS_CHOICES
    ]

    status_values = [
        status_counts.get(code, 0)
        for code in status_labels
    ]

    action_labels = [
        label for code, label in AnalysisJob.ACTION_CHOICES
    ] + ["UNKNOWN"]

    action_values = [
        action_counts.get(code, 0)
        for code, label in AnalysisJob.ACTION_CHOICES
    ] + [action_counts.get("UNKNOWN", 0)]

    context = {
        "total_jobs": AnalysisJob.objects.count(),
        "success_jobs": status_counts.get("SUCCESS", 0),
        "failure_jobs": status_counts.get("FAILURE", 0),
        "total_predictions": PersonPrediction.objects.count(),
        "unknown_count": action_counts.get("UNKNOWN", 0),

        "status_labels": status_labels,
        "status_values": status_values,
        "action_labels": action_labels,
        "action_values": action_values,
    }

    return render(
        request,
        "analyses/dashboard.html",
        context,
    )
