# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import datetime

def datetime_to_json(datetime_obj):
    """Convert datetime to format for JSON output"""
    if datetime_obj is None:
        return None
    # Hacky method to convert timezone to zulu timezone
    return datetime_obj.replace(tzinfo=datetime.timezone.utc).isoformat().replace('+00:00', 'Z')
