
import sys
import logging
import inspect

from terrarun.config import Config

log_levels = {
    class_log_level.split(':')[0]: class_log_level.split(':')[1]
    for class_log_level in Config.MODULE_LOG_LEVELS.split("\n")
    if class_log_level and len(class_log_level.split(':')) == 2
}

def get_logger(obj):
    name = "terrarun"
    class_name = ""

    if 'api_id' in dir(obj) and isinstance(obj.api_id, str):
        name = obj.api_id
        class_name = obj.__class__.__name__
    else:
        name = "Unknown"
        if hasattr(obj, "__name__"):
            name = obj.__name__
        elif hasattr(obj, "__class__") and hasattr(obj.__class__, "__name__"):
            name = obj.__class__.__name__
        name = name
        class_name = name

    logger = logging.getLogger(name)
    logger.setLevel(log_levels.get(class_name, Config().LOG_LEVEL_DEFAULT).upper())

    # Add handler to logger
    logHandler = logging.StreamHandler(sys.stdout)
    logHandler.setLevel(log_levels.get(class_name, Config().LOG_LEVEL_DEFAULT).upper())
    logger.addHandler(logHandler)

    # Set handler format
    logFormat = logging.Formatter("%(asctime)s - [%(filename)s:%(lineno)s - %(funcName)20s() ] - %(name)s - %(levelname)s - %(message)s")
    logHandler.setFormatter(logFormat)

    return logger