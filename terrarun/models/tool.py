# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

import re
from enum import Enum

import requests
import sqlalchemy
import sqlalchemy.orm
import semantic_version
from terrarun.errors import InvalidVersionNumberError, ToolChecksumUrlPlaceholderError, ToolUrlPlaceholderError, ToolVersionAlreadyExistsError, UnableToDownloadToolArchiveError, UnableToDownloadToolChecksumFileError

from terrarun.logger import get_logger
from terrarun.object_storage import ObjectStorage
from terrarun.models.base_object import BaseObject
import terrarun.database
import terrarun.models.organisation
import terrarun.models.run
import terrarun.models.configuration
from terrarun.database import Base, Database
import terrarun.utils


logger = get_logger(__name__)


class ToolType(Enum):

    TERRAFORM_VERSION = "terraform-versions"

ToolType.TERRAFORM_VERSION.display_name = "terraform"


class Tool(Base, BaseObject):

    ZIP_FORMAT = "terraform_{version}_{platform}_{arch}.zip"
    ZIP_UPSTREAM_URL = "https://releases.hashicorp.com/terraform/{version}/{zip_file}"
    CHECKSUM_UPSTREAM_URL = "https://releases.hashicorp.com/terraform/{version}/terraform_{version}_SHA256SUMS"
    S3_KEY_ZIP = "tools/{type}/{api_id}/{zip_file}"
    S3_KEY_CHECKSUM = "tools/{type}/{api_id}/terraform_{version}_SHA256SUMS"
    CHECKSUM_FILE_RE = re.compile(r"^([a-z0-9]+)\s+(.*)")

    ID_PREFIX = 'tool'

    __tablename__ = 'tool'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True)
    api_id_fk = sqlalchemy.Column(
        sqlalchemy.ForeignKey("api_id.id"), nullable=True)
    api_id_obj = sqlalchemy.orm.relation("ApiId", foreign_keys=[api_id_fk])

    tool_type = sqlalchemy.Column(sqlalchemy.Enum(ToolType), nullable=False)
    version = sqlalchemy.Column(
        terrarun.database.Database.GeneralString, nullable=False)
    sha = sqlalchemy.Column(
        terrarun.database.Database.GeneralString, nullable=True)

    enabled = sqlalchemy.Column(sqlalchemy.Boolean, default=True)

    deprecated = sqlalchemy.Column(sqlalchemy.Boolean, default=False)
    deprecated_reason = sqlalchemy.Column(
        terrarun.database.Database.GeneralString, nullable=True)
    # Override default URL
    custom_url = sqlalchemy.Column(
        terrarun.database.Database.GeneralString, nullable=True, name="url")
    custom_checksum_url = sqlalchemy.Column(
        terrarun.database.Database.GeneralString, nullable=True, name="checksum_url")

    created_at = sqlalchemy.Column(
        sqlalchemy.DateTime, default=sqlalchemy.sql.func.now())

    # @TODO Implement usage count
    usage = 0

    @classmethod
    def get_all(cls, tool_type):
        """Return all tools"""
        session = Database.get_session()
        return session.query(cls).filter(cls.tool_type == tool_type).all()

    @classmethod
    def get_by_version(cls, tool_type, version):
        """Get tool by version"""
        session = Database.get_session()
        return session.query(cls).filter(cls.tool_type == tool_type, cls.version == version).first()

    def update_attributes(self, session=None, **kwargs):
        """Update attributes"""
        update_kwargs = {}

        if 'custom_url' in kwargs:
            # Validate custom URL
            self._validate_url(kwargs['custom_url'])
            # Set the objects' custom URL and
            # attempt a download to ensure that it works
            self.custom_url = kwargs['custom_url']
            self.get_presigned_download_url(force_download=True)
            update_kwargs['custom_url'] = kwargs['custom_url']

        if 'custom_checksum_url' in kwargs:
            self._validate_checksum_url(kwargs['custom_checksum_url'])
            # Set the objects' custom checksum URL and
            # attempt a download to ensure that it works
            self.custom_checksum_url = kwargs['custom_checksum_url']

        if 'sha' in kwargs:
            update_kwargs['sha'] = kwargs['sha']

        if 'enabled' in kwargs:
            update_kwargs['enabled'] = kwargs['enabled']

        if 'deprecated' in kwargs:
            update_kwargs['deprecated'] = kwargs['deprecated']

        if 'deprecated_reason' in kwargs:
            update_kwargs['deprecated_reason'] = kwargs['deprecated_reason']

        return super().update_attributes(session=session, **update_kwargs)

    @staticmethod
    def _validate_version(version):
        """Validate version number"""
        try:
            semantic_version.Version(version)
        except ValueError:
            raise InvalidVersionNumberError('Tool version number is invalid')

    @staticmethod
    def _validate_url(url):
        """Validate download URL"""
        if url:
            try:
                url.format(platform="test", arch="test")
            except ValueError:
                raise ToolUrlPlaceholderError(
                    "Tool URL contains invalid placeholder")

    @staticmethod
    def _validate_checksum_url(checksum_url):
        """Validate checksum url"""
        if checksum_url:
            try:
                checksum_url.format(platform="test", arch="test")
            except ValueError:
                raise ToolChecksumUrlPlaceholderError(
                    "Tool checksum URL contains invalid placeholder")

    @classmethod
    def upsert_by_version(cls, tool_type, version, custom_url=None, custom_checksum_url=None,
                          sha=None, enabled=True, deprecated=False, deprecated_reason=None,
                          only_create=False):
        """Upsert version based on version number"""
        # Check version is valid
        cls._validate_version(version)
        cls._validate_url(custom_url)
        cls._validate_checksum_url(custom_checksum_url)

        session = Database.get_session()
        pre_existing = session.query(cls).filter(
            cls.tool_type == tool_type,
            cls.version == version
        ).first()

        # If the tool version already exists, raise exception
        # if only creating, otherwise return found version
        if pre_existing:
            if only_create:
                raise ToolVersionAlreadyExistsError(
                    "Tool version already exists")
            return pre_existing

        # Create new version
        tool_version = cls(
            tool_type=tool_type,
            version=version,
            custom_url=custom_url,
            custom_checksum_url=custom_checksum_url,
            sha=sha,
            deprecated=deprecated,
            deprecated_reason=deprecated_reason,
            enabled=enabled
        )

        session.add(tool_version)
        session.commit()

        # Attempt to download archive
        try:
            tool_version.get_presigned_download_url(force_download=True)
        except Exception:
            # If a file fails to be downloaded,
            # remove from database and raise exception
            session.delete(tool_version)
            session.commit()
            raise

        # Attempt to download checksum
        try:
            tool_version.get_checksum(force_download=True)
        except Exception:
            # If a file fails to be downloaded,
            # remove from database and raise exception
            tool_version.remove_file_archive()
            session.delete(tool_version)
            session.commit()
            raise

        return tool_version

    @property
    def official(self):
        """Determine if the release is official, based on whether the URL has been overriden"""
        return bool(self.custom_url)

    @property
    def beta(self):
        """Determine if release is beta"""
        return bool(semantic_version.Version(self.version).prerelease)

    @property
    def url(self):
        """Return URL for tool"""
        if self.custom_url:
            return self.custom_url

        elif self.tool_type is ToolType.TERRAFORM_VERSION:
            zip_file = self.ZIP_FORMAT.format(
                version=self.version, platform="{platform}", arch="{arch}")
            return self.ZIP_UPSTREAM_URL.format(version=self.version, zip_file=zip_file)

    @property
    def checksum_url(self):
        """Return checksum URL"""
        if self.custom_checksum_url:
            return self.custom_checksum_url

        elif self.tool_type is ToolType.TERRAFORM_VERSION:
            # format zip file, retaining placeholders for platform and arch
            return self.CHECKSUM_UPSTREAM_URL.format(version=self.version)

    def delete(self):
        """Delete tool"""
        session = Database.get_session()
        session.delete(self)
        session.commit()

    def get_api_details(self):
        """Return end-user API details"""
        return {
            "id": f"{self.tool_type.display_name}-{self.version}",
            "type": "tool-versions",
            "attributes": {
                "tool": self.tool_type.display_name,
                "version": self.version,
                "url": self.url.format(arch="amd64", platform="linux"),
                "sha": self.get_checksum(),
                "official": self.official,
                "enabled": self.enabled,
                "beta": self.beta,
                "deprecated": self.deprecated,
                "deprecated-reason": self.deprecated_reason
            }
        }

    def get_presigned_download_url(self, force_download=False):
        """Obtain pre-signed URL for terraform binary"""
        object_storage = ObjectStorage()

        # Generate keys in s3
        zip_file = self.ZIP_FORMAT.format(
            version=self.version, platform="linux", arch="amd64")
        object_key = self.S3_KEY_ZIP.format(
            zip_file=zip_file, type=self.tool_type.value, api_id=self.api_id)

        logger.debug(f'Getting pre-signed URL for {zip_file}')

        # Check if file exists in s3
        # If file does not exist, download and upload to s3
        if not object_storage.file_exists(object_key) or force_download:
            download_url = self.url.format(arch="amd64", platform="linux")

            logger.debug(
                f'Terraform zip does not exist.. downloading: {download_url}')
            # Get binary
            try:
                res = requests.get(
                    download_url,
                    headers={
                        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0"
                    }
                )
            except:
                raise UnableToDownloadToolArchiveError(
                    "An error occured whilst downloading Terraform zip")
            if res.status_code != 200:
                raise UnableToDownloadToolArchiveError(
                    "Non-200 response whilst downloading Terraform zip")

            logger.debug('Downloaded.. uploading to s3')
            object_storage.upload_file(path=object_key, content=res.content)
            logger.debug('Uploaded to s3')

        # Create pre-signed URL
        logger.debug('Creating pre-signed URL')
        url = object_storage.create_presigned_download_url(path=object_key)
        logger.debug(f'URL: {url}')
        return url

    def get_checksum(self, platform="linux", arch="amd64", force_download=False):
        """Obtain checksum for zip file version"""
        # If custom SHA has been defined, return it
        if self.sha:
            return self.sha

        object_storage = ObjectStorage()
        zip_file = self.ZIP_FORMAT.format(
            version=self.version, platform=platform, arch=arch)
        checksum_key = self.S3_KEY_CHECKSUM.format(
            version=self.version,
            type=self.tool_type.value,
            api_id=self.api_id
        )
        logger.debug(f'Getting checksum for {zip_file}')

        # Check if file exists in s3
        # If file does not exist, download and upload to s3
        if not object_storage.file_exists(checksum_key) or force_download:
            checksum_file_download_url = self.checksum_url
            logger.debug(
                f'Checksum file does not exist.. downloading: {checksum_file_download_url}')

            # Get checksum file
            try:
                res = requests.get(checksum_file_download_url, headers={
                                   "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0"})
            except:
                raise UnableToDownloadToolChecksumFileError(
                    "An error occured whilst downloading Terraform checksum file")

            if res.status_code != 200:
                raise UnableToDownloadToolChecksumFileError(
                    "Non-200 response whilst downloading Terraform checksum file")

            logger.debug('Downloaded.. uploading to s3')

            object_storage.upload_file(path=checksum_key, content=res.content)
            logger.debug('Uploaded to s3')

        logger.debug('Downloading checksum file from s3')
        checksum_file_content = object_storage.get_file(checksum_key)
        logger.debug(checksum_file_content)
        logger.debug('Download complete')

        for line in checksum_file_content.decode("utf-8").split("\n"):
            logger.debug(f'Checking line: {line}')
            if checksum_line_match := self.CHECKSUM_FILE_RE.match(line):
                if checksum_line_match.group(2) == zip_file:
                    logger.debug(
                        f'Found match for terraform {checksum_line_match.group(2)}: {checksum_line_match.group(1)}')
                    return checksum_line_match.group(1)

        logger.debug('No checksum found for zip')
        return None

    def remove_file_archive(self):
        """Remove file from archive"""
        object_storage = ObjectStorage()

        # Generate keys in s3
        zip_file = self.ZIP_FORMAT.format(
            version=self.version, platform="linux", arch="amd64")
        object_key = self.S3_KEY_ZIP.format(
            zip_file=zip_file, type=self.tool_type.value, api_id=self.api_id)
        if object_storage.file_exists(object_key):
            object_storage.delete_file(object_key)
