# Transcription And Trackers API

### Overview

Design and develop an asynchronous API that receives a request containing a URL for
an audio file and a list of sentences. The API would transcribe the audio file and verify
whether the given sentences were said in the audio or not.
The API results should be written as a DB record.

### Request Example
```
{
    "audio_url":"url/for/file.wav,
    "sentences": ["hi my name is joe", "can you hear me?"]
}
```
### Response Body

```
{
    "body": {
        "request_id": "generated_request_id",
        "message": "Your request was accepted successfully"
    }
}
```
### Results Example
```
{
    "id":"record_id",
    "request_id":"generated_request_id",
    "audio_url": "the_audio_url",
    (optional) "transcription_url": "transcription_url",
    "sentences": [
        {
            "plain_text:"the_sentences_as_a_plain_text",
            "was_present": true,
            "start_word_index": 7,
            "end_word_index": 13
        },
        {
            "plain_text:"the_sentences_as_a_plain_text",
            "was_present": false,
            "start_word_index": null,
            "end_word_index": null
        }
    ]
}
```
