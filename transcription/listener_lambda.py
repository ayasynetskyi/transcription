import logging
from logging import config as logging_config

import boto3
from pydantic import validate_call

from transcription import settings, usecases
from transcription.models import EventBridgeEvent, TrascriptionStatus

logger = logging.getLogger(__name__)


@validate_call
def handler(event: EventBridgeEvent, context) -> None:
    logging_config.dictConfig(settings.LOGGING)
    logger.info(event)
    table = boto3.resource("dynamodb").Table(settings.DYNAMODB_TABLE)

    if event.detail.status != TrascriptionStatus.FAILED:
        usecases.transcription_job_completed(event.detail.request_id, table)
    else:
        usecases.update_transcription_status_in_dynamodb(
            request_id=event.detail.request_id,
            status=event.detail.status,
            table=table,
        )
