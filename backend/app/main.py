from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from pathlib import Path
import traceback

from app.config import get_settings
from app.api import auth, videos, analysis
from app.core.database import engine, Base

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="Reride - 스노우보드 AI 분석 & 캐릭터화 서비스 API",
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions and log them."""
    print(f"\n{'='*80}")
    print(f"GLOBAL EXCEPTION HANDLER CAUGHT ERROR:")
    print(f"Request: {request.method} {request.url}")
    print(f"Error Type: {type(exc).__name__}")
    print(f"Error Message: {str(exc)}")
    print(f"Traceback:")
    traceback.print_exc()
    print(f"{'='*80}\n")

    return JSONResponse(
        status_code=500,
        content={"detail": f"{type(exc).__name__}: {str(exc)}"}
    )


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # TODO: 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"{settings.api_prefix}/auth", tags=["auth"])
app.include_router(videos.router, prefix=f"{settings.api_prefix}/videos", tags=["videos"])
app.include_router(analysis.router, prefix=f"{settings.api_prefix}/analysis", tags=["analysis"])

# Mount static files for local uploads/outputs
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)
outputs_dir = Path("outputs")
outputs_dir.mkdir(exist_ok=True)
app.mount("/static/uploads", StaticFiles(directory="uploads"), name="uploads")
app.mount("/static/outputs", StaticFiles(directory="outputs"), name="outputs")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/health")
async def health_check():
    return {"status": "ok", "service": settings.app_name}
