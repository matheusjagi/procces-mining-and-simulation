# Process Mining with PM4PY 🚀

![Process Mining](https://img.shields.io/badge/Process-Mining-blue?style=flat-square) ![Python](https://img.shields.io/badge/Python-3.8+-yellow?style=flat-square) ![PM4PY](https://img.shields.io/badge/PM4PY-2.7.9-orange?style=flat-square)

Welcome to **Process Mining with PM4PY**, a project focused on analyzing and simulating manufacturing processes using process mining techniques! This repository contains code to perform Monte Carlo simulations, critical path analysis, and performance evaluation on production data using the `pm4py` library. 📊

## 📋 Project Overview

This project aims to:
- **Discover Process Models**: Use the Inductive Miner to extract a Petri Net from production event logs.
- **Simulate Processes**: Run Monte Carlo simulations to analyze process behavior, including average case duration, number of activities per case, and rejection rates.
- **Identify Bottlenecks**: Perform critical path analysis to find the longest paths in the process and pinpoint performance bottlenecks.
- **Visualize Results**: Generate histograms and scatter plots to visualize simulation outcomes.

The project was developed as part of a Master's research at IFES (2024) under the guidance of Mateus Conrad. 🎓

---

## 🛠️ Installation

Follow these steps to set up the project on your local machine.

### Prerequisites
- Python 3.8 or higher 🐍
- Git installed
- A virtual environment (recommended)

### Steps
1. **Clone the Repository**:
   ```bash
   git clone https://github.com/seu-usuario/nome-do-repositorio.git
   cd nome-do-repositorio
   ```

2. **Set Up a Virtual Environment** (optional but recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   The project requires `pm4py` and other Python libraries. Install them using `pip`:
   ```bash
   pip install -r requirements.txt
   ```
   If you don't have a `requirements.txt`, install the required packages manually:
   ```bash
   pip install pm4py pandas numpy matplotlib
   ```

4. **Prepare Your Data**:
   - Place your production data CSV file in the `data/` folder.
   - The expected format is similar to `production_data.csv` with columns: `Case ID`, `Activity`, `Start Timestamp`, `Complete Timestamp`, `Span`, `Resource`, `Part Desc.`, `Qty Completed`, `Qty Rejected`, `Work Order Qty`.

---

## 🚀 Usage

### Running the Simulation
The main script (`src/main.py`) performs the entire process mining pipeline:
- Loads the event log from a CSV file.
- Discovers a Petri Net using the Inductive Miner.
- Runs Monte Carlo simulations to generate synthetic logs.
- Analyzes critical paths and performance metrics.
- Generates visualizations (histograms and scatter plots).

To run the simulation:
```bash
python src/main.py
```

### Outputs
The script generates the following outputs:
- **Petri Net Visualization**: Saved as `outcomes/petri_net_visualization.png`.
- **Simulated Logs**: Saved in `outcomes/simulations/` as `.xes` and `.csv` files for each simulation run.
- **Monte Carlo Results**: Summary statistics saved in `outcomes/monte_carlo_results.csv`.
- **Critical Paths**: Analysis of the longest paths and slowest activity transitions in `outcomes/critical_paths.txt`.
- **Visualizations**: Histograms and scatter plots saved as `outcomes/monte_carlo_visualizations.png`.

---

## 📈 Results

Here are some highlights from the latest Monte Carlo simulations (20 runs):

- **Average Case Duration**: ~45,438.76 minutes (~31.6 days)
- **Average Number of Activities per Case**: ~16.88 activities
- **Rejection Rate**: ~0.0771% (highly efficient process in terms of quality)

For detailed results, check the `outcomes/monte_carlo_results.csv` file and the visualizations in `outcomes/monte_carlo_visualizations.png`.

---

## 🧠 Key Features

- **Monte Carlo Simulations**: Simulates process behavior to analyze variability in case duration, activity count, and rejection rates.
- **Critical Path Analysis**: Identifies the longest paths in the process using performance spectrum analysis.
- **Performance Metrics**: Evaluates process efficiency with metrics like average case duration and rejection rate.
- **Visualizations**: Generates histograms for case duration and activity count, plus a scatter plot to correlate the two metrics.

---

## 📂 Project Structure

```
nome-do-repositorio/
│
├── data/                       # Folder for input data (e.g., production_data.csv)
├── outcomes/                   # Folder for output files (Petri Nets, simulated logs, results)
│   ├── simulations/            # Simulated logs for each Monte Carlo run
│   ├── petri_net_model.pnml    # Exported Petri Net model
│   ├── petri_net_visualization.png  # Petri Net visualization
│   ├── monte_carlo_results.csv # Monte Carlo simulation results
│   ├── monte_carlo_visualizations.png  # Histograms and scatter plots
│   └── critical_paths.txt      # Critical path analysis
├── src/                        # Source code
│   └── main.py                 # Main script for process mining and simulation
├── .gitignore                  # Files and folders to ignore (e.g., data/, outcomes/)
└── README.md                   # Project documentation (this file)
```

---

## 🤝 Contributing

Contributions are welcome! If you'd like to contribute:
1. Fork the repository.
2. Create a new branch (`git checkout -b feature/nova-funcionalidade`).
3. Make your changes and commit them (`git commit -m "Adicionando nova funcionalidade"`).
4. Push to your branch (`git push origin feature/nova-funcionalidade`).
5. Open a Pull Request on GitHub.

---

## 📧 Contact

For questions or feedback, feel free to reach out:
- **Author**: Matheus Jagi
- **Email**: matheus.jagi@gmail.com
- **Advisor**: Mateus Conrad

---

⭐ If you find this project useful, give it a star on GitHub! ⭐