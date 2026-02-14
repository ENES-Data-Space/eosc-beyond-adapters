import logging
import sys
import os
import datetime

EXPORT_LOG_DIR = "./logs"
os.makedirs(EXPORT_LOG_DIR, exist_ok=True)

def setup_logging(level=logging.INFO):
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(EXPORT_LOG_DIR, f"stac_export_{timestamp}.log")

    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(log_file, encoding="utf-8")
        ]
    )

    logging.info(f"Logging started. Log file: {log_file}")
