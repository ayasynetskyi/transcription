from enum import StrEnum
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, HttpUrl


class TrascriptionStatus(StrEnum):
    """Transcription job status."""

    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    FAILED = "FAILED"
    COMPLETED = "COMPLETED"


class CreateTranscriptionRequest(BaseModel):
    """Create transcription request."""

    audio_url: HttpUrl
    sentences: list[str]


class TranscriptionRequest(CreateTranscriptionRequest):
    """Internal transcription request."""

    request_id: UUID = Field(default_factory=uuid4)


class CreateTranscriptionResponse(BaseModel):
    """Create transcription request."""

    request_id: UUID | None
    message: str


class SentenceOccurrence(BaseModel):
    """Sentence occurence details."""

    plain_text: str
    was_present: bool = False
    start_word_index: int | None = None
    end_word_index: int | None = None


class TranscriptionResult(BaseModel):
    """Transcription result"""

    request_id: UUID
    status: TrascriptionStatus
    audio_url: HttpUrl | None = None
    transcription_url: HttpUrl | None = None
    sentences: list[SentenceOccurrence] = Field(default_factory=list)


class TanscriptionJobStatusChageEvent(BaseModel):
    """Transcribe Job State Change event."""

    request_id: UUID = Field(alias="TranscriptionJobName")
    status: TrascriptionStatus = Field(alias="TranscriptionJobStatus")


class EventBridgeEvent(BaseModel):
    """EventBridge event for Transcribe Job State Change."""

    detail: TanscriptionJobStatusChageEvent
