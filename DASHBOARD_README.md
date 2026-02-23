# SABR Calibration Dashboard

A professional Streamlit dashboard for visualizing SABR model calibration results with interactive 3D surface plots.

## Features

- **Interactive 3D Surface Plots**: Visualize ATM Volatility, Rho, and Nu parameter surfaces
- **Dynamic Filtering**: Select specific expiry and tenor combinations via sidebar controls
- **Real-time Metrics**: View key calibration statistics and market insights
- **Professional UI**: Clean, modern interface with custom styling
- **Data Analysis**: Automatic calculation of rolldown/rollup dynamics

## Quick Start

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Dashboard**:
   ```bash
   streamlit run app.py
   ```

3. **Access the Dashboard**:
   Open your browser and navigate to `http://localhost:8501`

## Dashboard Components

### Sidebar Controls
- **Expiry Selection**: Choose which option expiry times to display
- **Tenor Selection**: Choose which swap tenors to display  
- **Surface Selection**: Toggle between ATM Vol, Rho, and Nu surfaces

### Main Dashboard
- **Key Metrics**: Average volatilities and parameters
- **3D Surface Plots**: Interactive parameter surfaces with rotation/zoom
- **Data Tables**: Summary statistics and sample data points
- **Market Insights**: Automatic detection of rolldown/rollup extremes

## Data Requirements

The dashboard expects a CSV file at `data/processed/swaption_data_with_params.csv` with the following columns:
- `Expiry`: Option expiry (e.g., "3m", "1y")
- `Tenor`: Swap tenor in years
- `T_expiry`: Expiry in years (numeric)
- `Forward`: Forward rate
- `alpha`, `rho`, `nu`: Calibrated SABR parameters

## Technical Details

- Built with Streamlit 1.39.0
- Plotly 5.20.0 for 3D visualizations
- Responsive design with custom CSS styling
- Cached data loading for performance
- Real-time filtering and surface generation

## Troubleshooting

- **Data not found**: Ensure `swaption_data_with_params.csv` exists in `data/processed/`
- **Import errors**: Run `pip install -r requirements.txt` to install dependencies
- **Port conflicts**: Streamlit will automatically find an available port if 8501 is occupied
