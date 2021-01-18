import sys
from logging.handlers import RotatingFileHandler
from logging import Handler, StreamHandler, Formatter, LogRecord
from typing import Dict, List

MAX_BYTES = 10_000_000  # 10 MB
BACKUP_COUNT = 5


class LogHandler(Handler):
    file_handler: RotatingFileHandler
    print_handler: StreamHandler

    def __init__(self, formatter: Formatter, filename: str, max_bytes=MAX_BYTES, backup_count=BACKUP_COUNT):
        super().__init__()
        self.setFormatter(formatter)

        self.print_handler = StreamHandler(sys.stdout)
        self.print_handler.setFormatter(formatter)

        self.file_handler = RotatingFileHandler(filename, maxBytes=max_bytes, backupCount=backup_count)
        self.file_handler.setFormatter(formatter)

    def emit(self, record: LogRecord) -> None:
        handlers: List[Handler] = [self.file_handler, self.print_handler]
        for handler in handlers:
            if isinstance(record.args, Dict) and record.args.get('format', 'default') == 'plain':
                formatter = handler.formatter
                handler.setFormatter(None)
                handler.emit(record)
                handler.setFormatter(formatter)
            else:
                handler.emit(record)
