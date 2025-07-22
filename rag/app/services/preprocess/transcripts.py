import json
import pysrt
from rag.app.schemas.data import Chunk, TypeOfFormat
import logging
from rag.app.services.preprocess.constants import CHUNKING_SIZE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def build_chunk(subs, word_count, name_space) -> Chunk:
    """
    Builds a Chunk object from a list of subtitle segments.

    :param subs: List of subtitle objects (pysrt.SubRipItem).
    :param word_count: Total number of words in the combined text.
    :param name_space: The name of the file or namespace for this chunk.
    :return: Chunk object.
    """
    start = subs[0].start
    end = subs[-1].end
    chunk_text = " ".join(s.text.replace("\n", " ") for s in subs)

    chunk = Chunk(
        time_start=str(start),
        time_end=str(end),
        text=chunk_text,
        chunk_size=word_count,
        name_space=name_space,
    )
    return chunk


def chunk_srt(content: tuple[str, str]) -> list[Chunk]:
    file_name, text = content
    logger.debug(f"Chunking SRT file: {file_name}")
    subs = pysrt.from_string(text)
    logger.debug(f"Parsed {len(subs)} subtitle segments from {file_name}")

    chunks = []
    current_chunk = []
    word_count = 0

    for sub in subs:
        words = sub.text.replace("\n", " ").split()
        current_chunk.append(sub)
        word_count += len(words)

        if word_count >= CHUNKING_SIZE:
            chunk = build_chunk(current_chunk, word_count, file_name)
            chunks.append(chunk)
            current_chunk = []
            word_count = 0

    if current_chunk:
        chunk = build_chunk(current_chunk, word_count, file_name)
        chunks.append(chunk)

    logger.debug(f"Created {len(chunks)} chunks from {file_name}")
    return chunks


def chunk_txt(content: tuple[str, str]) -> list[Chunk]:
    """
    Splits plain text into word-based chunks without timing metadata.

    :param content: A tuple containing (filename, raw text content).
    :return: A list of Chunk objects, each with text data, chunk size, and file-level metadata.
    """
    file_name, text = content
    logger.debug(f"Chunking TXT file: {file_name}")
    words = text.split()
    logger.debug(f"Found {len(words)} words in {file_name}")

    chunks: list[Chunk] = []

    for i in range(0, len(words), CHUNKING_SIZE):
        chunk_words = words[i : i + CHUNKING_SIZE]
        chunk_text = " ".join(chunk_words)

        chunk = Chunk(
            name_space=file_name,
            text=chunk_text,
            chunk_size=len(chunk_words),
            time_start=None,
            time_end=None,
        )
        chunks.append(chunk)

    logger.debug(f"Created {len(chunks)} chunks from {file_name}")
    return chunks


def preprocess_raw_transcripts(
    raw_transcripts: list[tuple[str, str]], data_format: TypeOfFormat = TypeOfFormat.SRT
) -> list[Chunk]:
    """
    Processes raw transcripts by applying preprocessing steps, including:

    1. Chunking data into fixed-size word batches
    2. Adding metadata to each chunk

    :param raw_transcripts: List of (filename, content) tuples
    :param data_format: Format of the data (e.g., SRT or TXT)
    :return: List of Chunk objects
    """
    if data_format is None:
        raise RuntimeError(f"Unknown data_format")
    logger.info(
        f"Starting preprocessing of {len(raw_transcripts)} transcripts with format: {data_format.name}"
    )
    cleaned_transcripts: list[Chunk] = []

    for i, raw_transcript in enumerate(raw_transcripts, 1):
        file_name = raw_transcript[0]
        logger.info(f"Processing transcript {i}/{len(raw_transcripts)}: {file_name}")

        if data_format.value == TypeOfFormat.SRT.value:
            chunks = chunk_srt(raw_transcript)
        elif data_format.value == TypeOfFormat.TXT.value:
            chunks = chunk_txt(raw_transcript)
        else:
            logger.error(f"Unsupported format: {data_format}")
            raise ValueError(f"Unsupported format: {data_format}")

        cleaned_transcripts.extend(chunks)
        logger.info(f"Completed processing {file_name}: {len(chunks)} chunks")

    logger.info(
        f"Preprocessing completed. Total chunks created: {len(cleaned_transcripts)}"
    )
    return cleaned_transcripts


def translate_chunks(chunks: list[Chunk]) -> list[tuple[str, Chunk]]:
    logger.info(f"Starting translation of {len(chunks)} chunks")

    try:
        with open(
            "/Users/dothanbardichev/Desktop/RAV/RavProject/embed/data_embedder/data/translations/assigned.json",
            "r",
        ) as f:
            translations = json.load(f)
        logger.debug(f"Loaded {len(translations)} translation mappings")
    except Exception as e:
        logger.error(f"Failed to load translation file: {str(e)}")
        raise

    result: list[tuple[str, Chunk]] = []
    for i, chunk in enumerate(chunks, 1):
        if i % 100 == 0:
            logger.debug(f"Translated {i}/{len(chunks)} chunks")

        words = chunk.text.lower().split()
        translated_words = [translations.get(word, word) for word in words]
        mapped_text = " ".join(translated_words)
        result.append((mapped_text, chunk))

    logger.info(f"Translation completed for {len(result)} chunks")
    return result
