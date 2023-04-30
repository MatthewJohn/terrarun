# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

import datetime
import string
import secrets

from terrarun.database import Database
import terrarun.models.audit_event


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

def update_object_status(obj, new_status, current_user=None, session=None):
    """Update state of run."""
    print(f"Updating {str(obj)} to from {str(obj.status)} to {str(new_status)}")
    should_commit = False
    if session is None:
        session = Database.get_session()
        session.refresh(obj)
        should_commit = True

    audit_event = terrarun.models.audit_event.AuditEvent(
        organisation=obj.organisation,
        user_id=current_user.id if current_user else None,
        object_id=obj.id,
        object_type=obj.ID_PREFIX,
        old_value=Database.encode_value(obj.status.value) if obj.status else None,
        new_value=Database.encode_value(new_status.value),
        event_type=terrarun.models.audit_event.AuditEventType.STATUS_CHANGE)

    obj.update_attributes(status=new_status, session=session)

    session.add(obj)
    session.add(audit_event)
    if should_commit:
        session.commit()

