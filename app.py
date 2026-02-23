import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy.stats import norm
from scipy.optimize import least_squares
import os

# Set page config
st.set_page_config(
    page_title="SABR Calibration Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for professional styling
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: #f0f2f6;
        padding: 1rem;
        border-radius: 10px;
        border-left: 4px solid #1f77b4;
    }
    .sidebar-section {
        background: #ffffff;
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border: 1px solid #e1e5e9;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.markdown('<h1 class="main-header">SABR Calibration Dashboard</h1>', unsafe_allow_html=True)

# Load data
@st.cache_data
def load_data():
    """Load the swaption data with calibrated SABR parameters"""
    data_path = "data/processed/swaption_data_with_params.csv"
    if not os.path.exists(data_path):
        st.error(f"Data file not found: {data_path}")
        return None
    
    df = pd.read_csv(data_path)
    
    # Convert Expiry to numeric years
    df['T_expiry'] = df['T_expiry'].astype(float)
    df['Tenor'] = df['Tenor'].astype(float)
    
    return df

# SABR functions from notebook
def calculate_sabr_normal_vol(F, K, T, alpha, rho, nu):
    """Calculate SABR normal volatility"""
    if F == K:
        # ATM Case (K = F)
        sigma_n = alpha * (1 + ((2 - 3 * rho**2) / 24 * nu**2) * T)
    else:
        # OTM Case (K != F)
        zeta = (nu / alpha) * (F - K)
        
        # x_hat(zeta) calculation
        term = np.sqrt(1 - 2 * rho * zeta + zeta**2)
        x_hat_zeta = np.log((term + zeta - rho) / (1 - rho))
        
        # Hagan Normal Volatility Expansion
        sigma_n = alpha * (zeta / x_hat_zeta) * (1 + ((2 - 3 * rho**2) / 24 * nu**2) * T)
    return sigma_n

def calculate_atm_vols(df):
    """Calculate ATM volatilities for all data points"""
    df['ATM Vol'] = df.apply(
        lambda row: calculate_sabr_normal_vol(
            F=row['Forward'], 
            K=row['Forward'], # For ATM Vol, Strike = Forward
            T=row['T_expiry'], 
            alpha=row['alpha'], 
            rho=row['rho'], 
            nu=row['nu']
        ), 
        axis=1
    )
    return df

# Load and process data
df = load_data()

if df is not None:
    # Calculate ATM vols
    df = calculate_atm_vols(df)
    
    # Sidebar for controls
    st.sidebar.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
    st.sidebar.markdown("### 📊 Dashboard Controls")
    
    # Expiry range selection
    available_expiries = sorted(df['T_expiry'].unique())
    selected_expiries = st.sidebar.multiselect(
        "Select Expiries (Years)",
        available_expiries,
        default=available_expiries,
        help="Choose which expiry times to display"
    )
    
    # Tenor range selection
    available_tenors = sorted(df['Tenor'].unique())
    selected_tenors = st.sidebar.multiselect(
        "Select Tenors (Years)",
        available_tenors,
        default=available_tenors,
        help="Choose which swap tenors to display"
    )
    
    # Surface type selection
    surface_types = ['ATM Vol', 'Rho', 'Nu']
    selected_surfaces = st.sidebar.multiselect(
        "Select Surfaces to Display",
        surface_types,
        default=surface_types,
        help="Choose which parameter surfaces to visualize"
    )
    
    st.sidebar.markdown('</div>', unsafe_allow_html=True)
    
    # Filter data based on selections
    if selected_expiries and selected_tenors:
        filtered_df = df[
            (df['T_expiry'].isin(selected_expiries)) & 
            (df['Tenor'].isin(selected_tenors))
        ]
    else:
        filtered_df = df
    
    # Key metrics section
    st.markdown("### 📈 Key Metrics")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.metric("Data Points", len(filtered_df))
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        avg_atm = filtered_df['ATM Vol'].mean() * 10000  # Convert to bps
        st.metric("Avg ATM Vol", f"{avg_atm:.1f} bps")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col3:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        avg_rho = filtered_df['rho'].mean()
        st.metric("Avg Rho", f"{avg_rho:.3f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col4:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        avg_nu = filtered_df['nu'].mean()
        st.metric("Avg Nu", f"{avg_nu:.3f}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Surface plots
    if selected_surfaces:
        st.markdown("### 🎯 Parameter Surfaces")
        
        # Create pivot tables for surfaces
        surface_data = {}
        
        if 'ATM Vol' in selected_surfaces:
            surface_data['ATM Vol'] = filtered_df.pivot(
                index='T_expiry', columns='Tenor', values='ATM Vol'
            )
        
        if 'Rho' in selected_surfaces:
            surface_data['Rho'] = filtered_df.pivot(
                index='T_expiry', columns='Tenor', values='rho'
            )
        
        if 'Nu' in selected_surfaces:
            surface_data['Nu'] = filtered_df.pivot(
                index='T_expiry', columns='Tenor', values='nu'
            )
        
        # Display surfaces in columns
        cols = st.columns(min(len(selected_surfaces), 3))
        
        for i, (surface_name, pivot_table) in enumerate(surface_data.items()):
            with cols[i % 3]:
                # Choose appropriate colorscale
                if surface_name == 'ATM Vol':
                    colorscale = 'Viridis'
                    colorbar_title = 'ATM Normal Vol'
                elif surface_name == 'Rho':
                    colorscale = 'RdBu'
                    colorbar_title = 'SABR Rho'
                else:  # Nu
                    colorscale = 'RdBu'
                    colorbar_title = 'SABR Nu'
                
                # Create surface plot
                fig = go.Figure(data=[go.Surface(
                    z=pivot_table.values,
                    x=pivot_table.columns,
                    y=pivot_table.index,
                    colorscale=colorscale,
                    colorbar_title=colorbar_title,
                    contours_z=dict(show=True, usecolormap=True, highlightcolor="limegreen", project_z=True)
                )])
                
                # Update layout
                fig.update_layout(
                    title=f'{surface_name} Surface',
                    scene=dict(
                        xaxis_title='Swap Tenor (Years)',
                        yaxis_title='Option Expiry (Years)',
                        zaxis_title=colorbar_title,
                        camera=dict(
                            eye=dict(x=1.5, y=1.5, z=1.5)
                        )
                    ),
                    height=500,
                    margin=dict(l=0, r=0, b=0, t=30)
                )
                
                st.plotly_chart(fig, use_container_width=True)
    
    # Data table section
    st.markdown("### 📋 Calibration Data")
    
    # Show summary statistics
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Parameter Statistics**")
        summary_stats = filtered_df[['alpha', 'rho', 'nu', 'ATM Vol']].describe()
        st.dataframe(summary_stats.style.format("{:.4f}"))
    
    with col2:
        st.markdown("**Sample Data Points**")
        sample_data = filtered_df[['Expiry', 'Tenor', 'Forward', 'alpha', 'rho', 'nu', 'ATM Vol']].head(10)
        st.dataframe(sample_data.style.format({
            'Forward': "{:.4f}",
            'alpha': "{:.4f}",
            'rho': "{:.4f}",
            'nu': "{:.4f}",
            'ATM Vol': "{:.4f}"
        }))
    
    # Insights section
    st.markdown("### 💡 Market Insights")
    
    # Calculate rolldown/rollup for rho and nu
    insights_df = filtered_df.copy().sort_values(['Tenor', 'T_expiry'])
    insights_df['rho_roll'] = insights_df.groupby('Tenor')['rho'].diff() / insights_df.groupby('Tenor')['T_expiry'].diff()
    insights_df['nu_roll'] = insights_df.groupby('Tenor')['nu'].diff() / insights_df.groupby('Tenor')['T_expiry'].diff()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Rho Dynamics**")
        most_rolldown_rho = insights_df.loc[insights_df['rho_roll'].idxmin()]
        most_rollup_rho = insights_df.loc[insights_df['rho_roll'].idxmax()]
        
        st.write(f"📉 Most Rho Rolldown: {most_rolldown_rho['T_expiry']:.1f}y expiry, {most_rolldown_rho['Tenor']:.1f}y tenor")
        st.write(f"📈 Most Rho Rollup: {most_rollup_rho['T_expiry']:.1f}y expiry, {most_rollup_rho['Tenor']:.1f}y tenor")
    
    with col2:
        st.markdown("**Nu Dynamics**")
        most_rolldown_nu = insights_df.loc[insights_df['nu_roll'].idxmin()]
        most_rollup_nu = insights_df.loc[insights_df['nu_roll'].idxmax()]
        
        st.write(f"📉 Most Nu Rolldown: {most_rolldown_nu['T_expiry']:.1f}y expiry, {most_rolldown_nu['Tenor']:.1f}y tenor")
        st.write(f"📈 Most Nu Rollup: {most_rollup_nu['T_expiry']:.1f}y expiry, {most_rollup_nu['Tenor']:.1f}y tenor")

else:
    st.error("Unable to load data. Please check the data file path.")

# Footer
st.markdown("---")
st.markdown("🏦 SABR Calibration Dashboard | Built with Streamlit & Plotly")
