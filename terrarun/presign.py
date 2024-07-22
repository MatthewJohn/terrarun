# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0


import base64
from cryptography.fernet import Fernet

import terrarun.config

class Presign:
    """Interface to encrypt/decrypt pre-sign keys"""

    @property
    def fernet(self):
        """Obtain instance of farnet"""
        if not terrarun.config.Config().AGENT_PRESIGN_ENCRYPTION_KEY:
            raise Exception('AGENT_PRESIGN_ENCRYPTION_KEY must be set')
        return Fernet(base64.b64encode(terrarun.config.Config().AGENT_PRESIGN_ENCRYPTION_KEY.encode('utf-8')))

    def encrypt(self, input):
        """Encrypt token"""
        return self.fernet.encrypt(input.encode()).hex()
    
    def decrypt(self, input):
        """Decrypt token"""
        try:
            return self.fernet.decrypt(bytes.fromhex(input)).decode()
        except ValueError:
            return None
