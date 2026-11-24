import tempfile
from pathlib import Path
from threading import Lock

from fastapi import (
    APIRouter,
    UploadFile,
    File,
    HTTPException,
    Request,
)

from services.action_inference import analyze_video


router = APIRouter()
inference_lock = Lock()


@router.post("/predict/video")
def predict_video(
    request: Request,
    file: UploadFile = File(...),
):
    # 1. 파일 형식 확인
    if not file.filename or not file.filename.lower().endswith(".mp4"):
        raise HTTPException(
            status_code=400,
            detail="MP4 영상만 업로드할 수 있습니다.",
        )

    temp_path = None

    try:
        # 2. 업로드 영상을 임시 파일로 저장
        with tempfile.NamedTemporaryFile(
            suffix=".mp4",
            delete=False,
        ) as temp_file:
            temp_path = Path(temp_file.name)
            temp_file.write(file.file.read())

        # 3. 서버에 로딩된 모델 가져오기
        models = request.app.state.models

        # 4. 기존 영상 추론 함수 실행
        with inference_lock:
            result = analyze_video(
                temp_path,
                *models,
            )

        # 5. 결과 반환
        if not result["predictions"]:
            result["message"] = "추적된 사람이 없습니다."

        return result

    except RuntimeError as e:
        raise HTTPException(
            status_code=422,
            detail=str(e),
        )

    finally:
        # 6. 추론이 끝난 임시 영상 삭제
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

        file.file.close()
