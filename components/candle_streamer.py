import websocket
import json
import threading

class CandleStreamer:
    def __init__(self, chart_panel, symbol="btcusdt"):
        self.chart = chart_panel
        self.symbol = symbol.lower()
        self.ws = None
        self.is_active = False

    def start(self):
        if self.is_active:
            return
        self.is_active = True

        ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@kline_1m"

        self.ws = websocket.WebSocketApp(
            ws_url,
            on_message=self.on_message,
            on_error=lambda ws, err: print("Candle error:", err),
            on_close=lambda ws, s, m: print("Candle closed"),
            on_open=lambda ws: print(f"Candle stream connected: {self.symbol}")
        )
        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def stop(self):
        self.is_active = False
        if self.ws:
            self.ws.close()
            self.ws = None

    def change_symbol(self, symbol):
        self.stop()
        self.symbol = symbol.lower()
        if self.chart.visible:
            self.start()

    def on_message(self, ws, message):
        if not self.is_active:
            return

        data = json.loads(message)["k"]

        candle = {
            "time": data["t"],
            "open": float(data["o"]),
            "high": float(data["h"]),
            "low": float(data["l"]),
            "close": float(data["c"]),
            "volume": float(data["v"]),
            "is_closed": data["x"]
        }

        self.chart.parent.after(0, self.chart.update_realtime_candle, candle)
