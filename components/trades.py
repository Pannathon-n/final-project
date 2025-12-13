import tkinter as tk
from tkinter import ttk
import websocket
import json
import threading
from datetime import datetime
from config.theme import DarkTheme

class RecentTradesPanel:
    def __init__(self, parent, symbol="btcusdt"):
        self.parent = parent
        self.symbol = symbol.lower()
        self.frame = tk.Frame(parent, relief="solid", borderwidth=1,
                             bg=DarkTheme.CARD_BG, highlightbackground=DarkTheme.BORDER,
                             highlightthickness=1)
        self.visible = False
        self.ws = None
        self.is_active = False

        padding_frame = tk.Frame(self.frame, bg=DarkTheme.CARD_BG)
        padding_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        title_frame = tk.Frame(padding_frame, bg=DarkTheme.CARD_BG)
        title_frame.pack(fill=tk.X)
        
        tk.Label(title_frame, text="Recent Trades", 
                font=("Arial", 12, "bold"), bg=DarkTheme.CARD_BG, fg=DarkTheme.FG).pack()
        
        self.symbol_var = tk.StringVar(value=symbol)
        self.symbol_combo = ttk.Combobox(title_frame, textvariable=self.symbol_var, 
                                         values=["btcusdt", "ethusdt", "bnbusdt", "solusdt", "adausdt", "xrpusdt"],
                                         state="readonly", width=12)
        self.symbol_combo.pack(pady=5)
        self.symbol_combo.bind("<<ComboboxSelected>>", self.change_symbol)

        # Create treeview for trades
        columns = ("Time", "Price", "Amount", "Type")
        
        self.trades_tree = ttk.Treeview(padding_frame, columns=columns, show="headings", 
                                        height=25, style="Dark.Treeview")
        self.trades_tree.heading("Time", text="Time")
        self.trades_tree.heading("Price", text="Price")
        self.trades_tree.heading("Amount", text="Amount")
        self.trades_tree.heading("Type", text="Type")
        
        self.trades_tree.column("Time", width=80)
        self.trades_tree.column("Price", width=100)
        self.trades_tree.column("Amount", width=100)
        self.trades_tree.column("Type", width=60)
        
        self.trades_tree.pack(fill=tk.BOTH, expand=True)

        # Configure tags for colors
        self.trades_tree.tag_configure('buy', foreground=DarkTheme.GREEN)
        self.trades_tree.tag_configure('sell', foreground=DarkTheme.RED)

    def change_symbol(self, event=None):
        new_symbol = self.symbol_var.get()
        if new_symbol != self.symbol:
            self.symbol = new_symbol
            for item in self.trades_tree.get_children():
                self.trades_tree.delete(item)
            if self.is_active:
                self.stop()
                self.start()

    def start(self):
        if self.is_active:
            return
        self.is_active = True

        ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@trade"

        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self.on_message,
            on_error=lambda ws, err: print(f"Trades error:", err),
            on_close=lambda ws, s, m: print(f"Trades closed"),
            on_open=lambda ws: print(f"Trades connected: {self.symbol}")
        )
        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def stop(self):
        self.is_active = False
        if self.ws:
            self.ws.close()
            self.ws = None

    def on_message(self, ws, message):
        if not self.is_active:
            return

        data = json.loads(message)
        trade = {
            'time': datetime.fromtimestamp(data['T'] / 1000).strftime('%H:%M:%S'),
            'price': float(data['p']),
            'amount': float(data['q']),
            'is_buyer_maker': data['m']
        }

        self.parent.after(0, self.add_trade, trade)

    def add_trade(self, trade):
        if not self.is_active:
            return

        trade_type = "SELL" if trade['is_buyer_maker'] else "BUY"
        tag = 'sell' if trade['is_buyer_maker'] else 'buy'

        self.trades_tree.insert("", 0, 
            values=(trade['time'], f"{trade['price']:.2f}", 
                   f"{trade['amount']:.4f}", trade_type),
            tags=(tag,))

        children = self.trades_tree.get_children()
        if len(children) > 100:
            self.trades_tree.delete(children[-1])

    def show(self):
        self.visible = True
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.start()

    def hide(self):
        self.visible = False
        self.stop()
        self.frame.pack_forget()