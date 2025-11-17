from fastapi import FastAPI
from pydantic import BaseModel
import simulation_manager

app = FastAPI()

class SimulationRequest(BaseModel):
    model_name: str
    attack_id: str
    start_time: str
    end_time: str

@app.get("/")
def read_root():
    return {"message": "Welcome to the GridAttackSim API"}

@app.post("/simulations/start")
def start_simulation(request: SimulationRequest):
    model_path = f"Database/{request.model_name}"
    result = simulation_manager.run_simulation(
        model_path, request.attack_id, request.start_time, request.end_time
    )
    return result
