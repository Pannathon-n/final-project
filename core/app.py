import tkinter as tk
from config.theme import DarkTheme
from core.preferences import PreferencesManager
from components.ticker import CryptoTicker
from components.chart import ChartPanel
from components.orderbook import OrderBookPanel
from components.trades import RecentTradesPanel

class DashboardApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Binance Real-Time Dashboard - Professional Edition")
        self.root.geometry("1400x900")
        self.root.configure(bg=DarkTheme.BG)

        self.prefs = PreferencesManager()

        self.available_cryptos = [
            ("btcusdt", "BTC/USDT"),
            ("ethusdt", "ETH/USDT"),
            ("bnbusdt", "BNB/USDT"),
            ("solusdt", "SOL/USDT"),
            ("adausdt", "ADA/USDT"),
            ("xrpusdt", "XRP/USDT")
        ]

        self.tickers = {}

        main_container = tk.Frame(root, bg=DarkTheme.BG)
        main_container.pack(fill=tk.BOTH, expand=True)

        control_frame = tk.Frame(main_container, bg=DarkTheme.CARD_BG, 
                                relief="solid", borderwidth=1, 
                                highlightbackground=DarkTheme.BORDER, highlightthickness=1)
        control_frame.pack(fill=tk.X, padx=10, pady=10)

        control_inner = tk.Frame(control_frame, bg=DarkTheme.CARD_BG)
        control_inner.pack(padx=10, pady=10, fill=tk.X)

        tk.Label(control_inner, text="Dashboard Controls", 
                font=("Arial", 14, "bold"), bg=DarkTheme.CARD_BG, fg=DarkTheme.FG).pack(side=tk.LEFT, padx=10)

        # Panel toggles
        self.chart_btn = tk.Button(control_inner, text="📊 Chart", 
                                   command=self.toggle_chart,
                                   bg=DarkTheme.ACCENT, fg=DarkTheme.FG,
                                   activebackground=DarkTheme.BLUE,
                                   relief="raised", padx=10, pady=5)
        self.chart_btn.pack(side=tk.LEFT, padx=5)

        self.orderbook_btn = tk.Button(control_inner, text="📖 Order Book", 
                                       command=self.toggle_orderbook,
                                       bg=DarkTheme.ACCENT, fg=DarkTheme.FG,
                                       activebackground=DarkTheme.BLUE,
                                       relief="raised", padx=10, pady=5)
        self.orderbook_btn.pack(side=tk.LEFT, padx=5)

        self.trades_btn = tk.Button(control_inner, text="💱 Trades", 
                                    command=self.toggle_trades,
                                    bg=DarkTheme.ACCENT, fg=DarkTheme.FG,
                                    activebackground=DarkTheme.BLUE,
                                    relief="raised", padx=10, pady=5)
        self.trades_btn.pack(side=tk.LEFT, padx=5)

        self.status_label = tk.Label(control_inner, text="Status: Active", 
                                     font=("Arial", 10), bg=DarkTheme.CARD_BG, fg=DarkTheme.FG)
        self.status_label.pack(side=tk.RIGHT, padx=10)

        ticker_control = tk.Frame(main_container, bg=DarkTheme.CARD_BG,
                                 relief="solid", borderwidth=1,
                                 highlightbackground=DarkTheme.BORDER,
                                 highlightthickness=1)
        ticker_control.pack(fill=tk.X, padx=10, pady=5)

        tk.Label(ticker_control, text="Select Cryptocurrencies",
                font=("Arial", 10, "bold"), bg=DarkTheme.CARD_BG, 
                fg=DarkTheme.FG).pack(anchor=tk.W, padx=10, pady=(10, 5))

        ticker_inner = tk.Frame(ticker_control, bg=DarkTheme.CARD_BG)
        ticker_inner.pack(padx=10, pady=(0, 10), fill=tk.X)

        self.ticker_vars = {}
        for symbol, display_name in self.available_cryptos:
            var = tk.BooleanVar(value=symbol in self.prefs.prefs['visible_tickers'])
            self.ticker_vars[symbol] = var
            cb = tk.Checkbutton(ticker_inner, text=display_name, variable=var,
                               command=self.update_tickers,
                               bg=DarkTheme.CARD_BG, fg=DarkTheme.FG,
                               selectcolor=DarkTheme.ACCENT,
                               activebackground=DarkTheme.CARD_BG,
                               activeforeground=DarkTheme.FG,
                               font=("Arial", 9),
                               borderwidth=0,
                               highlightthickness=0)
            cb.pack(side=tk.LEFT, padx=10)

        self.ticker_frame = tk.Frame(main_container, bg=DarkTheme.BG)
        self.ticker_frame.pack(fill=tk.X, padx=10, pady=5)

        self.data_container = tk.Frame(main_container, bg=DarkTheme.BG)
        self.data_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.chart_container = tk.Frame(self.data_container, bg=DarkTheme.BG)
        self.orderbook_container = tk.Frame(self.data_container, bg=DarkTheme.BG)
        self.trades_container = tk.Frame(self.data_container, bg=DarkTheme.BG)

        self.chart = ChartPanel(self.chart_container)
        self.orderbook = OrderBookPanel(self.orderbook_container)
        self.trades = RecentTradesPanel(self.trades_container)

        self.update_tickers()

        if self.prefs.prefs['chart_visible']:
            self.toggle_chart()
        if self.prefs.prefs['orderbook_visible']:
            self.toggle_orderbook()
        if self.prefs.prefs['trades_visible']:
            self.toggle_trades()

    def update_tickers(self):
        visible = [symbol for symbol, var in self.ticker_vars.items() if var.get()]
        
        for symbol in list(self.tickers.keys()):
            if symbol not in visible:
                self.tickers[symbol].stop()
                self.tickers[symbol].hide()
                del self.tickers[symbol]

        for symbol in visible:
            if symbol not in self.tickers:
                display_name = next(name for s, name in self.available_cryptos if s == symbol)
                ticker = CryptoTicker(self.ticker_frame, symbol, display_name)
                ticker.pack(side=tk.LEFT, padx=10, pady=5)
                ticker.start()
                self.tickers[symbol] = ticker

        self.prefs.prefs['visible_tickers'] = visible
        self.prefs.save()

    def toggle_chart(self):
        if self.chart.visible:
            self.chart.hide()
            self.chart_container.pack_forget()
            self.chart_btn.config(text="📊 Chart")
        else:
            self.chart_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            self.chart.show()
            self.chart_btn.config(text="📊 Chart ✓")
        
        self.prefs.prefs['chart_visible'] = self.chart.visible
        self.prefs.save()
        self.update_status()

    def toggle_orderbook(self):
        if self.orderbook.visible:
            self.orderbook.hide()
            self.orderbook_container.pack_forget()
            self.orderbook_btn.config(text="📖 Order Book")
        else:
            self.orderbook_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            self.orderbook.show()
            self.orderbook_btn.config(text="📖 Order Book ✓")
        
        self.prefs.prefs['orderbook_visible'] = self.orderbook.visible
        self.prefs.save()
        self.update_status()

    def toggle_trades(self):
        if self.trades.visible:
            self.trades.hide()
            self.trades_container.pack_forget()
            self.trades_btn.config(text="💱 Trades")
        else:
            self.trades_container.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            self.trades.show()
            self.trades_btn.config(text="💱 Trades ✓")
        
        self.prefs.prefs['trades_visible'] = self.trades.visible
        self.prefs.save()
        self.update_status()

    def update_status(self):
        active_panels = []
        if self.chart.visible:
            active_panels.append("Chart")
        if self.orderbook.visible:
            active_panels.append("OrderBook")
        if self.trades.visible:
            active_panels.append("Trades")
        
        status = f"Active: {len(self.tickers)} Tickers"
        if active_panels:
            status += f" | {', '.join(active_panels)}"
        
        self.status_label.config(text=status)

    def on_closing(self):
        print("Shutting down dashboard...")
        
        for ticker in self.tickers.values():
            ticker.stop()
        
        self.chart.streamer.stop()
        self.orderbook.stop()
        self.trades.stop()
        
        self.prefs.save()
        
        print("Shutdown complete")
        self.root.destroy()

