# Copyright (C) 2024 Matt Comben - All Rights Reserved
# SPDX-License-Identifier: GPL-2.0

from typing import Optional
from dataclasses import dataclass

import terrarun.models.user
import terrarun.models.run_queue


@dataclass
class AuthContext:
    """Handle passing current authentication context"""

    user: Optional['terrarun.models.user.User']
    job: Optional['terrarun.models.run_queue.RunQueue']
