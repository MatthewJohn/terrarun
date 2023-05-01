
import re

import requests

from terrarun.object_storage import ObjectStorage


class TerraformBinary:
    """Obtain terraform binaries"""

    ZIP_FORMAT = "terraform_{version}_{platform}_{arch}.zip"
    ZIP_UPSTREAM_URL = "https://releases.hashicorp.com/terraform/{version}/{zip_file}"
    CHECKSUM_UPSTREAM_URL = "https://releases.hashicorp.com/terraform/{version}/terraform_{version}_SHA256SUMS"
    S3_KEY_ZIP = "terraform-binaries/{zip_file}"
    S3_KEY_CHECKSUM = "terraform-binaries/terraform_{version}_SHA256SUMS"
    CHECKSUM_FILE_RE = re.compile(r"^([a-z0-9]+)\s+(.*)")

    @classmethod
    def get_terraform_url(cls, version):
        """Obtain pre-signed URL for terraform binary"""
        object_storage = ObjectStorage()

        # Generate keys in s3w
        zip_file = cls.ZIP_FORMAT.format(version=version, platform="linux", arch="amd64")
        object_key = cls.S3_KEY_ZIP.format(zip_file=zip_file)
        print(f'Getting pre-signed URL for {zip_file}')

        # Check if file exists in s3
        # If file does not exist, download and upload to s3
        if not object_storage.file_exists(object_key):
            print(f'Terraform zip does not exist.. downloading')
            # Get binary
            res = requests.get(
                cls.ZIP_UPSTREAM_URL.format(zip_file=zip_file, version=version),
                headers={"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0"}
            )
            if res.status_code != 200:
                raise Exception("Non-200 response whilst downloading Terraform zip")
            print('Downloaded.. uploading to s3')
            object_storage.upload_file(path=object_key, content=res.content)
            print('Uploaded to s3')

        # Create pre-signed URL
        print('Creating pre-signed URL')
        url = object_storage.create_presigned_download_url(path=object_key)
        print(f'URL: {url}')
        return url

    @classmethod
    def get_checksum(cls, version):
        """Obtain checksum for zip file version"""
        object_storage = ObjectStorage()
        zip_file = cls.ZIP_FORMAT.format(version=version, platform="linux", arch="amd64")
        checksum_key = cls.S3_KEY_CHECKSUM.format(version=version)
        print(f'Getting checksum for {zip_file}')

        # Check if file exists in s3
        # If file does not exist, download and upload to s3
        if not object_storage.file_exists(checksum_key):
            checksum_file_download_url = cls.CHECKSUM_UPSTREAM_URL.format(version=version)
            print(f'Checksum file does not exist.. downloading: {checksum_file_download_url}')
            # Get checksum file
            res = requests.get(checksum_file_download_url, headers={"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/112.0"})
            if res.status_code != 200:
                raise Exception("Non-200 response whilst downloading Terraform checksum")
            print('Downloaded.. uploading to s3')
            object_storage.upload_file(path=checksum_key, content=res.content)
            print('Uploaded to s3')

        print('Downloading checksum file from s3')
        checksum_file_content = object_storage.get_file(checksum_key)
        print(checksum_file_content)
        print('Download complete')

        for line in checksum_file_content.decode("utf-8").split("\n"):
            print(f'Checking line: {line}')
            if checksum_line_match := cls.CHECKSUM_FILE_RE.match(line):
                if checksum_line_match.group(2) == zip_file:
                    print(f'Found match for terraform {checksum_line_match.group(2)}: {checksum_line_match.group(1)}')
                    return checksum_line_match.group(1)

        print('No checksum found for zip')
        return None
