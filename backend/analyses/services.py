
import requests

from django.conf import settings
from django.db import transaction
from django.utils import timezone

from .models import PersonPrediction


def analyze_uploaded_video(job):

    job.status = "STARTED"
    job.error_message = ""
    job.save()

    try:
        url = f"{settings.FASTAPI_URL}/predict/video"

        # 저장된 영상 파일을 FastAPI에 전달
        with job.video.open("rb") as video_file:
            response = requests.post(
                url,
                files={
                    "file": (
                        job.video.name.split("/")[-1],
                        video_file,
                        "video/mp4",
                    )
                },
                timeout=120,
            )

        # HTTP 오류 확인
        response.raise_for_status()

        # FastAPI 응답을 Python 데이터로 변환
        result = response.json()

        # 추론 결과 및 작업 상태 저장
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
            job.save()

    except Exception as e:

        job.status = "FAILURE"
        job.error_message = str(e)
        job.completed_at = timezone.now()
        job.save()
