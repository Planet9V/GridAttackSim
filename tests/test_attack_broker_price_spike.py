import os
import shutil
import pytest
from attack_broker import apply_attack_config

@pytest.fixture
def model_path():
    return "Database/13_Nodes_73_Houses"

@pytest.fixture
def setup_teardown_run_file(model_path):
    """
    Fixture to create a temporary run file for testing and clean it up afterwards.
    """
    run_file = os.path.join(model_path, "run_GridLab-D.glm")
    original_file = os.path.join(model_path, "GridLab-D.glm")

    if os.path.exists(run_file):
        os.remove(run_file)

    shutil.copyfile(original_file, run_file)

    yield run_file

    if os.path.exists(run_file):
        os.remove(run_file)

def test_price_spike_attack(model_path, setup_teardown_run_file):
    """
    Tests that the "Price Spike" attack correctly injects the player object and generates the player file.
    """
    attack_id = "10"
    start_time = "12:00:00"
    end_time = "18:00:00"

    # Run the configuration function
    apply_attack_config(attack_id, model_path, start_time, end_time)

    # Check that the run_GridLab-D.glm file was correctly modified
    run_file = setup_teardown_run_file
    with open(run_file, "r") as f:
        content = f.read()
        assert "object player" in content
        assert 'file "attack_schedule.player";' in content
        assert 'property "Market_1.period"' in content

    # Check that the player file was created
    player_file = os.path.join(model_path, "attack_schedule.player")
    assert os.path.exists(player_file)
    with open(player_file, "r") as f:
        content = f.read()
        assert "2009-07-21 11:59:59 ,300" in content
        assert "2009-07-21 12:00:00 ,60" in content
        assert "2009-07-21 18:00:00 ,300" in content

    # Clean up the player file
    os.remove(player_file)
