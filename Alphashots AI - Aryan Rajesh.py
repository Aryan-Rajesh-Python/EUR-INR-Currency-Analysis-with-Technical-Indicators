import pandas as pd
import numpy as np
import yfinance as yf
import streamlit as st
import matplotlib.pyplot as plt

# Function to calculate indicators
def calculate_indicators(data, sma_window=7):
    data['1-Day Simple Moving Average'] = data['Close'].rolling(window=1).mean()
    data['7-Day Simple Moving Average'] = data['Close'].rolling(window=sma_window).mean()
    
    rolling_std = data['Close'].rolling(window=sma_window).std().squeeze()
    data['Bollinger Upper Band'] = data['7-Day Simple Moving Average'] + (rolling_std * 2)
    data['Bollinger Lower Band'] = data['7-Day Simple Moving Average'] - (rolling_std * 2)
    
    data['CCI'] = (data['Close'] - data['Close'].rolling(window=20).mean()) / (0.015 * data['Close'].rolling(window=20).std())
    
    return data

# Enhanced function to generate specific decisions for each indicator
def get_indicator_decision(indicator, latest_data, historical_data):
    close_price = latest_data['Close'].item()
    upper_band = latest_data['Bollinger Upper Band'].item()
    lower_band = latest_data['Bollinger Lower Band'].item()
    cci = latest_data['CCI'].item()
    sma_1day = latest_data['1-Day Simple Moving Average'].item()  
    sma_7day_current = latest_data['7-Day Simple Moving Average'].item()
    
    if len(historical_data) > 1:
        sma_7day_previous = historical_data['7-Day Simple Moving Average'].iloc[-2]  
        sma_1day_previous = historical_data['1-Day Simple Moving Average'].iloc[-2]  
    else:
        sma_7day_previous = sma_7day_current
        sma_1day_previous = sma_1day

    decision = 'NEUTRAL'

    # 1-Day SMA Decision Logic
    if indicator == '1-Day SMA':
        if close_price > sma_7day_current:
            decision = 'BUY'
        elif close_price < sma_7day_current:
            decision = 'SELL'
    
    # 7-Day SMA Decision Logic
    elif indicator == '7-Day SMA':
        if sma_1day > sma_7day_current and sma_1day_previous <= sma_7day_previous:
            decision = 'BUY' 
        elif sma_1day < sma_7day_current and sma_1day_previous >= sma_7day_previous:
            decision = 'SELL'

    # Bollinger Bands Decision Logic
    if indicator == 'Close Price':
        if close_price < lower_band:
            decision = 'BUY'
        elif close_price > upper_band:
            decision = 'SELL'
    elif indicator == 'Bollinger Upper Band':
        if close_price > upper_band:
            decision = 'SELL'
        elif close_price > (upper_band - (upper_band - lower_band) / 2):
            decision = 'SELL'
    elif indicator == 'Bollinger Lower Band':
        if close_price < lower_band:
            decision = 'BUY'
        elif close_price < (lower_band + (upper_band - lower_band) / 2):
            decision = 'BUY'
    
    # CCI Decision Logic
    elif indicator == 'CCI':
        if cci > 100:
            decision = 'SELL' 
        elif cci < -100:
            decision = 'BUY' 
        elif 50 < cci <= 100:
            decision = 'SELL'
        elif -100 <= cci < -50:
            decision = 'BUY'

    return decision

# Streamlit app layout
st.title("Currency Data Analysis App")
st.markdown("This app retrieves currency data and calculates technical indicators.")

# Sidebar for user inputs
st.sidebar.header("User Input Parameters")
sma_window = st.sidebar.slider("SMA Window", min_value=1, max_value=30, value=7)
bollinger_window = st.sidebar.slider("Bollinger Band Window", min_value=5, max_value=30, value=7)
ticker_symbol = st.sidebar.text_input("Enter the ticker symbol (e.g., EURINR=X):", "EURINR=X")
start_date = st.sidebar.date_input("Start date", value=pd.to_datetime("2023-01-01"))
end_date = st.sidebar.date_input("End date", value=pd.to_datetime("2024-01-01"))

# Validate dates
if end_date < start_date:
    st.error("End date must be after the start date.")
else:
    @st.cache_data
    def get_data(ticker, start, end):
        data = yf.download(ticker, start=start, end=end, progress=False)
        return data

    data = get_data(ticker_symbol, start_date, end_date)

    if data.empty:
        st.error("No data found for the given ticker symbol. Please try again.")
    else:
        st.write("### Data Head:")
        st.dataframe(data.head())

        data = calculate_indicators(data, sma_window=sma_window)

        st.write("### Data with Indicators:")
        st.dataframe(data[['Close', '1-Day Simple Moving Average', '7-Day Simple Moving Average', 
                           'Bollinger Upper Band', 'Bollinger Lower Band', 'CCI']].tail())

        latest_data = data.iloc[-1]  
        indicator_decisions = pd.DataFrame({
            'Indicator': ['1-Day SMA', '7-Day SMA', 'Bollinger Upper Band', 'Bollinger Lower Band', 'CCI'],
        })
        indicator_decisions['Decision'] = indicator_decisions['Indicator'].apply(lambda x: get_indicator_decision(x, latest_data, data))

        # Display color-coded Indicator Decisions Table
        st.write("### Indicator Decisions Table:")
        def color_decision(val):
            color = 'green' if val == 'BUY' else 'red' if val == 'SELL' else 'grey'
            return f'background-color: {color}'
        st.dataframe(indicator_decisions.style.applymap(color_decision, subset=['Decision']))

        # Display Indicator Summary for recent trends
        def indicator_summary(data, period='7D'):
            summary = {}
            recent_data = data.last(period)
            sma_trend = 'Increasing' if recent_data['7-Day Simple Moving Average'].iloc[-1] > recent_data['7-Day Simple Moving Average'].iloc[0] else 'Decreasing'
            cci_latest = recent_data['CCI'].iloc[-1]
            cci_trend = 'Overbought' if cci_latest > 100 else 'Oversold' if cci_latest < -100 else 'Neutral'
            summary['SMA Trend'] = sma_trend
            summary['CCI Trend'] = cci_trend
            return pd.DataFrame(summary, index=[0])

        st.write("### Indicator Summary (Recent Trends):")
        st.dataframe(indicator_summary(data, '7D'))

        # Original Matplotlib Plotting
        if st.button("Plot Data"):
            plt.figure(figsize=(14, 10))

            plt.subplot(2, 1, 1)
            plt.plot(data.index, data['Close'], label='Close Price', color='blue', alpha=0.5)
            plt.plot(data.index, data['7-Day Simple Moving Average'], label='7-Day SMA', color='orange')
            plt.plot(data.index, data['Bollinger Upper Band'], label='Bollinger Upper Band', color='red', linestyle='--')
            plt.plot(data.index, data['Bollinger Lower Band'], label='Bollinger Lower Band', color='green', linestyle='--')
            plt.title(f'{ticker_symbol} Price and Bollinger Bands')
            plt.xlabel('Date')
            plt.ylabel('Price')
            plt.legend()

            plt.subplot(2, 1, 2)
            plt.plot(data.index, data['CCI'], label='CCI', color='purple')
            plt.axhline(y=100, color='red', linestyle='--', linewidth=1)
            plt.axhline(y=-100, color='green', linestyle='--', linewidth=1)
            plt.title(f'{ticker_symbol} Commodity Channel Index (CCI)')
            plt.xlabel('Date')
            plt.ylabel('CCI')
            plt.legend()
            st.pyplot(plt)
