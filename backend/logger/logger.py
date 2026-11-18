import json
import logging
from datetime import datetime, timezone

from conf.config import APP_NAME, DEBUG


def init_logger(access_info):
    """Log JSON 1 dòng ra stdout → CloudWatch Logs"""
    logger = logging.getLogger(APP_NAME)
    logger.setLevel(logging.DEBUG if DEBUG else logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        logger.addHandler(logging.StreamHandler())
    logger.handlers[0].setFormatter(Formatter(access_info))


def get_logger():
    return logging.getLogger(APP_NAME)


class Formatter(logging.Formatter):
    def __init__(self, access_info):
        super().__init__()
        self.access_info = access_info

    def format(self, record):
        log = {
            "time": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            **self.access_info,
        }
        if hasattr(record, "details"):
            log["details"] = record.details
        if record.exc_info:
            log["exception"] = self.formatException(record.exc_info)
        return json.dumps(log, ensure_ascii=False, default=str)
