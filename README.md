
# GridAttackSim: Smart Grid Attack Simulation Framework

**Note:** This project is currently undergoing a major architectural refactoring. The original GUI-based application is being deprecated in favor of a modern, API-driven backend to support the development of a real-time, interactive "Cyber-Physical Grid Range."

GridAttackSim is a framework that makes it possible to simulate
various cyber-attacks on the smart grid infrastructure and visualize
their consequences. GridAttackSim uses a co-simulation approach, and
it is based on a combination of [GridLAB-D](https://www.gridlabd.org),
[ns-3](https://www.nsnam.org), and
[FNCS](https://github.com/FNCS).

## Installation

GridAttackSim was developed and tested exclusively using the Ubuntu
16.04 LTS operating system; either a physical host or a virtual
machine installation can be used. Other Linux OSes may work, but have
not been tested, nor has this software been tested on Windows.

To run GridAttackSim, you have to first install and configure the
three external components, FNCS, ns-3, and GridLAB-D. For details,
please consult our [Installation Guide](/installation_guide.md).

Once the external components are installed, you can install the required Python packages:

```bash
pip install -r requirements.txt
```

## Quick Start (API Backend)

The new version of GridAttackSim runs as a backend API service.

1. Use a terminal window to navigate to the GridAttackSim directory.

2. Start the backend service using Uvicorn:

   ```bash
   uvicorn main:app --reload
   ```

   The API will be available at `http://127.0.0.1:8000`.

3. You can interact with the API using a tool like `curl` or by visiting the interactive documentation at `http://127.0.0.1:8000/docs`.

   To start a simulation, you can send a POST request to the `/simulations/start` endpoint:

   ```bash
   curl -X POST "http://127.0.0.1:8000/simulations/start" -H "Content-Type: application/json" -d '{
     "model_name": "13_Nodes_73_Houses",
     "attack_id": "1",
     "start_time": "12:00:00",
     "end_time": "18:00:00"
   }'
   ```

## References

For a research background regarding GridAttackSim, please refer to the
following papers:
1. T. D. Le, A. Anwar, S. W. Loke, R. Beuran, Y. Tan, "GridAttackSim:
   Cyber Attack Simulation Framework for Smart Grids", MDPI
   Electronics, Special Issue on Applications of IoT for Microgrids,
   vol. 9, no. 8, August
   2020, 1218. [https://doi.org/10.3390/electronics9081218]
2. T. D. Le, A. Anwar, R. Beuran, S. W. Loke, "Smart Grid
   Co-Simulation Tools: Review and Cybersecurity Case Study", 7th
   International Conference on Smart Grid (icSmartGrid 2019),
   Newcastle, Australia, December 9-11, 2019,
   pp. 39-45. [https://ieeexplore.ieee.org/abstract/document/8990712]

For a list of contributors to this project, check the file
CONTRIBUTORS included with the source code.
