"""
Pytest configuration for pydiameter2json tests.
"""
import pytest
import sys
import os

# Add the project root to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

@pytest.fixture(scope="session")
def test_data_dir():
    """Fixture providing the test data directory path."""
    return os.path.join(os.path.dirname(__file__))