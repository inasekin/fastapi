from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse

from app.database import Base, engine
from app.routers import auth, tasks


@asynccontextmanager
async def lifespan(_app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


API_DESCRIPTION = """
REST API задач с JWT. После регистрации получите токен через **POST /api/auth/token**
(form: `username`, `password`), затем передайте заголовок `Authorization: Bearer <token>`
"""

app = FastAPI(
    title="Task Manager API",
    description=API_DESCRIPTION,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8080",
        "http://localhost:8080",
        "http://127.0.0.1:3000",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api")
app.include_router(tasks.router, prefix="/api")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/swagger", include_in_schema=False)
def swagger_redirect() -> RedirectResponse:
    return RedirectResponse(url="/docs", status_code=307)
