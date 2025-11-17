from fastapi.testclient import TestClient
from main import app
from unittest.mock import patch

client = TestClient(app)

@patch("simulation_manager.run_simulation")
def test_start_simulation(mock_run_simulation):
    # Arrange
    mock_run_simulation.return_value = {"status": "success", "message": "Simulation finished successfully"}
    payload = {
        "model_name": "13_Nodes_73_Houses",
        "attack_id": "1",
        "start_time": "12:00:00",
        "end_time": "18:00:00",
    }

    # Act
    response = client.post("/simulations/start", json=payload)

    # Assert
    assert response.status_code == 200
    assert response.json() == {"status": "success", "message": "Simulation finished successfully"}
    mock_run_simulation.assert_called_once_with(
        "Database/13_Nodes_73_Houses", "1", "12:00:00", "18:00:00"
    )
