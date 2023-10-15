import logging
from colorlog import ColoredFormatter


# Set up the logging handler with a ColoredFormatter
handler = logging.StreamHandler()
formatter = ColoredFormatter(
    "%(log_color)s%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%H:%M:%S",
    reset=True,
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'green',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    },
    secondary_log_colors={},
    style='%'
)
handler.setFormatter(formatter)

# Set up the logger with the handler
logger = logging.getLogger('custom_logger')
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)