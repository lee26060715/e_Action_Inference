
import time
from pathlib import Path

import cv2

from django.conf import settings


def capture_camera_video(camera_url, output_path):

    # 허용된 카메라 주소인지 확인
    if not settings.IP_WEBCAM_URL:
        raise ValueError("허용된 카메라 URL이 설정되지 않았습니다.")

    if camera_url != settings.IP_WEBCAM_URL:
        raise ValueError("허용되지 않은 카메라 URL입니다.")

    duration = settings.IP_WEBCAM_CAPTURE_SECONDS

    if not 5 <= duration <= 10:
        raise ValueError("영상 수집 시간은 5~10초여야 합니다.")

    output_path = Path(output_path)

    output_path.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    cap = cv2.VideoCapture(
        camera_url,
        cv2.CAP_FFMPEG,
        [
            cv2.CAP_PROP_OPEN_TIMEOUT_MSEC, 5000,
            cv2.CAP_PROP_READ_TIMEOUT_MSEC, 5000,
        ],
    )

    frames = []
    writer = None
    success = False

    try:

        if not cap.isOpened():
            raise RuntimeError(
                "IP Webcam에 연결할 수 없습니다."
            )

        # 지정된 시간 동안 영상 프레임 수집
        start_time = time.monotonic()

        while time.monotonic() - start_time < duration:

            ret, frame = cap.read()

            if not ret:
                raise RuntimeError(
                    "카메라 영상 수신에 실패했습니다."
                )

            # 영상 크기 통일
            frame = cv2.resize(frame, (640, 360))

            frames.append(frame)

        capture_time = time.monotonic() - start_time

        if len(frames) < 10:
            raise RuntimeError(
                "수집된 영상 프레임이 부족합니다."
            )

        # 실제 수집 속도를 기준으로 FPS 계산
        fps = len(frames) / capture_time

        # MP4 영상 저장
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")

        writer = cv2.VideoWriter(
            str(output_path),
            fourcc,
            fps,
            (640, 360),
        )

        if not writer.isOpened():
            raise RuntimeError(
                "MP4 영상 파일을 생성할 수 없습니다."
            )

        for frame in frames:
            writer.write(frame)

        writer.release()
        writer = None

        if not output_path.exists():
            raise RuntimeError("영상 파일이 생성되지 않았습니다.")

        if output_path.stat().st_size == 0:
            raise RuntimeError("생성된 영상 파일이 비어 있습니다.")

        success = True

        return {
            "output_path": str(output_path),
            "frame_count": len(frames),
            "capture_time": round(capture_time, 2),
            "fps": round(fps, 2),
        }

    finally:

        cap.release()

        if writer is not None:
            writer.release()

        if not success:
            output_path.unlink(missing_ok=True)
