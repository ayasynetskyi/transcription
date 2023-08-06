import logging
from logging import config as logging_config

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from mangum import Mangum
from starlette import status

from transcription import settings
from transcription.api import transcription
from transcription.usecases import DoesNotExist

logging_config.dictConfig(settings.LOGGING)

ROOT = "/api/v1"

app = FastAPI(root_path=ROOT)

app.include_router(
    transcription.router,
    prefix="/transcription",
)

logger = logging.getLogger(__name__)


@app.exception_handler(ValueError)
async def value_error_exception_handler(request: Request, exc: ValueError):
    """Readable response for ValidationError."""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"message": str(exc)},
    )


@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    """Readable response for generic Exception."""
    logger.exception(exc)
    return JSONResponse(
        {
            "message": "Internal server error",
        },
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@app.exception_handler(DoesNotExist)
async def recipe_does_not_exist_handler(request: Request, exc: DoesNotExist):
    """Readable response for DoesNotExist class of exciptions."""
    return JSONResponse(
        {
            "message": str(exc),
        },
        status_code=status.HTTP_404_NOT_FOUND,
    )


root_app = FastAPI()
root_app.mount(ROOT, app)
handler = Mangum(root_app)
