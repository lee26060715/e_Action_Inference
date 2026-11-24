
import cv2

from src.common import load_config, resolve_device
from src.multi_person_utils import extract_person_features


def iter_video_features(video_path, pose_model):
    config = load_config()
    device = resolve_device(config["device"])

    # 1. 영상 열기
    capture = cv2.VideoCapture(str(video_path))

    try:
        if not capture.isOpened():
            raise RuntimeError("영상을 열 수 없습니다.")

        # 2. 영상 FPS 확인
        fps = float(capture.get(cv2.CAP_PROP_FPS))

        if fps <= 0:
            fps = 30.0

        # 이전 영상의 Tracking 상태 초기화
        if pose_model.predictor is not None:
            for tracker in getattr(
                pose_model.predictor, "trackers", []
            ):
                tracker.reset()

        frame_id = 0

        # 3. 영상 프레임 반복 처리
        while True:
            success, frame = capture.read()

            if not success:
                break

            video_time = frame_id / fps

            # 4. YOLO Pose + ByteTrack
            result = pose_model.track(
                source=frame,
                persist=True,
                tracker="bytetrack.yaml",
                imgsz=int(config["image_size"]),
                conf=float(config["person_confidence"]),
                device=device,
                verbose=False,
            )[0]

            # 5. Track ID별 Feature 추출
            person_features = extract_person_features(result)

            # 6. 현재 프레임의 처리 결과 전달
            yield video_time, person_features

            frame_id += 1

        if frame_id == 0:
            raise RuntimeError("처리한 프레임이 없습니다.")

    finally:
        capture.release()
