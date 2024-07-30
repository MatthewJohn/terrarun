# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

import datetime
import secrets
import string

from terrarun.logger import get_logger


logger = get_logger(__name__)


def generate_random_secret_string(length=64):
    """Generate random secret string"""
    chars = string.ascii_letters + string.digits
    return ''.join(secrets.choice(chars) for i in range(length))


def datetime_to_json(datetime_obj):
    """Convert datetime to format for JSON output"""
    if datetime_obj is None:
        return None
    # Hacky method to convert timezone to zulu timezone
    return datetime_obj.replace(tzinfo=datetime.timezone.utc).isoformat().replace('+00:00', 'Z')

def datetime_from_json(datetime_str):
    """Convert datetime to format for JSON output"""
    if datetime_str is None:
        return None
    # Hacky method to convert timezone from Zulu
    return datetime.datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
