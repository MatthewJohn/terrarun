
import gzip

from terrarun.object_storage import ObjectStorage
import terrarun.config


class AgentFilesystem:
    """Interface to create/update agent filesystems"""

    FILE_SYSTEM_KEY = "agent-filesystem/{run_id}.gzip"

    def __init__(self, run):
        """Store member variables"""
        self._run = run
        self._object_storage = ObjectStorage()

    @property
    def filesystem_key(self):
        """Return filesystem key"""
        return self.FILE_SYSTEM_KEY.format(run_id=self._run.api_id)

    def get_upload_signed_url(self):
        """Get signed upload URL"""
        # Since upload occurs at end of run, allow the signed URL to last for
        # the length of the timeout
        return self._object_storage.create_presigned_upload_url(
            path=self.filesystem_key,
            expiry=terrarun.config.Config.AGENT_JOB_TIMEOUT
        )

    def get_download_signed_url(self):
        """Get filesystem or run"""
        # If filesystem doesn't exit, create an empty one
        if not self._object_storage.file_exists(self.filesystem_key):
            # Create empty filesystem
            self._object_storage.upload_file(path=self.filesystem_key, content=gzip.compress(data=b""))

        # Return signed URL for downloading file
        return self._object_storage.create_presigned_download_url(path=self.filesystem_key)
        