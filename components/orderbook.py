import tkinter as tk
from tkinter import ttk
import websocket
import json
import threading
from config.theme import DarkTheme

class OrderBookPanel:
    def __init__(self, parent, symbol="btcusdt"):
        self.parent = parent
        self.symbol = symbol.lower()
        self.frame = tk.Frame(parent, relief="solid", borderwidth=1, 
                             bg=DarkTheme.CARD_BG, highlightbackground=DarkTheme.BORDER,
                             highlightthickness=1)
        self.visible = False
        self.ws = None
        self.is_active = False

        # Add padding
        padding_frame = tk.Frame(self.frame, bg=DarkTheme.CARD_BG)
        padding_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Title with symbol selector
        title_frame = tk.Frame(padding_frame, bg=DarkTheme.CARD_BG)
        title_frame.pack(fill=tk.X)
        
        tk.Label(title_frame, text="Order Book", 
                font=("Arial", 12, "bold"), bg=DarkTheme.CARD_BG, fg=DarkTheme.FG).pack()
        
        self.symbol_var = tk.StringVar(value=symbol)
        self.symbol_combo = ttk.Combobox(title_frame, textvariable=self.symbol_var, 
                                         values=["btcusdt", "ethusdt", "bnbusdt", "solusdt", "adausdt", "xrpusdt"],
                                         state="readonly", width=12)
        self.symbol_combo.pack(pady=5)
        self.symbol_combo.bind("<<ComboboxSelected>>", self.change_symbol)

        # Create style for dark treeview
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Dark.Treeview",
                       background=DarkTheme.ACCENT,
                       foreground=DarkTheme.FG,
                       fieldbackground=DarkTheme.ACCENT,
                       borderwidth=0)
        style.configure("Dark.Treeview.Heading",
                       background=DarkTheme.CARD_BG,
                       foreground=DarkTheme.FG,
                       borderwidth=1)
        style.map('Dark.Treeview', background=[('selected', DarkTheme.BLUE)])

        # Create treeview for order book
        columns = ("Price", "Amount", "Total")
        
        tk.Label(padding_frame, text="ASKS (Sell Orders)", 
                font=("Arial", 10, "bold"), foreground=DarkTheme.RED,
                bg=DarkTheme.CARD_BG).pack(pady=(10,5))
        
        self.asks_tree = ttk.Treeview(padding_frame, columns=columns, show="headings", 
                                      height=10, style="Dark.Treeview")
        for col in columns:
            self.asks_tree.heading(col, text=col)
            self.asks_tree.column(col, width=100)
        self.asks_tree.pack()

        tk.Label(padding_frame, text="BIDS (Buy Orders)", 
                font=("Arial", 10, "bold"), foreground=DarkTheme.GREEN,
                bg=DarkTheme.CARD_BG).pack(pady=(10,5))
        
        self.bids_tree = ttk.Treeview(padding_frame, columns=columns, show="headings", 
                                      height=10, style="Dark.Treeview")
        for col in columns:
            self.bids_tree.heading(col, text=col)
            self.bids_tree.column(col, width=100)
        self.bids_tree.pack()

    def change_symbol(self, event=None):
        new_symbol = self.symbol_var.get()
        if new_symbol != self.symbol:
            self.symbol = new_symbol
            if self.is_active:
                self.stop()
                self.start()

    def start(self):
        if self.is_active:
            return
        self.is_active = True

        ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@depth10@100ms"

        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self.on_message,
            on_error=lambda ws, err: print(f"OrderBook error:", err),
            on_close=lambda ws, s, m: print(f"OrderBook closed"),
            on_open=lambda ws: print(f"OrderBook connected: {self.symbol}")
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
        bids = data["bids"][:10]  
        asks = data["asks"][:10]  

        self.parent.after(0, self.update_display, bids, asks)

    def update_display(self, bids, asks):
        if not self.is_active:
            return

        for item in self.asks_tree.get_children():
            self.asks_tree.delete(item)
        for item in self.bids_tree.get_children():
            self.bids_tree.delete(item)

        for ask in reversed(asks):
            price = float(ask[0])
            amount = float(ask[1])
            total = price * amount
            self.asks_tree.insert("", 0, values=(f"{price:.2f}", f"{amount:.4f}", f"{total:.2f}"))

        for bid in bids:
            price = float(bid[0])
            amount = float(bid[1])
            total = price * amount
            self.bids_tree.insert("", tk.END, values=(f"{price:.2f}", f"{amount:.4f}", f"{total:.2f}"))

    def show(self):
        self.visible = True
        self.frame.pack(fill=tk.BOTH, expand=True)
        self.start()

    def hide(self):
        self.visible = False
        self.stop()
        self.frame.pack_forget()