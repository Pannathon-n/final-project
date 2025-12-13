import tkinter as tk
import websocket
import json
import threading
from config.theme import DarkTheme

class CryptoTicker:
    def __init__(self, parent, symbol, display_name):
        self.parent = parent
        self.symbol = symbol.lower()
        self.display_name = display_name
        self.is_active = False
        self.ws = None

        self.frame = tk.Frame(parent, relief="solid", borderwidth=1, 
                             bg=DarkTheme.CARD_BG, highlightbackground=DarkTheme.BORDER,
                             highlightthickness=1)

        padding_frame = tk.Frame(self.frame, bg=DarkTheme.CARD_BG)
        padding_frame.pack(padx=15, pady=15, fill=tk.BOTH, expand=True)

        self.title_label = tk.Label(
            padding_frame, text=display_name, font=("Arial", 12, "bold"),
            bg=DarkTheme.CARD_BG, fg=DarkTheme.FG
        )
        self.title_label.pack()

        self.price_label = tk.Label(
            padding_frame, text="--,---", font=("Arial", 36, "bold"), 
            bg=DarkTheme.CARD_BG, fg=DarkTheme.FG
        )
        self.price_label.pack(pady=5)

        tk.Label(padding_frame, text="USDT", font=("Arial", 10),
                bg=DarkTheme.CARD_BG, fg=DarkTheme.FG).pack()

        self.change_label = tk.Label(padding_frame, text="--", font=("Arial", 10),
                                     bg=DarkTheme.CARD_BG, fg=DarkTheme.FG)
        self.change_label.pack(pady=3)

        self.volume_label = tk.Label(padding_frame, text="Vol: --", font=("Arial", 9),
                                     bg=DarkTheme.CARD_BG, fg=DarkTheme.FG)
        self.volume_label.pack(pady=2)

        self.high_low_label = tk.Label(padding_frame, text="H: -- | L: --", font=("Arial", 8),
                                       bg=DarkTheme.CARD_BG, fg=DarkTheme.FG)
        self.high_low_label.pack()

    def start(self):
        """Start WebSocket streaming."""
        if self.is_active:
            return

        self.is_active = True
        ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@ticker"

        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self.on_message,
            on_error=lambda ws, err: print(f"{self.symbol} error:", err),
            on_close=lambda ws, s, m: print(f"{self.symbol} closed"),
            on_open=lambda ws: print(f"{self.symbol} connected"),
        )

        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def stop(self):
        """Stop WebSocket connection."""
        self.is_active = False
        if self.ws:
            self.ws.close()
            self.ws = None

    def on_message(self, ws, message):
        if not self.is_active:
            return

        data = json.loads(message)
        price = float(data["c"])
        change = float(data["p"])
        percent = float(data["P"])
        volume = float(data["v"])
        high = float(data["h"])
        low = float(data["l"])

        self.parent.after(
            0, self.update_display, price, change, percent, volume, high, low
        )

    def update_display(self, price, change, percent, volume, high, low):
        if not self.is_active:
            return

        color = DarkTheme.GREEN if change >= 0 else DarkTheme.RED
        self.price_label.config(text=f"{price:,.2f}", fg=color, bg=DarkTheme.CARD_BG)

        sign = "+" if change >= 0 else ""
        self.change_label.config(
            text=f"{sign}{change:,.2f} ({sign}{percent:.2f}%)",
            foreground=color,
            background=DarkTheme.CARD_BG
        )

        if volume >= 1_000_000:
            vol_str = f"{volume/1_000_000:.2f}M"
        elif volume >= 1_000:
            vol_str = f"{volume/1_000:.2f}K"
        else:
            vol_str = f"{volume:.2f}"
        
        self.volume_label.config(text=f"Vol: {vol_str} USDT", bg=DarkTheme.CARD_BG)
        self.high_low_label.config(text=f"H: {high:,.2f} | L: {low:,.2f}", bg=DarkTheme.CARD_BG)

    def pack(self, **kwargs):
        self.frame.pack(**kwargs)

    def hide(self):
        self.frame.pack_forget()