Feature Definition: Dynamic Portfolio & Technical Analysis Dashboard
Project Objective
To build a lightweight, fully interactive web application that allows a user to monitor a 116-stock portfolio, visualize historical price action, and dynamically apply standard technical indicators for market analysis.

Target User
Individual retail investors managing mid-to-large private portfolios who need quick, visual insights without the clutter of complex, institutional trading platforms.

1. Core Functionalities
Portfolio Navigation & Selection: * Provide an intuitive UI (e.g., dropdown menus, search bars) to quickly select and view any of the 116 configured stock tickers.

Dynamic Data Acquisition: * Automatically fetch historical Open, High, Low, Close, and Volume (OHLCV) market data on demand for the selected asset.

Interactive Charting: * Render financial charts (candlesticks) that support user interactions including zooming, panning, and hovering over data points to read exact price/date values.

Technical Indicator Overlays: * Allow the user to dynamically toggle and configure key financial indicators directly on the price chart:
* Moving Averages (Simple and Exponential)
* Bollinger Bands
* Fibonacci Retracement levels
* Relative Strength Index (RSI)

2. Technical Architecture & Stack
This application will be built entirely in Python using a data-focused, declarative stack to minimize frontend overhead.

Application Framework: Streamlit

Purpose: Handles the web interface, routing, and interactive UI widgets (sliders, dropdowns, toggles) without requiring HTML, CSS, or JavaScript.

Data Pipeline: yfinance

Purpose: Serves as the primary data provider, pulling reliable daily-interval OHLCV data directly from Yahoo Finance.

Quantitative Engine: pandas-ta (Pandas Technical Analysis)

Purpose: Extends standard Pandas dataframes to calculate technical indicators (EMA, Bollinger Bands, RSI) efficiently with minimal custom math.

Visualization Engine: Plotly (plotly.graph_objects)

Purpose: Renders the dynamic, interactive HTML-based charts that embed seamlessly into the Streamlit frontend.

Interactive Prototype
To give you an idea of the kind of user experience you can build for her using these tools, here is a functional prototype of a financial dashboard. You can toggle the moving averages and Bollinger Bands to see how they overlay on the price action.
