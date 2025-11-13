import os
import shutil
import pytest

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
CHAR_DIR = os.path.join(BASE_DIR, 'data', 'characters')

@pytest.fixture(autouse=True)
def clean_characters_dir():
    """
    Automatically clean data/characters/ before each test and ensure it exists.
    This keeps tests isolated from previous runs.
    """
    # Remove existing directory contents
    if os.path.isdir(CHAR_DIR):
        shutil.rmtree(CHAR_DIR)
    os.makedirs(CHAR_DIR, exist_ok=True)
    yield
    # Clean up after as well
    if os.path.isdir(CHAR_DIR):
        shutil.rmtree(CHAR_DIR)
        os.makedirs(CHAR_DIR, exist_ok=True)
