#!/usr/bin/env python3
"""Health check script for Docker container."""

import os
import sys
import tempfile
import time


def check_health() -> bool:
    """Check if the application is healthy."""
    try:
        heartbeat_file = os.environ.get(
            "HEALTHCHECK_HEARTBEAT_FILE",
            os.path.join(tempfile.gettempdir(), "healthy"),
        )
        if not os.path.exists(heartbeat_file):
            return False

        mtime = os.path.getmtime(heartbeat_file)
        return (time.time() - mtime) < 30
    except Exception:  # Healthcheck must catch all errors to return proper exit code
        return False


if __name__ == "__main__":
    sys.exit(0 if check_health() else 1)
