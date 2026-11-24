import json
import time
from pathlib import Path

from src.realtime_utils import (
    TimedFeatureBuffer,
    predict_from_window,
    validate_runtime_values,
)
from src.sequence_utils import sequence_feature_names
from services.pose_pipeline import iter_video_features


BASE_DIR = Path(__file__).resolve().parent.parent


def analyze_video(
    video_path,
    rf_model,
    feature_columns,
    training_info,
    pose_model,
):
    start_time = time.perf_counter()

    # 1. 기존 실시간 추론 설정 불러오기
    with open(
        BASE_DIR / "day07_realtime.json",
        encoding="utf-8",
    ) as f:
        config = json.load(f)

    sequence_steps = int(training_info["sequence_steps"])

    validate_runtime_values(
        window_seconds=config["window_seconds"],
        confidence_threshold=config["confidence_threshold"],
        stabilization_buffer=config["stabilization_buffer"],
        stabilization_min_votes=config["stabilization_min_votes"],
    )

    # 2. 학습 당시 Feature 순서 검증
    if sequence_feature_names(sequence_steps) != feature_columns:
        raise ValueError("Feature 순서가 일치하지 않습니다.")

    # 3. 사람별 Buffer 및 결과 저장 공간
    buffers = {}
    last_prediction_times = {}
    prediction_history = {}

    # 4. 영상의 프레임별 Feature 처리
    for video_time, person_features in iter_video_features(
        video_path,
        pose_model,
    ):
        # 새로 등장한 사람의 Buffer 생성
        for track_id in person_features:
            if track_id not in buffers:
                buffers[track_id] = TimedFeatureBuffer(
                    config["window_seconds"]
                )

                last_prediction_times[track_id] = -1e9
                prediction_history[track_id] = []

        # 사람마다 독립적으로 Feature 저장
        for track_id, buffer in buffers.items():
            feature = person_features.get(track_id)

            buffer.append(video_time, feature)

            # 현재 프레임에 없는 사람은 예측하지 않음
            if track_id not in person_features:
                continue

            # 5. Window 준비 여부 확인
            ready = buffer.is_ready(
                min_window_fill_ratio=config[
                    "min_window_fill_ratio"
                ],
                min_valid_feature_ratio=config[
                    "min_valid_feature_ratio"
                ],
                min_valid_features=config[
                    "min_valid_features"
                ],
            )

            if not ready:
                continue

            # 6. 예측 실행 간격 확인
            elapsed = (
                video_time
                - last_prediction_times[track_id]
            )

            if elapsed < config["prediction_interval_sec"]:
                continue

            # 7. 기존 Random Forest 추론 함수 재사용
            label, raw_label, confidence, probabilities = (
                predict_from_window(
                    model=rf_model,
                    feature_buffer=buffer,
                    sequence_steps=sequence_steps,
                    confidence_threshold=config[
                        "confidence_threshold"
                    ],
                )
            )

            prediction_history[track_id].append({
                "action_label": label,
                "confidence": float(confidence),
            })

            last_prediction_times[track_id] = video_time

    # 8. 사람별 대표 예측 결과 생성
    predictions = []

    for track_id, history in prediction_history.items():
        if not history:
            predictions.append({
                "track_id": track_id,
                "action_label": "UNKNOWN",
                "confidence": 0.0,
                "window_count": 0,
            })
            continue

        best = max(
            history,
            key=lambda item: item["confidence"],
        )

        predictions.append({
            "track_id": track_id,
            "action_label": best["action_label"],
            "confidence": best["confidence"],
            "window_count": len(history),
        })

    # 9. 최종 결과 반환
    return {
        "predictions": predictions,
        "processing_time": round(
            time.perf_counter() - start_time,
            3,
        ),
    }
