
from django.contrib import admin
from .models import AnalysisJob, PersonPrediction


@admin.register(AnalysisJob)
class AnalysisJobAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "title",
        "input_type",
        "status",
        "created_at",
        "completed_at",
    )

    list_filter = (
        "input_type",
        "status",
        "created_at",
    )

    search_fields = (
        "user__username",
        "title",
    )

    ordering = ("-created_at",)


@admin.register(PersonPrediction)
class PersonPredictionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "job",
        "track_id",
        "action_label",
        "confidence",
        "window_count",
        "predicted_at",
    )

    list_filter = (
        "action_label",
        "predicted_at",
    )

    search_fields = (
        "job__title",
        "job__user__username",
    )

    ordering = ("-predicted_at",)
