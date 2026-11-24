from fastapi import FastAPI

from routers.predictions import router
from services.model_loader import load_models


app = FastAPI(
    title="Vision AI Action Inference",
    version="1.0.0",
)


@app.on_event("startup")
def startup():
    app.state.models = load_models()
    print("AI 모델 로딩 완료")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "model_loaded": hasattr(app.state, "models"),
    }


app.include_router(router)
