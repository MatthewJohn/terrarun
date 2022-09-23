# Copyright (C) Matt Comben - All Rights Reserved
# Unauthorized copying of this file, via any medium is strictly prohibited
# Proprietary and confidential

from enum import Enum
import json
import sqlalchemy
import sqlalchemy.orm

import bcrypt

import terrarun.organisation
from terrarun.base_object import BaseObject
from terrarun.database import Base, Database
from terrarun.permissions.user import UserPermissions


class UserType(Enum):

    # Normal user of the site
    NORMAL = "normal"
    # Task execution user for a single run
    TASK_EXECUTION_USER = "task-execution"


class TaskExecutionUserAccess(Base):
    """Table to bind temporary task execution users to the run"""

    __tablename__ = 'task_execution_user_access'

    user_id = sqlalchemy.Column(sqlalchemy.ForeignKey("user.id"), nullable=False, primary_key=True)
    user = sqlalchemy.orm.relation("User")
    run_id = sqlalchemy.Column(sqlalchemy.ForeignKey("run.id"), nullable=False)
    run = sqlalchemy.orm.relation("Run")
    


class User(Base, BaseObject):

    ID_PREFIX = 'user'

    __tablename__ = 'user'
    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)

    username = sqlalchemy.Column(sqlalchemy.String, unique=True)
    salt = sqlalchemy.Column(sqlalchemy.BLOB)
    _password = sqlalchemy.Column("password", sqlalchemy.BLOB)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)
    service_account = sqlalchemy.Column(sqlalchemy.Boolean)
    site_admin = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    user_type = sqlalchemy.Column(sqlalchemy.Enum(UserType, default=UserType.NORMAL))

    user_tokens = sqlalchemy.orm.relation("UserToken", back_populates="user")

    teams = sqlalchemy.orm.relationship("TeamUserMembership", back_populates="user")

    def __init__(self, *args, **kwargs):
        """Setup salt"""
        super(User, self).__init__(*args, **kwargs)
        if not self.salt:
            self.salt = self.generate_salt()

    @classmethod
    def get_by_username(cls, username):
        """Return user by username"""
        session = Database.get_session()
        return session.query(cls).filter(cls.username==username).first()

    @classmethod
    def generate_salt(cls):
        """Generate salt"""
        return bcrypt.gensalt()

    @classmethod
    def create_user(cls, username, email, password):
        """Create user."""
        session = Database.get_session()
        user = cls(
            username=username,
            email=email,
            service_account=False,
            user_type=UserType.NORMAL)
        user.password = password
        session.add(user)
        session.commit()
        return user

    @property
    def password(self):
        """Return hashed password"""
        return self._password

    @password.setter
    def password(self, value):
        """hash password before storing"""
        password = value.encode(encoding='UTF-8', errors='strict')
        hashed_password = bcrypt.hashpw(password, self.salt)
        self._password = hashed_password

    def check_password(self, password):
        """Check password."""
        # Only authenticate 'Normal' users with passwords
        if not self.user_type == UserType.NORMAL:
            return False
        if not self.password:
            return False
        return bcrypt.checkpw(
            password.encode(encoding='UTF-8', errors='strict'),
            self.password
        )

    def has_task_execution_run_access(self, run):
        """Check access permissions for task execution users"""
        if self.user_type is not UserType.TASK_EXECUTION_USER:
            return False

        session = Database.get_session()
        access = session.query(TaskExecutionUserAccess).filter(
            TaskExecutionUserAccess.user==self,
            TaskExecutionUserAccess.run==run).first()

        return bool(access)

    @property
    def organisations(self):
        """List of organisations that the user is a member of."""
        session = Database.get_session()

        # Return user as being a member of all organisations,
        # if they're a site admin
        if self.site_admin:
            print('Site ADMIN')
            return session.query(terrarun.organisation.Organisation).all()

        organisations = []
        org_ids = []
        # Iterate through all team memberships and all team workspace accesses
        # to determine which organisations this user has access to
        for team in self.teams:
            for workspace_access in team.workspace_accesses:
                org = workspace_access.workspace.organisation
                if org.web_id not in org_ids:
                    org_ids.append(org_ids)
                    organisations.append(org)
        return organisations

    def get_account_details(self, effective_user):
        """Get API details for account endpoint."""
        user_permissions = UserPermissions(current_user=effective_user, user=self)
        return {
            "id": self.api_id,
            "type": "users",
            "attributes": {
                "username": self.username,
                "is-service-account": self.service_account,
                "avatar-url": "https://www.gravatar.com/avatar/9babb00091b97b9ce9538c45807fd35f?s=100&d=mm",
                "v2-only": False,
                "is-site-admin": self.site_admin,
                "is-sso-login": False,
                "email": self.email,
                "unconfirmed-email": None,
                "password": None,
                "enterprise-support": False,
                "two-factor": {
                    "enabled": False,
                    "verified": False
                },
                "permissions": user_permissions.get_api_permissions()
            },
            "relationships": {
                "authentication-tokens": {
                    "links": {
                        "related": f"/api/v2/users/{self.api_id}/authentication-tokens"
                    }
                }
            },
            "links": {
                "self": f"/api/v2/users/{self.api_id}"
            }
        }

    def get_admin_details(self):
        """Get API details for admin endpoint."""
        return {
            "id": self.api_id,
            "type": "users",
            "attributes": {
                "username": self.username,
                "email": self.email,
                "avatar-url": "https://www.gravatar.com/avatar/9babb00091b97b9ce9538c45807fd35f?s=100&d=mm",
                "is-admin": self.site_admin,
                "is-suspended": self.suspended,
                "is-service-account": self.service_account
            },
            "relationships": {
                "organizations": {
                    "data": [
                        {
                            "id": organisation.name_id,
                            "type": "organizations"
                        }
                        for organisation in self.organisations
                    ]
                }
            },
            "links": {
                "self": f"/api/v2/users/{self.api_id}"
            }
        }

    def get_api_details(self, effective_user):
        """Return API details for user"""
        user_permissions = UserPermissions(current_user=effective_user, user=self)
        return {
            "id": self.api_id,
            "type": "users",
            "attributes": {
                "username": self.username,
                "is-service-account": self.service_account,
                "avatar-url": "https://www.gravatar.com/avatar/9babb00091b97b9ce9538c45807fd35f?s=100&d=mm",
                "v2-only": False,
                "permissions": user_permissions.get_api_permissions()
            },
            "relationships": {
                "authentication-tokens": {
                    "links": {
                        "related": f"/api/v2/users/{self.api_id}/authentication-tokens"
                    }
                }
            },
            "links": {
                "self": f"/api/v2/users/{self.api_id}"
            }
        }
