import os

LOGGING = {  # noqa: WPS407
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
            "formatter": "standard",
            "class": "logging.StreamHandler",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": False,
        },
    },
}

AWS_REGION = os.environ.get("AWS_REGION", "eu-west-3")
AUDIO_BUCKET = os.environ.get("AUDIO_BUCKET", "transcription-audio")
TRANSCRIPTION_BUCKET = os.environ.get(
    "TRANSCRIPTION_BUCKET", "transcription-transcriptions"
)
PROCESSOR_LAMBDA = os.environ.get("PROCESSOR_LAMBDA", "transcription-processor")
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE", "transcription")
