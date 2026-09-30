import logging
import os
import sys

def initialize_logger(name:str, log_level:str|None=None)-> logging.Logger:
    logger = logging.getLogger(name)

    if log_level is None:
        log_level = os.environ.get("LOGLEVEL", "INFO")

    logger.setLevel(log_level)
    if len(logger.handlers) == 0:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger

