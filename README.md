# SABR Model Calibration & Volatility Surface Analysis

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-success)

## 📌 Project Overview

This repository contains a robust Python implementation for calibrating the **SABR (Stochastic Alpha, Beta, Rho)** model to interest rate swaption data.

The project was developed to "reverse engineer" market views on volatility by fitting the SABR parameters to observed option prices across a grid of Expiries (3m to 10y) and Tenors (1y to 30y). The result is a fully calibrated volatility surface that captures the market's smile (skew) and convexity (vol of vol).

### Key Features
* **Data Pipeline:** Automated extraction and "tidying" of raw market matrices (Forwards, Annuities, Straddles, Risk Reversals) from Excel into clean CSVs.
* **Calibration Engine:** Uses `scipy.optimize` to minimize the Sum of Squared Errors (SSE) between market prices and Bachelier (Normal) model prices.
* **Visualization:** Generates 3D interaction surfaces for $\alpha$ (ATM Vol), $\rho$ (Skew), and $\nu$ (Vol of Vol) to analyze term structure rolldown.

---

## 📉 The Mathematics: Normal SABR Model
The calibration relies on the asymptotic expansion derived by **Hagan et al. (2002)** for the Normal SABR model.

The implied normal volatility $\sigma_N(K)$ is approximated as:

$$
\sigma_N(K) = \alpha \frac{z}{\chi(z)} \cdot \Bigg\{ 1 + \Bigg[ \frac{2-3\rho^2}{24}\nu^2 \Bigg] T \Bigg\}
$$

Where:
* $z = \frac{\nu}{\alpha} (F - K)$
* $\chi(z) = \ln \left( \frac{\sqrt{1 - 2\rho z + z^2} + z - \rho}{1 - \rho} \right)$

**The Parameters:**
1.  **$\alpha$ (Alpha):** The level of at-the-money (ATM) volatility.
2.  **$\rho$ (Rho):** The correlation between the asset price and volatility (Controls the **Skew**).
3.  **$\nu$ (Nu):** The volatility of volatility (Controls the **Smile/Wings**).

---

## 🛠️ Repository Structure

```text
SABR-Calibration-Project/
│
├── data/
│   ├── raw/                  # Original market data (Excel)
│   └── processed/            # Cleaned "Tidy" CSV data
│
├── notebooks/
│   ├── 01_Data_Cleaning.ipynb    # ETL pipeline: Matrix -> Tidy Format
│   └── 02_SABR_Calibration.ipynb # Main calibration loop & Plotting
│
├── src/                      # (Optional) Modularized Python scripts
│   ├── sabr_formula.py       # Hagan approximation functions
│   └── optimization.py       # Error minimization logic
│
├── images/                   # Generated 3D Surface plots
│   ├── alpha_surface.png
│   ├── rho_surface.png
│   └── nu_surface.png
│
├── requirements.txt          # Dependencies
└── README.md                 # Project Documentation