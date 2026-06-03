import logging
import sys

class iFilter(logging.Filter):
    def filter(self, record):
        return record.levelno in (logging.DEBUG, logging.INFO)

def setup_root_logger():
    logger = logging.getLogger('main')
    logger.handlers.clear()

    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] [%(process)d] [%(funcName)s] %(message)s",
        datefmt="%d-%b-%y %H:%M:%S",
    )

    cli_h_out = logging.StreamHandler(stream=sys.stdout)
    cli_h_out.setLevel(logging.DEBUG)
    cli_h_out.addFilter(iFilter())
    cli_h_out.setFormatter(formatter)

    cli_h_err = logging.StreamHandler(stream=sys.stderr)
    cli_h_err.setLevel(logging.WARNING)
    cli_h_err.setFormatter(formatter)

    logger.addHandler(cli_h_out)
    logger.addHandler(cli_h_err)
    return logger

# Create a default logger instance that can be imported
logger = setup_root_logger()

