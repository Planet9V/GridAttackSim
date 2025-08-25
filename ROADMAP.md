# GridAttackSim Development Roadmap

This document outlines the planned improvements and future features for the GridAttackSim framework. The roadmap is divided into three main phases, with the initial focus on improving the core user experience before adding major new functionality.

---

## Phase 1: Foundational UI/UX Overhaul

This phase addresses the most critical user experience issues to modernize the application and provide a solid platform for future development.

### 1.1: Asynchronous Simulation Execution (Responsiveness)
- **Problem:** The user interface currently freezes and becomes unresponsive while a simulation is running.
- **Solution:** Refactor the simulation execution logic to run in a separate background thread. This will keep the GUI responsive, allowing the user to interact with other parts of the application (like the AI Research tool) while a simulation is in progress.

### 1.2: Real-time GUI Feedback
- **Problem:** The user has no visibility into the simulation's progress beyond a simple "running" message.
- **Solution:** Implement a real-time feedback system in the main GUI. This will include:
    - A **progress bar** to provide a visual indication of the simulation's advancement.
    - An **embedded log window** that displays status updates and key events from the `attack_broker.py` script as they happen.

### 1.3: UI Modernization (Aesthetics & Scalability)
- **Problem:** The UI, built with standard `tkinter`, looks dated and is not organized to scale well as new features are added.
- **Solution:**
    - **Aesthetics:** Migrate from standard `tkinter` widgets to the `tkinter.ttk` themed widgets to give the application a more modern look and feel across different operating systems.
    - **Scalability:** Reorganize the main window into a **tabbed interface**. This will create logical separation for different functions (e.g., "Simulation Setup", "Batch Runner", "Results Analysis"), preventing clutter and making the application easier to navigate.

---

## Phase 2: Core Feature Enhancements

With a modern and stable UI, this phase will focus on delivering powerful new capabilities to enhance the framework's research and analysis value.

### 2.1: Advanced Interactive Visualization
- **Problem:** The current result charts are static images.
- **Solution:** Replace the existing `plot_result.py` script with a more powerful, interactive plotting library (e.g., Plotly, Bokeh). This will allow users to zoom, pan, hover for data points, and select/deselect data series directly within the charts.

### 2.2: Real-Time Monitoring Dashboard
- **Problem:** All analysis happens after the simulation is complete.
- **Solution:** Building on the asynchronous execution from Phase 1, create a new "Live Monitor" tab. This dashboard will poll key output files or use a message queue to display critical metrics (e.g., total load, market price, network latency) on live-updating charts as the simulation runs.

### 2.3: GUI-Based Parameter Sweeping
- **Problem:** The powerful batch runner feature is only accessible via the command line.
- **Solution:** Create a user-friendly interface for parameter sweeping. This will allow a user to select a model parameter (e.g., `delay_cluster`), define a range of values (e.g., 100ms to 1000ms in 100ms steps), and have the application automatically generate the configuration and run the batch simulation.

---

## Phase 3: Ecosystem and Deployment Improvements

This phase focuses on improving the end-to-end user and developer experience, from installation to long-term data management.

### 3.1: Simplified Dependency Management (Dockerization)
- **Problem:** The installation process for all external dependencies (FNCS, ns-3, GridLAB-D) is complex, error-prone, and a major barrier to entry.
- **Solution:** Create a `Dockerfile` and a Docker Compose configuration. This will encapsulate the entire environment and installation process into a single, distributable image, allowing a new user to get started with a simple `docker run` command.

### 3.2: Results Management Database
- **Problem:** Simulation results are stored as individual CSV files, which are difficult to manage, query, and compare over time.
- **Solution:** Integrate a lightweight database (e.g., SQLite) into the application. The framework will automatically log the parameters and key output metrics of every simulation run to this database. A new UI section will allow users to browse, filter, and select historical runs for analysis and comparison.
