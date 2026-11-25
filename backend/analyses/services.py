import tempfile
from pathlib import Path

import requests

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import PersonPrediction
from .camera_capture import capture_camera_video


# 작업 시작 상태 저장
def mark_started(job):

    job.status = "STARTED"
    job.error_message = ""
    job.save(update_fields=["status", "error_message"])


# FastAPI 영상 추론 요청
def request_video_prediction(video_file, filename):

    url = f"{settings.FASTAPI_URL}/predict/video"

    response = requests.post(
        url,
        files={
            "file": (
                filename,
                video_file,
                "video/mp4",
            )
        },
        timeout=120,
    )

    response.raise_for_status()

    return response.json()


# 추론 결과 및 성공 상태 저장
def save_predictions(job, result):

    with transaction.atomic():

        for prediction in result["predictions"]:

            PersonPrediction.objects.create(
                job=job,
                track_id=prediction["track_id"],
                action_label=prediction["action_label"],
                confidence=prediction["confidence"],
                window_count=prediction["window_count"],
            )

        job.status = "SUCCESS"
        job.completed_at = timezone.now()

        job.save(
            update_fields=["status", "completed_at"]
        )


# 실패 상태 저장
def mark_failed(job, error):

    job.status = "FAILURE"
    job.error_message = str(error)
    job.completed_at = timezone.now()

    job.save(
        update_fields=[
            "status",
            "error_message",
            "completed_at",
        ]
    )


# 업로드 영상 분석
def analyze_uploaded_video(job):

    mark_started(job)

    try:

        with job.video.open("rb") as video_file:

            result = request_video_prediction(
                video_file,
                Path(job.video.name).name,
            )

        save_predictions(job, result)

    except Exception as e:

        mark_failed(job, e)


# IP Webcam 영상 분석
def analyze_camera_video(job):

    mark_started(job)

    try:

        with tempfile.TemporaryDirectory() as temp_dir:

            output_path = Path(temp_dir) / f"camera_{job.id}.mp4"

            capture_result = capture_camera_video(
                job.camera_url,
                output_path,
            )

            print(
                f"Job {job.id} camera capture: "
                f"{capture_result['capture_time']} seconds, "
                f"{capture_result['frame_count']} frames",
                flush=True,
            )

            with output_path.open("rb") as video_file:

                result = request_video_prediction(
                    video_file,
                    output_path.name,
                )

            print(
                f"Job {job.id} inference time: "
                f"{result.get('processing_time')} seconds",
                flush=True,
            )

            save_predictions(job, result)

    except Exception as e:

        mark_failed(job, e)
