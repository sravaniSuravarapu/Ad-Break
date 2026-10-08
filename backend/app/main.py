from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.errors import AppError, RuleError
from app.routers import auth, bookings, breaks, campaigns, catalog, reports
from app.schemas.dto import HealthResponse

app = FastAPI(title="Ad Break & Campaign Booking Manager")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[item.strip() for item in settings.cors_origins.split(",") if item.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RuleError)
async def rule_error_handler(_request: object, exc: RuleError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail()})


@app.exception_handler(AppError)
async def app_error_handler(_request: object, exc: AppError) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.reason})


@app.get("/api/v1/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


app.include_router(auth.router, prefix="/api/v1")
app.include_router(catalog.router, prefix="/api/v1")
app.include_router(campaigns.router, prefix="/api/v1")
app.include_router(breaks.router, prefix="/api/v1")
app.include_router(bookings.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")
