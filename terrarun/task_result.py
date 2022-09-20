# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from enum import Enum
import datetime
import hashlib
import hmac
import json
import uuid
import requests
import sqlalchemy
import sqlalchemy.orm
from terrarun.audit_event import AuditEvent, AuditEventType

from terrarun.base_object import BaseObject
from terrarun.user import TaskExecutionUserAccess, User, UserType
from terrarun.user_token import UserToken
from terrarun.utils import datetime_to_json, update_object_status
from terrarun.blob import Blob
from terrarun.database import Base, Database
from terrarun.workspace_task import WorkspaceTaskStage
import terrarun.config
import terrarun.utils


class TaskResultStatus(Enum):
    """Task stage statuses"""

    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ERRRORED = "errored"
    CANCELED = "canceled"
    UNREACHABLE = "unreachable"


class TaskResult(Base, BaseObject):

    ID_PREFIX = 'taskrs'

    __tablename__ = 'task_result'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    status = sqlalchemy.Column(sqlalchemy.Enum(TaskResultStatus))
    message_id = sqlalchemy.Column(sqlalchemy.ForeignKey("blob.id"), nullable=True)
    _message = sqlalchemy.orm.relation("Blob", foreign_keys=[message_id])
    url = sqlalchemy.Column(sqlalchemy.String)

    callback_id = sqlalchemy.Column(sqlalchemy.String)

    task_stage_id = sqlalchemy.Column(sqlalchemy.ForeignKey("task_stage.id"), nullable=False)
    task_stage = sqlalchemy.orm.relationship("TaskStage", back_populates="task_results")

    workspace_task_id = sqlalchemy.Column(sqlalchemy.ForeignKey("workspace_task.id"), nullable=False)
    workspace_task = sqlalchemy.orm.relationship("WorkspaceTask", back_populates="task_results")

    start_time = sqlalchemy.Column(sqlalchemy.DateTime)

    @classmethod
    def get_by_callback_id(cls, callback_id):
        """Return task result for callback ID"""
        session = Database.get_session()
        return session.query(cls).where(cls.callback_id==callback_id).first()

    @property
    def message(self):
        """Return plan output value"""
        if self._plan_output_binary and self._plan_output_binary.data:
            return self._plan_output_binary.data
        return {}

    @message.setter
    def message(self, value):
        """Set message"""
        session = Database.get_session()

        if self._plan_output_binary:
            message = self._message
            session.refresh(message)
        else:
            message = Blob()

        message.data = value

        session.add(message)
        session.refresh(self)
        self._message = message
        session.add(self)
        session.commit()

    @property
    def organisation(self):
        """Return organisation"""
        return self.workspace_task.workspace.organisation

    def execute(self):
        """Execute task"""
        payload = json.dumps(self.generate_payload())

        hmac_signature = None
        if self.workspace_task.task.hmac_key:
            hmac_signature = hmac.new(
                self.workspace_task.task.hmac_key.encode('utf-8'),
                payload.encode('utf-8'),
                hashlib.sha512
            ).hexdigest()

        config = terrarun.config.Config()

        # Attempt to call external URL
        for _ in range(config.TASK_CALL_MAX_ATTEMPTS):
            try:
                res = requests.post(
                    self.workspace_task.task.url,
                    data=payload,
                    headers={
                        'Content-Type': 'application/json',
                        'User-Agent': f'TRC/1.0 (+%${config.BASE_URL}; TRC)',
                        'X-TFC-Task-Signature': hmac_signature
                    })
                print('GOT HERE')
                if res.status_code == 200:
                    break
            except requests.exceptions.ConnectionError:
                pass
        else:
            # If unable to get 200 response from remote,
            # mark task result as failed
            update_object_status(self, TaskResultStatus.FAILED)
            return

        # Update start time of request and mark as running
        self.update_attributes(start_time=datetime.datetime.now())
        update_object_status(self, TaskResultStatus.RUNNING)

    def generate_payload(self):
        """Create payload to sent to remote endpoint"""
        # Create temporary user, mapping and token
        callback_user = User(
            # Give a fake username
            username=self.api_id,
            email=None,
            service_account=False,
            user_type=UserType.TASK_EXECUTION_USER
        )
        session = Database.get_session()
        session.add(callback_user)

        task_exec_access = TaskExecutionUserAccess(
            user=callback_user,
            run=self.task_stage.run
        )
        session.add(task_exec_access)

        callback_token = UserToken.generate_token()
        user_token = UserToken(
            expiry=datetime.datetime.now() + datetime.timedelta(minutes=10),
            user=callback_user,
            token=callback_token)
        session.add(user_token)

        self.callback_id = str(uuid.uuid4())
        session.add(self)
        session.commit()

        config = terrarun.config.Config()
        payload = {
            "payload_version": 1,
            "access_token": callback_token,
            "stage": self.workspace_task.stage.value,
            "is_speculative": self.task_stage.run.configuration_version.speculative,
            "task_result_id": self.api_id,
            "task_result_enforcement_level": self.workspace_task.enforcement_level.value,
            "task_result_callback_url": f"{config.BASE_URL}/api/v2/task-results/{self.callback_id}",
            "run_app_url": f"{config.BASE_URL}/app/{self.task_stage.run.configuration_version.workspace.organisation.name}/{self.task_stage.run.configuration_version.workspace.name}/runs/{self.task_stage.run.api_id}",
            "run_id": self.task_stage.run.api_id,
            "run_message": self.task_stage.run.message,
            "run_created_at": datetime_to_json(self.task_stage.run.created_at),
            "run_created_by": self.task_stage.run.created_by.username,
            "workspace_id": self.task_stage.run.configuration_version.workspace.api_id,
            "workspace_name": self.task_stage.run.configuration_version.workspace.name,
            "workspace_app_url": f"{config.BASE_URL}/app/{self.task_stage.run.configuration_version.workspace.organisation.name}/{self.task_stage.run.configuration_version.workspace.name}",
            "organization_name": self.task_stage.run.configuration_version.workspace.organisation.name,
            "plan_json_api_url": f"{config.BASE_URL}/api/v2/plans/{self.task_stage.run.plan.api_id}/json-output" if self.task_stage.run.plan else None,
            "vcs_repo_url": None,
            "vcs_branch": None,
            "vcs_pull_request_url": None,
            "vcs_commit_url": None
        }

        if self.task_stage.stage is WorkspaceTaskStage.PRE_PLAN:
            payload["configuration_version_id"] = self.task_stage.run.configuration_version.api_id
            payload["configuration_version_download_url"] = f"{config.BASE_URL}/api/v2/runs/{self.task_stage.run.api_id}/configuration-version/download"
            payload["workspace_working_directory"] = None

        elif self.task_stage.stage in [WorkspaceTaskStage.POST_PLAN, WorkspaceTaskStage.PRE_APPLY]:
            payload["plan_json_api_url"] = f"{config.BASE_URL}/api/v2/plans/{self.task_stage.run.plan.api_id}/json-output"
        
        return payload

    def handle_callback(self, status, message, url):
        """Handle callback"""
        self.update_attributes(url=url)
        update_object_status(self, status)
        self.message = message

    def get_api_details(self):
        """Return API details for task"""
        session = Database.get_session()
        audit_events = {
            '{}-at'.format(Database.decode_blob(event.new_value).replace('_', '-')): terrarun.utils.datetime_to_json(event.timestamp)
            for event in session.query(AuditEvent).where(
                AuditEvent.object_id==self.id,
                AuditEvent.object_type==self.ID_PREFIX,
                AuditEvent.event_type==AuditEventType.STATUS_CHANGE)
        }
        return {
            "id": self.api_id,
            "type": "task-results",
            "attributes": {
                "message": self.message,
                "status": self.status.value,
                "status-timestamps": audit_events,
                "url": "https://external.service/project/task-123abc",
                "created-at": "2022-06-08T12:31:56.954Z",
                "updated-at": "2022-06-08T12:32:12.27Z",
                "task-id": self.workspace_task.task.api_id,
                "task-name": self.workspace_task.task.name,
                "task-url": self.workspace_task.task.url,
                "stage": self.task_stage.stage.value,
                "is-speculative": self.task_stage.run.configuration_version.speculative,
                "workspace-task-id": self.workspace_task.api_id,
                "workspace-task-enforcement-level": self.workspace_task.enforcement_level.value
            },
            "relationships": {
                "task-stage": {
                    "data": {
                        "id": self.task_stage.api_id,
                        "type": "task-stages"
                    }
                }
            },
            "links": {
                "self": f"/api/v2/task-results/{self.api_id}"
            }
        }