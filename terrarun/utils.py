# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

def datetime_to_json(datetime_obj):
    """Convert datetime to format for JSON output"""
    if datetime_obj is None:
        return None
    return datetime_obj.isoformat()
