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
    run_file = os.path.join(model_path, "run_ns-3.cc")
    original_file = os.path.join(model_path, "ns-3.cc")

    if os.path.exists(run_file):
        os.remove(run_file)

    shutil.copyfile(original_file, run_file)

    yield run_file

    if os.path.exists(run_file):
        os.remove(run_file)

def test_ns3_attack_scheduling(model_path, setup_teardown_run_file):
    """
    Tests that the ns-3 attack scheduling logic correctly injects the C++ code.
    """
    attack_id = "1"
    start_time = "12:00:00"
    end_time = "18:00:00"

    # Run the configuration function
    apply_attack_config(attack_id, model_path, start_time, end_time)

    # Check that the run_ns-3.cc file was correctly modified
    run_file = setup_teardown_run_file
    with open(run_file, "r") as f:
        content = f.read()
        assert "Simulator::Schedule(Seconds(43200.0), &SetAttackParameters);" in content
        assert "Simulator::Schedule(Seconds(64800.0), &SetNormalParameters);" in content
