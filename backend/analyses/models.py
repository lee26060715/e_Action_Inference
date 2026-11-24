
from django.conf import settings
from django.db import models


class AnalysisJob(models.Model):

    INPUT_CHOICES = [
        ("UPLOAD", "영상 업로드"),
        ("IP_WEBCAM", "IP Webcam"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "대기 중"),
        ("STARTED", "분석 중"),
        ("SUCCESS", "완료"),
        ("FAILURE", "실패"),
    ]

    ACTION_CHOICES = [
        ("bend_return", "허리를 굽혔다 펴기"),
        ("leg_raise_lower", "다리 올렸다 내리기"),
        ("walk_turn_walk", "걷고 돌아서 걷기"),
        ("drink_return", "마시고 원위치"),
        ("sit_stand", "앉았다 일어나기"),
        ("wave", "손 흔들기"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="analysis_jobs",
    )

    title = models.CharField(
        max_length=100,
        blank=True,
    )

    memo = models.TextField(blank=True)

    input_type = models.CharField(
        max_length=20,
        choices=INPUT_CHOICES,
    )

    video = models.FileField(
        upload_to="videos/",
        blank=True,
    )

    camera_url = models.URLField(
        max_length=500,
        blank=True,
    )

    expected_action = models.CharField(
        max_length=30,
        choices=ACTION_CHOICES,
        blank=True,
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default="PENDING",
    )

    celery_task_id = models.CharField(
        max_length=255,
        blank=True,
    )

    error_message = models.TextField(blank=True)

    created_at = models.DateTimeField(
        auto_now_add=True,
    )

    completed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Job {self.id} - {self.status}"


class PersonPrediction(models.Model):

    job = models.ForeignKey(
        AnalysisJob,
        on_delete=models.CASCADE,
        related_name="predictions",
    )

    track_id = models.IntegerField()

    action_label = models.CharField(
        max_length=30,
    )

    confidence = models.FloatField()

    window_count = models.PositiveIntegerField(
        default=0,
    )

    predicted_at = models.DateTimeField(
        auto_now_add=True,
    )

    def __str__(self):
        return (
            f"Job {self.job_id} - "
            f"Track {self.track_id} - "
            f"{self.action_label}"
        )
