#!/usr/bin/env python3
"""Health check script for Docker container."""

import os
import sys
import time


def check_health() -> bool:
    """Check if the application is healthy."""
    try:
        # Check if heartbeat file exists and was modified recently
        heartbeat_file = "/tmp/healthy"
        if not os.path.exists(heartbeat_file):
            return False

        mtime = os.path.getmtime(heartbeat_file)
        # Healthy if modified within last 30 seconds
        return (time.time() - mtime) < 30
    except Exception:
        return False


if __name__ == "__main__":
    sys.exit(0 if check_health() else 1)
