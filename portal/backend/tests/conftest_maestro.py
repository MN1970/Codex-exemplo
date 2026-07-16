"""
Pytest configuration for Maestro service tests.
Separate from main conftest.py to avoid importing the FastAPI app.
"""

import pytest

# This conftest is intentionally minimal to avoid import issues
# with the main app's security dependencies.
