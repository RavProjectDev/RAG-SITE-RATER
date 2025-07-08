import pytest
from rag.app.services.preprocess.transcripts import preprocess_raw_transcripts
from rag.app.schemas.data import TypeOfFormat, Chunk


def test_preprocess_raw_transcripts_srt(monkeypatch):
    # Patch chunk_srt to avoid pysrt dependency
    monkeypatch.setattr(
        "rag.app.services.preprocess.transcripts.chunk_srt",
        lambda content: [Chunk(text="abc", chunk_size=3, name_space=content[0])],
    )
    raw = [("file.srt", "dummy srt content")]
    chunks = preprocess_raw_transcripts(raw, TypeOfFormat.SRT)
    assert len(chunks) == 1
    assert chunks[0].name_space == "file.srt"


def test_preprocess_raw_transcripts_txt(monkeypatch):
    monkeypatch.setattr(
        "rag.app.services.preprocess.transcripts.chunk_txt",
        lambda content: [Chunk(text="abc", chunk_size=3, name_space=content[0])],
    )
    raw = [("file.txt", "dummy txt content")]
    chunks = preprocess_raw_transcripts(raw, TypeOfFormat.TXT)
    assert len(chunks) == 1
    assert chunks[0].name_space == "file.txt"


def test_preprocess_raw_transcripts_invalid_format():
    with pytest.raises(RuntimeError):
        preprocess_raw_transcripts([("file.xyz", "content")], None)
