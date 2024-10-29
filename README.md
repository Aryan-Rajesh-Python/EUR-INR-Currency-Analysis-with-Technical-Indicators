# EUR/INR Currency Analysis with Technical Indicators

## Overview
This project implements a comprehensive analysis of the EUR/INR currency pair using technical indicators. The analysis includes calculations for Moving Averages, Bollinger Bands, and the Commodity Channel Index (CCI) over specified timeframes. The aim is to generate actionable trading decisions based on these indicators, aiding in informed currency trading.

## Project Components
- **Data Retrieval:** Scrapes EUR/INR currency data from Yahoo Finance for the period of January 1, 2023, to September 30, 2024.
- **Technical Analysis:** Calculates:
  - 1-Day and 7-Day Simple Moving Averages (SMA)
  - Bollinger Bands
  - Commodity Channel Index (CCI)
- **Decision Making:** Provides BUY, SELL, or NEUTRAL signals based on the indicators' outcomes.
- **Visualization:** Displays graphs for a visual representation of the metrics and their corresponding trading decisions.

## Requirements
- Python 3.x
- Libraries: `pandas`, `numpy`, `yfinance`, `streamlit`, `matplotlib`

## Usage

   ```bash
   git clone https://github.com/Aryan-Rajesh-Python/EUR-INR-Currency-Analysis-with-Technical-Indicators.git
   pip install -r requirements.txt
   streamlit run alphashots.py
