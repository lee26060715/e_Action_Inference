from rest_framework import serializers
from .models import AnalysisJob, PersonPrediction


class PersonPredictionSerializer(serializers.ModelSerializer):

    class Meta:
        model = PersonPrediction
        fields = (
            "id",
            "track_id",
            "action_label",
            "confidence",
            "window_count",
            "predicted_at",
        )
        read_only_fields = fields


class AnalysisJobSerializer(serializers.ModelSerializer):

    predictions = PersonPredictionSerializer(
        many=True,
        read_only=True,
    )

    class Meta:
        model = AnalysisJob
        fields = (
            "id",
            "user",
            "title",
            "memo",
            "input_type",
            "video",
            "camera_url",
            "expected_action",
            "status",
            "celery_task_id",
            "error_message",
            "created_at",
            "completed_at",
            "predictions",
        )

        read_only_fields = (
            "id",
            "user",
            "status",
            "celery_task_id",
            "error_message",
            "created_at",
            "completed_at",
            "predictions",
        )

    def validate(self, attrs):
        if self.instance is not None:
            allowed_fields = {"title", "memo"}

            if set(attrs) - allowed_fields:
                raise serializers.ValidationError(
                    "제목과 메모만 수정할 수 있습니다."
                )

            return attrs

        input_type = attrs.get("input_type")
        video = attrs.get("video")
        camera_url = attrs.get("camera_url")

        if input_type == "UPLOAD":
            if not video:
                raise serializers.ValidationError(
                    "영상 파일을 업로드해주세요."
                )

            if not video.name.lower().endswith(".mp4"):
                raise serializers.ValidationError(
                    "MP4 영상만 업로드할 수 있습니다."
                )

            if camera_url:
                raise serializers.ValidationError(
                    "영상 업로드 시 카메라 URL은 입력하지 않습니다."
                )

        elif input_type == "IP_WEBCAM":
            if not camera_url:
                raise serializers.ValidationError(
                    "카메라 URL을 입력해주세요."
                )

            if video:
                raise serializers.ValidationError(
                    "IP Webcam 사용 시 영상 파일은 입력하지 않습니다."
                )

        return attrs