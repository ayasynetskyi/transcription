import logging
from logging import config as logging_config

import boto3
from pydantic import validate_call

from transcription import settings, usecases
from transcription.models import TranscriptionRequest

logger = logging.getLogger(__name__)


@validate_call
def handler(transcription_request: TranscriptionRequest, context) -> None:
    logging_config.dictConfig(settings.LOGGING)

    table = boto3.resource("dynamodb").Table(settings.DYNAMODB_TABLE)
    usecases.start_transption_job(transcription_request, table)
