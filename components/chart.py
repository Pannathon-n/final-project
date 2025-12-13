import tkinter as tk
from tkinter import ttk
import requests
import matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from config.theme import DarkTheme
from components.candle_streamer import CandleStreamer

class ChartPanel:
    def __init__(self, parent):
        self.parent = parent
        self.frame = tk.Frame(parent, bg=DarkTheme.CARD_BG)
        self.visible = False
        self.current_symbol = "btcusdt"

        padding_frame = tk.Frame(self.frame, bg=DarkTheme.CARD_BG)
        padding_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        control_frame = tk.Frame(padding_frame, bg=DarkTheme.CARD_BG)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(control_frame, text="Chart Symbol:", font=("Arial", 10, "bold"),
                bg=DarkTheme.CARD_BG, fg=DarkTheme.FG).pack(side=tk.LEFT, padx=5)
        
        self.symbol_var = tk.StringVar(value="btcusdt")
        self.symbol_combo = ttk.Combobox(control_frame, textvariable=self.symbol_var, 
                                         values=["btcusdt", "ethusdt", "bnbusdt", "solusdt", "adausdt", "xrpusdt"],
                                         state="readonly", width=15)
        self.symbol_combo.pack(side=tk.LEFT, padx=5)
        self.symbol_combo.bind("<<ComboboxSelected>>", self.change_symbol)

        self.fig = Figure(figsize=(10, 6), dpi=100, facecolor=DarkTheme.CARD_BG)
        self.ax_price = self.fig.add_subplot(2, 1, 1, facecolor=DarkTheme.ACCENT)
        self.ax_vol = self.fig.add_subplot(2, 1, 2, facecolor=DarkTheme.ACCENT)

        self.canvas = FigureCanvasTkAgg(self.fig, master=padding_frame)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.configure(bg=DarkTheme.CARD_BG)

        self.times = []
        self.opens = []
        self.highs = []
        self.lows = []
        self.closes = []
        self.volumes = []

        self.streamer = CandleStreamer(self)

    def change_symbol(self, event=None):
        """Change the symbol being displayed"""
        new_symbol = self.symbol_var.get()
        if new_symbol != self.current_symbol:
            self.current_symbol = new_symbol
            self.fetch_initial_data()
            self.draw_chart()
            self.streamer.change_symbol(new_symbol)

    def fetch_initial_data(self):
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": self.current_symbol.upper(), "interval": "1m", "limit": 100}
        data = requests.get(url, params=params).json()

        self.times = [c[0] for c in data]
        self.opens = [float(c[1]) for c in data]
        self.highs = [float(c[2]) for c in data]
        self.lows  = [float(c[3]) for c in data]
        self.closes = [float(c[4]) for c in data]
        self.volumes = [float(c[5]) for c in data]

    def update_realtime_candle(self, c):
        if not self.times:
            return

        if c["time"] == self.times[-1]:
            self.highs[-1] = c["high"]
            self.lows[-1] = c["low"]
            self.closes[-1] = c["close"]
            self.volumes[-1] = c["volume"]
        else:
            self.times.append(c["time"])
            self.opens.append(c["open"])
            self.highs.append(c["high"])
            self.lows.append(c["low"])
            self.closes.append(c["close"])
            self.volumes.append(c["volume"])

            self.times = self.times[-100:] 
            self.opens = self.opens[-100:]
            self.highs = self.highs[-100:]
            self.lows = self.lows[-100:]
            self.closes = self.closes[-100:]
            self.volumes = self.volumes[-100:]

        if self.visible:
            self.draw_chart()

    def draw_chart(self):
        self.ax_price.clear()
        self.ax_vol.clear()

        self.ax_price.set_facecolor(DarkTheme.ACCENT)
        self.ax_vol.set_facecolor(DarkTheme.ACCENT)

        for i in range(len(self.closes)):
            o = self.opens[i]
            h = self.highs[i]
            l = self.lows[i]
            c = self.closes[i]

            color = DarkTheme.GREEN if c >= o else DarkTheme.RED
            self.ax_price.plot([i, i], [l, h], color=DarkTheme.FG, linewidth=0.5)
            self.ax_price.add_patch(
                matplotlib.patches.Rectangle(
                    (i - 0.3, min(o, c)),
                    0.6,
                    abs(o - c) if abs(o - c) > 0 else 0.5,
                    color=color
                )
            )

        self.ax_price.set_title(f"{self.current_symbol.upper()} 1-Minute Candlestick Chart", 
                               fontsize=12, fontweight='bold', color=DarkTheme.FG)
        self.ax_price.set_ylabel("Price (USDT)", color=DarkTheme.FG)
        self.ax_price.tick_params(colors=DarkTheme.FG)
        self.ax_price.grid(True, alpha=0.2, color=DarkTheme.FG)
        self.ax_price.set_xticks([])
        self.ax_price.spines['bottom'].set_color(DarkTheme.BORDER)
        self.ax_price.spines['top'].set_color(DarkTheme.BORDER)
        self.ax_price.spines['left'].set_color(DarkTheme.BORDER)
        self.ax_price.spines['right'].set_color(DarkTheme.BORDER)

        colors = [DarkTheme.GREEN if self.closes[i] >= self.opens[i] else DarkTheme.RED
                  for i in range(len(self.closes))]
        self.ax_vol.bar(range(len(self.volumes)), self.volumes, color=colors, width=0.8)
        self.ax_vol.set_ylabel("Volume", color=DarkTheme.FG)
        self.ax_vol.tick_params(colors=DarkTheme.FG)
        self.ax_vol.grid(True, alpha=0.2, color=DarkTheme.FG)
        self.ax_vol.spines['bottom'].set_color(DarkTheme.BORDER)
        self.ax_vol.spines['top'].set_color(DarkTheme.BORDER)
        self.ax_vol.spines['left'].set_color(DarkTheme.BORDER)
        self.ax_vol.spines['right'].set_color(DarkTheme.BORDER)

        self.fig.tight_layout()
        self.canvas.draw()

    def show(self):
        self.visible = True
        self.fetch_initial_data()
        self.draw_chart()
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.canvas_widget.pack(fill=tk.BOTH, expand=True)
        self.streamer.start()

    def hide(self):
        self.visible = False
        self.streamer.stop()
        self.frame.pack_forget()