import json
import pysrt
import uuid
from shared.classes import Chunk
from shared.constants import CHUNKING_SIZE
from shared.enums import TypeOfFormat
from logging import getLogger
logger = getLogger(__name__)

def build_chunk(subs, word_count, full_srt_text, search_start,name_space) -> tuple[Chunk, int]:
    """
    Builds a Chunk object from a list of subtitle segments.

    :param subs: List of subtitle objects (pysrt.SubRipItem).
    :param word_count: Total number of words in the combined text.
    :param full_srt_text: Original SRT file content as string.
    :param search_start: Starting index to search from in full_srt_text.
    :return: (Chunk object, updated search index).
    """
    start = subs[0].start
    end = subs[-1].end
    chunk_text = " ".join(s.text.replace('\n', ' ') for s in subs)

    char_start = full_srt_text.find(chunk_text, search_start)
    char_end = char_start + len(chunk_text)

    chunk = Chunk(
        id = uuid.uuid4(),
        time_start = str(start),
        time_end = str(end),
        text=chunk_text,
        chunk_size=word_count,
        char_start=char_start,
        char_end=char_end,
        name_space=name_space,
    )
    return chunk, char_end


def chunk_srt(content: tuple[str,str]) -> list[Chunk]:
    file_name, text = content
    logger.debug(f"Chunking SRT file: {file_name}")
    subs = pysrt.from_string(text)
    logger.debug(f"Parsed {len(subs)} subtitle segments from {file_name}")
    
    chunks = []
    current_chunk = []
    word_count = 0
    search_index = 0

    for sub in subs:
        words = sub.text.replace('\n', ' ').split()
        current_chunk.append(sub)
        word_count += len(words)

        if word_count >= CHUNKING_SIZE:
            chunk, search_index = build_chunk(current_chunk, word_count, text, search_index,file_name)
            chunks.append(chunk)
            current_chunk = []
            word_count = 0

    if current_chunk:
        chunk, _ = build_chunk(current_chunk, word_count, text, search_index,file_name)
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

    char_idx = 0  # track running character index

    for i in range(0, len(words), CHUNKING_SIZE):
        chunk_words = words[i:i + CHUNKING_SIZE]
        chunk_text = " ".join(chunk_words)

        # Find where this chunk starts and ends in the original text
        start_idx = text.find(chunk_text, char_idx)
        end_idx = start_idx + len(chunk_text)

        chunk = Chunk(
            id = uuid.uuid4(),
            name_space=file_name,
            text=chunk_text,
            chunk_size=len(chunk_words),
            char_start=start_idx,
            char_end=end_idx,
            time_end=None, 
            time_start=None
        )
        chunks.append(chunk)
        char_idx = end_idx  # move past this chunk

    logger.debug(f"Created {len(chunks)} chunks from {file_name}")
    return chunks
def run(raw_transcripts: list[tuple[str, str]],data_format: TypeOfFormat) -> list[Chunk]:
    """
    Processes raw transcripts by applying preprocessing steps, including:

    1. Chunking data into fixed-size word batches
    2. Adding metadata to each chunk

    :param raw_transcripts: List of (filename, content) tuples
    :param data_format: Format of the data (e.g., SRT or TXT)
    :return: List of Chunk objects
    """
    logger.info(f"Starting preprocessing of {len(raw_transcripts)} transcripts with format: {data_format.name}")
    cleaned_transcripts: list[Chunk] = []
    
    for i, raw_transcript in enumerate(raw_transcripts, 1):
        file_name = raw_transcript[0]
        logger.info(f"Processing transcript {i}/{len(raw_transcripts)}: {file_name}")
        
        chunks: list[Chunk]
        if data_format.value == TypeOfFormat.SRT.value:
            chunks  = chunk_srt(raw_transcript)
        elif data_format.value == TypeOfFormat.TXT.value:
            chunks = chunk_txt(raw_transcript)
        else:
            logger.error(f"Unsupported format: {data_format}")
            raise ValueError(f"Unsupported format: {data_format}")
        
        cleaned_transcripts.extend(chunks)
        logger.info(f"Completed processing {file_name}: {len(chunks)} chunks")

    logger.info(f"Preprocessing completed. Total chunks created: {len(cleaned_transcripts)}")
    return cleaned_transcripts

def translate_chunks(chunks: list[Chunk]) -> list[tuple[str, Chunk]]:
    logger.info(f"Starting translation of {len(chunks)} chunks")
    
    try:
        with open('/Users/dothanbardichev/Desktop/RAV/RavProject/embed/data_embedder/data/translations/assigned.json', 'r') as f:
            translations = json.load(f)
        logger.debug(f"Loaded {len(translations)} translation mappings")
    except Exception as e:
        logger.error(f"Failed to load translation file: {str(e)}")
        raise

    result: list[tuple[str, Chunk]] = []
    for i, chunk in enumerate(chunks, 1):
        if i % 100 == 0:  # Log progress every 100 chunks
            logger.debug(f"Translated {i}/{len(chunks)} chunks")
        
        words = chunk.text.lower().split()
        translated_words = [translations.get(word, word) for word in words]
        mapped_text = " ".join(translated_words)
        result.append((mapped_text, chunk))

    logger.info(f"Translation completed for {len(result)} chunks")
    return result


