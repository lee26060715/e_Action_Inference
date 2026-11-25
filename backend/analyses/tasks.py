from celery import shared_task

from .models import AnalysisJob
from .services import (
    analyze_uploaded_video,
    analyze_camera_video,
    mark_failed,
)


@shared_task
def analyze_job(job_id):

    job = AnalysisJob.objects.get(id=job_id)

    if job.input_type == "UPLOAD":

        analyze_uploaded_video(job)

    elif job.input_type == "IP_WEBCAM":

        analyze_camera_video(job)

    else:

        mark_failed(
            job,
            "지원하지 않는 입력 방식입니다.",
        )

    return {
        "job_id": job.id,
        "status": job.status,
    }