# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


import sys
import logging
import inspect

from terrarun.config import Config

log_levels = {
    class_log_level.split(':')[0]: class_log_level.split(':')[1]
    for class_log_level in Config.MODULE_LOG_LEVELS.split("\n")
    if class_log_level and len(class_log_level.split(':')) == 2
}

def get_logger(name):

    logger = logging.getLogger(name)
    logger.setLevel(log_levels.get(name, Config().LOG_LEVEL_DEFAULT).upper())

    # Add handler to logger
    logHandler = logging.StreamHandler(sys.stdout)
    logHandler.setLevel(log_levels.get(name, Config().LOG_LEVEL_DEFAULT).upper())
    logger.addHandler(logHandler)

    # Set handler format
    logFormat = logging.Formatter("%(asctime)s - [%(filename)s:%(lineno)s - %(funcName)20s() ] - %(name)s - %(levelname)s - %(message)s")
    logHandler.setFormatter(logFormat)

    return logger