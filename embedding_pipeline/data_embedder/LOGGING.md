# Logging Configuration

This document describes the logging configuration for the data embedder pipeline.

## Overview

The logging system has been configured to provide comprehensive tracking of the embedding pipeline operations. It includes:

- **Main pipeline logger**: Tracks overall pipeline execution
- **Component-specific loggers**: Separate loggers for data, preprocessing, embedding, and database operations
- **File and console output**: Logs are written to both files and console
- **Timestamped log files**: Each run creates timestamped log files

## Logger Structure

### Main Logger
- **Name**: `embedding_pipeline`
- **Purpose**: Overall pipeline execution tracking
- **Usage**: `from data_embedder.logger_config import logger`

### Component Loggers
- **Data Logger**: `embedding_pipeline.data` - Tracks data loading operations
- **Preprocess Logger**: `embedding_pipeline.preprocess` - Tracks preprocessing operations
- **Embedding Logger**: `embedding_pipeline.embedding` - Tracks embedding generation
- **Database Logger**: `embedding_pipeline.database` - Tracks database operations

## Log Files

Log files are stored in the `logs/` directory with the following naming convention:
- `pipeline_YYYYMMDD_HHMMSS.log` - Main pipeline logs
- `data_YYYYMMDD_HHMMSS.log` - Data operation logs
- `preprocess_YYYYMMDD_HHMMSS.log` - Preprocessing logs
- `embedding_YYYYMMDD_HHMMSS.log` - Embedding logs
- `database_YYYYMMDD_HHMMSS.log` - Database logs

## Log Format

All logs use the following format:
```
YYYY-MM-DD HH:MM:SS - logger_name - LEVEL - message
```

## Log Levels

- **INFO**: General operational information
- **DEBUG**: Detailed debugging information
- **WARNING**: Warning messages
- **ERROR**: Error messages with stack traces

## Usage Examples

### Basic Usage
```python
from data_embedder.logger_config import logger

logger.info("Starting pipeline")
logger.error("An error occurred", exc_info=True)
```

### Component-Specific Logging
```python
from data_embedder.logger_config import data_logger, preprocess_logger

data_logger.info("Loading data files...")
preprocess_logger.debug("Processing chunk 1/100")
```

## Testing

Run the test script to verify logging is working:
```bash
cd data_embedder
python test_logging.py
```

This will create test log entries and verify that all loggers are functioning properly.

## Configuration

The logging configuration is centralized in `logger_config.py`. Key features:

- **Automatic log directory creation**: Creates `logs/` directory if it doesn't exist
- **Duplicate handler prevention**: Prevents multiple handlers on the same logger
- **Timestamped files**: Each run creates new log files with timestamps
- **Console and file output**: Logs appear both in console and files

## Integration

The logging has been integrated into all major components:

1. **Main Pipeline** (`insert.py`): Tracks overall execution flow
2. **Data Loading** (`datastore/`): Tracks file loading operations
3. **Preprocessing** (`preprocess/`): Tracks chunking and translation
4. **Embedding** (`embedding/`): Tracks embedding generation
5. **Database** (`db/`): Tracks database operations

All logging statements are non-intrusive and don't change the application logic. 