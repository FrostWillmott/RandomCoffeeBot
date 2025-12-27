#!/usr/bin/env python3
"""Health check script for Docker container."""

import sys
import urllib.error
import urllib.request


def check_health() -> bool:
    """Check if the application is healthy."""
    try:
        url = "http://localhost:8000/api/v1/health"
        request = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(request, timeout=5) as response:
            return response.status == 200
    except (urllib.error.URLError, urllib.error.HTTPError):
        return False


if __name__ == "__main__":
    sys.exit(0 if check_health() else 1)
