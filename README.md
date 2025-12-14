# Crypto Dashboard 

A **professional, real-time cryptocurrency trading dashboard** built with **Python + Tkinter**, using **Binance WebSocket & REST APIs**.  
This project displays **live prices, candlestick charts, order books, and recent trades** with a modern dark-themed UI.

---

##  Features

### 🔹 Real-Time Market Data
- Live price updates via **Binance WebSocket**
- Supports multiple trading pairs (BTC, ETH, BNB, SOL, ADA, XRP)

### 🔹 Interactive Ticker Cards
- Large price display
- 24h price change (%)
- Volume, high, and low
- Color-coded price movement (green/red)

### 🔹 Advanced Panels (Toggleable)
-  **Candlestick Chart (1m timeframe)**
-  **Order Book (Top 10 bids/asks)**
-  **Recent Trades (Live stream)**

### 🔹 UI & UX
- Dark theme
- Select which tickers to display
- Panel visibility is remembered between sessions
- Responsive layout

### 🔹 Persistent Preferences
- Saves visible tickers
- Remembers open panels (Chart / Order Book / Trades)
- Auto-restores on next launch

---

##  Project Structure
crypto_dashboard/\
│\
├── main.py # Application entry point\
│\
├── config/\
│ └── theme.py # Dark theme configuration\
│\
├── core/\
│ ├── app.py # Main dashboard application\
│ └── preferences.py # Persistent preferences manager\
│\
├── components/\
│ ├── ticker.py # Crypto price ticker cards\
│ ├── chart.py # Candlestick chart panel\
│ ├── candle_streamer.py # Real-time candle WebSocket\
│ ├── orderbook.py # Order book panel\
│ └── trades.py # Recent trades panel\
│\
├── requirements.txt\
└── README.md\

# Known Bugs / Issues
 Order Book Panel Cropped

Issue:
The Order Book panel may appear cropped or partially hidden, especially when multiple panels (Chart, Trades, Order Book) are enabled at the same time.