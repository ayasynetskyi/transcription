import logging
from uuid import UUID

from fastapi import APIRouter
from starlette import status

from transcription import usecases
from transcription.models import (
    CreateTranscriptionRequest,
    CreateTranscriptionResponse,
    TranscriptionResult,
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=CreateTranscriptionResponse
)
def create_transcription_job(
    transcription_request: CreateTranscriptionRequest,
) -> CreateTranscriptionResponse:
    return usecases.create_transcription_job(transcription_request)


@router.get("/{request_id}", response_model=TranscriptionResult)
def get_transcription_result(
    request_id: UUID,
) -> TranscriptionResult:
    return usecases.get_transcription_result(request_id)
