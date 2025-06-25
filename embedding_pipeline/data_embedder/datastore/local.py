from pathlib import Path
from shared.logger_config import data_logger

def get_transcripts_from_local() -> list[tuple[str, str]]:
    """
    Gets transcripts from local storage. Assumes the path is a subdirectory named 'transcripts' in the parent directory.

    :return:
    A list of tuples where the first element is the transcript file name and the second is the file contents.
    """
    data_dir = Path(__file__).resolve().parent.parent / "data/transcripts"
    data_logger.info(f"Looking for transcript files in: {data_dir}")
    
    srt_files = list(data_dir.glob("*.srt"))
    data_logger.info(f"Found {len(srt_files)} SRT files")

    transcripts: list[tuple[str, str]] = []
    for srt_file in srt_files:
        data_logger.debug(f"Loading transcript file: {srt_file.name}")
        try:
            with open(srt_file, encoding="utf-8") as f:
                content = f.read()
                transcripts.append((srt_file.stem, content))
                data_logger.debug(f"Successfully loaded {srt_file.name} ({len(content)} characters)")
        except Exception as e:
            data_logger.error(f"Failed to load transcript file {srt_file.name}: {str(e)}")
            raise

    data_logger.info(f"Successfully loaded {len(transcripts)} transcript files")
    return transcripts
