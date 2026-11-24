
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import AnalysisJob
from .serializers import AnalysisJobSerializer
from .services import analyze_uploaded_video


class AnalysisJobViewSet(viewsets.ModelViewSet):

    serializer_class = AnalysisJobSerializer
    permission_classes = [IsAuthenticated]

    http_method_names = [
        "get",
        "post",
        "patch",
        "delete",
        "head",
        "options",
    ]

    def get_queryset(self):
        return AnalysisJob.objects.filter(
            user=self.request.user
        ).order_by("-created_at")

    def perform_create(self, serializer):

        job = serializer.save(
            user=self.request.user
        )

        if job.input_type == "UPLOAD":
            analyze_uploaded_video(job)

    @action(detail=True, methods=["get"])
    def status(self, request, pk=None):
        job = self.get_object()

        return Response({
            "id": job.id,
            "status": job.status,
            "error_message": job.error_message,
            "completed_at": job.completed_at,
            "predictions": self.get_serializer(
                job
            ).data["predictions"],
        })
