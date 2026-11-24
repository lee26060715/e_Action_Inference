import json
from pathlib import Path

import joblib
from ultralytics import YOLO


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_DIR = BASE_DIR / "models"


def load_models():
    # 1. Random Forest 모델 불러오기
    rf_model = joblib.load(
        MODEL_DIR / "rf_action_baseline.joblib"
    )

    # 2. Feature 이름 및 순서 불러오기
    with open(
        MODEL_DIR / "rf_feature_columns.json",
        encoding="utf-8"
    ) as f:
        feature_columns = json.load(f)

    # 3. 모델 학습 정보 불러오기
    with open(
        MODEL_DIR / "rf_training_info.json",
        encoding="utf-8"
    ) as f:
        training_info = json.load(f)

    # 4. 모델 입력 규격 확인
    if len(rf_model.classes_) != 6:
        raise ValueError("동작 클래스 수가 일치하지 않습니다.")

    if rf_model.n_features_in_ != 1140:
        raise ValueError("모델 Feature 수가 일치하지 않습니다.")

    if len(feature_columns) != 1140:
        raise ValueError("Feature 목록의 길이가 일치하지 않습니다.")

    # 5. YOLO Pose 모델 불러오기
    pose_model = YOLO(
        str(MODEL_DIR / "yolo11n-pose.pt")
    )

    return rf_model, feature_columns, training_info, pose_model


if __name__ == "__main__":
    rf_model, feature_columns, training_info, pose_model = load_models()

    print("모델 로딩 성공")
    print("Classes:", rf_model.classes_)
    print("Class count:", len(rf_model.classes_))
    print("Model feature count:", rf_model.n_features_in_)
    print("Feature columns:", len(feature_columns))
    print("Sequence steps:", training_info["sequence_steps"])
    print("YOLO Pose loading: OK")
