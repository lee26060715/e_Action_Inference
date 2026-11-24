from celery import shared_task

from .models import AnalysisJob
from .services import analyze_uploaded_video


@shared_task
def analyze_job(job_id):

    job = AnalysisJob.objects.get(id=job_id)

    analyze_uploaded_video(job)

    return {
        "job_id": job.id,
        "status": job.status,
    }