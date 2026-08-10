import sys
import uvicorn
from pathlib import Path


def configure_import_path() -> Path:

    backend_dir = Path(__file__).resolve().parents[1]
    if str(backend_dir) not in sys.path:
        sys.path.insert(0, str(backend_dir))
    return backend_dir


BACKEND_DIR = configure_import_path()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.calculations import router as calculations_router
from app.api.routes.auth import router as auth_router
from app.api.routes.users import router as users_router
from app.core.config import get_settings
from app.database import Base, engine
from app.persistence.migrations import migrate_legacy_user_ids, migrate_user_email_column

settings = get_settings()
Base.metadata.create_all(bind=engine)
migrate_user_email_column()
migrate_legacy_user_ids()

app = FastAPI(title=settings.app_name, version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(calculations_router, prefix="/api/v1")
app.include_router(auth_router, prefix="/api/v1")
app.include_router(users_router, prefix="/api/v1")


@app.get("/health", tags=["system"])
def health_check():
    return {"status": "ok"}

def run_development_server() -> None:
    import os
    from subprocess import Popen

    frontend_dir = BACKEND_DIR.parent / "frontend"
    os.chdir(frontend_dir)
    Popen(["npm", "run", "dev"], shell=True)

    os.chdir(BACKEND_DIR)
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8082,
        reload=True,
        app_dir=str(BACKEND_DIR),
    )

if __name__ == "__main__":
    run_development_server()
