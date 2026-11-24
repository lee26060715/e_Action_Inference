from src.realtime_utils import frame_feature_from_pose


def extract_person_features(result):
    person_features = {}

    boxes = result.boxes
    keypoints = result.keypoints

    if boxes is None or keypoints is None:
        return person_features

    if boxes.id is None:
        return person_features

    track_ids = (
        boxes.id.detach().cpu().numpy().astype(int)
    )

    person_count = min(
        len(track_ids),
        len(keypoints.xy),
    )

    for index in range(person_count):
        track_id = int(track_ids[index])

        # 한 사람의 Pose 결과만 선택
        person_result = result[index]

        # 기존 38차원 Feature 생성 함수 재사용
        feature = frame_feature_from_pose(person_result)

        person_features[track_id] = feature

    return person_features