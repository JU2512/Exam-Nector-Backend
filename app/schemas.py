from pydantic import BaseModel
from typing import Literal, Union, List


# =======================
# YOUTUBE SUMMARY SCHEMA
# =======================

class SummaryRequest(BaseModel):
    youtube_url: str
    depth: Literal["easy", "medium", "long"]


class SummaryResponse(BaseModel):
    summary: str


# =======================
# DOCUMENT SUMMARY SCHEMA
# =======================

class DocumentSummaryResponse(BaseModel):
    summary: str
    filename: str


# =======================
# WHISPER TRANSCRIPTION SCHEMAS
# =======================

class WhisperResponse(BaseModel):
    text: str


class YouTubeTranscriptRequest(BaseModel):
    youtube_url: str


class YouTubeTranscriptResponse(BaseModel):
    youtube_url: str
    transcript: str


# =======================
# YOUTUBE SUMMARY RESPONSE (FIXED)
# =======================

class YouTubeSummaryResponse(BaseModel):
    youtube_url: str
    summary: Union[List[str], str]
