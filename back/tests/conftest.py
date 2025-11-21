import os
import shutil
import pytest

BASE_DIR = os.path.dirname(__file__)
TEST_DATA_DIR = os.path.join(BASE_DIR, 'gamedata')
PROD_DATA_DIR = os.path.join(BASE_DIR, '..', 'gamedata')

# Set the environment variable for the application to use the test data directory
os.environ["JDR_DATA_DIR"] = TEST_DATA_DIR

@pytest.fixture(autouse=True)
def clean_test_data_dir():
    """
    Automatically clean tests/gamedata/ before each test and ensure it exists.
    This keeps tests isolated from previous runs and production data.
    """
    # Remove existing directory contents
    if os.path.isdir(TEST_DATA_DIR):
        shutil.rmtree(TEST_DATA_DIR)
    os.makedirs(TEST_DATA_DIR, exist_ok=True)
    
    # Create necessary subdirectories that the app expects
    os.makedirs(os.path.join(TEST_DATA_DIR, 'sessions'), exist_ok=True)
    os.makedirs(os.path.join(TEST_DATA_DIR, 'characters'), exist_ok=True)
    
    # Copy scenarios from production to test data
    prod_scenarios_dir = os.path.join(PROD_DATA_DIR, 'scenarios')
    test_scenarios_dir = os.path.join(TEST_DATA_DIR, 'scenarios')
    if os.path.isdir(prod_scenarios_dir):
        shutil.copytree(prod_scenarios_dir, test_scenarios_dir)
    else:
        os.makedirs(test_scenarios_dir, exist_ok=True)
    
    yield
    
    # Clean up after as well
    if os.path.isdir(TEST_DATA_DIR):
        shutil.rmtree(TEST_DATA_DIR)
        os.makedirs(TEST_DATA_DIR, exist_ok=True)
