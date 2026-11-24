
import json
import sys

from services.model_loader import load_models
from services.action_inference import analyze_video


if __name__ == "__main__":
    video_path = sys.argv[1]

    rf_model, feature_columns, training_info, pose_model = (
        load_models()
    )

    result = analyze_video(
        video_path,
        rf_model,
        feature_columns,
        training_info,
        pose_model,
    )

    print(
        json.dumps(
            result,
            ensure_ascii=False,
            indent=2,
        )
    )
