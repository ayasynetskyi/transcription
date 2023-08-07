import logging
from pathlib import Path
from typing import TYPE_CHECKING
from urllib.parse import unquote
from uuid import UUID

import boto3

from transcription import settings, utils
from transcription.models import (
    CreateTranscriptionRequest,
    CreateTranscriptionResponse,
    TranscriptionRequest,
    TranscriptionResult,
    TrascriptionStatus,
    SentenceOccurrence,
)
from transcription.utils import check_url_exsits

if TYPE_CHECKING:
    from mypy_boto3_dynamodb.service_resource import Table

logger = logging.getLogger(__name__)


class DoesNotExist(Exception):
    """Entity does not exist, error on API request."""


def create_transcription_job(
    transcription_request: CreateTranscriptionRequest,
) -> CreateTranscriptionResponse:
    """"""
    if not check_url_exsits(str(transcription_request.audio_url)):
        raise ValueError("Audio URL does not exsit")

    transcription_request = TranscriptionRequest(**transcription_request.model_dump())

    lambda_client = boto3.client("lambda")
    response = lambda_client.invoke(
        FunctionName=settings.PROCESSOR_LAMBDA,
        InvocationType="Event",
        Payload=transcription_request.model_dump_json().encode(),
    )
    logger.info("Invoke result: %s", response)

    item = TranscriptionResult(
        request_id=transcription_request.request_id,
        status=TrascriptionStatus.QUEUED,
        audio_url=transcription_request.audio_url,
        sentences=[
            SentenceOccurrence(plain_text=sentence)
            for sentence in transcription_request.sentences
        ],
    ).model_dump(mode="json")
    table = boto3.resource("dynamodb").Table(settings.DYNAMODB_TABLE)
    table.put_item(Item=item)

    return CreateTranscriptionResponse(
        request_id=transcription_request.request_id,
        message="Your request was accepted successfully",
    )


def get_transcription_result(request_id: UUID) -> TranscriptionResult:
    table = boto3.resource("dynamodb").Table(settings.DYNAMODB_TABLE)
    return get_transcription_result_from_dynamodb(request_id, table)


def get_transcription_result_from_dynamodb(
    request_id: UUID,
    table: 'Table',
) -> TranscriptionResult:
    result = table.get_item(Key={"request_id": str(request_id)})
    if "Item" not in result:
        raise DoesNotExist()
    return TranscriptionResult(**result["Item"])


def start_transcription_job(transcription_request: TranscriptionRequest, table: 'Table'):
    audio_filename = ""
    if url_path := transcription_request.audio_url.path:
        audio_filename = Path(unquote(url_path)).name

    audio_key = f"{transcription_request.request_id.hex}_{audio_filename}"

    utils.upload_url_to_s3(
        url=str(transcription_request.audio_url),
        bucket_name=settings.AUDIO_BUCKET,
        key=audio_key,
    )

    transcribe_client = boto3.client("transcribe", region_name=settings.AWS_REGION)

    transcribe_client.start_transcription_job(
        TranscriptionJobName=transcription_request.request_id.hex,
        Media={"MediaFileUri": f"s3://{settings.AUDIO_BUCKET}/{audio_key}"},
        LanguageCode="en-US",
        OutputBucketName=settings.TRANSCRIPTION_BUCKET,
    )

    update_transcription_status_in_dynamodb(
        request_id=transcription_request.request_id,
        status=TrascriptionStatus.IN_PROGRESS,
        table=table,
    )


def update_transcription_status_in_dynamodb(
    request_id: UUID,
    status: TrascriptionStatus,
    table: 'Table',
):
    table.update_item(
        Key={
            "request_id": str(request_id),
        },
        AttributeUpdates={
            "status": {
                "Value": status.value,
                "Action": "PUT",
            },
        },
    )


def transcription_job_completed(request_id: UUID, table: 'Table'):
    transcribe_client = boto3.client("transcribe", region_name=settings.AWS_REGION)
    job = transcribe_client.get_transcription_job(TranscriptionJobName=request_id.hex)

    logger.info(job)
    transcription_uri = job["TranscriptionJob"]["Transcript"]["TranscriptFileUri"]
    transcription = utils.read_json_from_s3(transcription_uri)
    transcription_text = transcription["results"]["transcripts"][0][
        "transcript"
    ].lower()

    db_record = get_transcription_result_from_dynamodb(request_id, table)

    update_record = TranscriptionResult(
        request_id=request_id,
        status=TrascriptionStatus.COMPLETED,
        audio_url=db_record.audio_url,
        transcription_url=transcription_uri,
        sentences=[
            find_occurence(transcription_text, sentence.plain_text)
            for sentence in db_record.sentences
        ],
    ).model_dump(mode="json")
    table.put_item(Item=update_record)


def find_occurence(text: str, sentence: str) -> SentenceOccurrence:
    index = text.find(sentence.lower())
    if index == -1:
        return SentenceOccurrence(plain_text=sentence)
    return SentenceOccurrence(
        plain_text=sentence,
        was_present=True,
        start_word_index=index,
        end_word_index=index + len(sentence),
    )
