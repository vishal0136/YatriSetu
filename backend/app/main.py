from fastapi import FastAPI

from backend.app.api.admin import router as admin_router


app = FastAPI(
    title="YatriSetu Admin AI API",
    description="API for the YatriSetu Transit Operations Intelligence System",
    version="0.1.0",
)


app.include_router(admin_router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "YatriSetu Admin AI API",
        "version": "0.1.0",
    }

