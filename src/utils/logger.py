# src/utils/logger.py

import logging
import os
import sys


def setup_logger():
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler("logs/harvester.log"),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("GraphAOT")