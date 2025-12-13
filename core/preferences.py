import pickle
import os

class PreferencesManager:
    def __init__(self, filename="dashboard_prefs.pkl"):
        self.filename = filename
        self.prefs = self.load()

    def load(self):
        if os.path.exists(self.filename):
            try:
                with open(self.filename, 'rb') as f:
                    return pickle.load(f)
            except:
                pass
        return {
            'visible_tickers': ['btcusdt', 'ethusdt', 'solusdt', 'bnbusdt', 'adausdt'],
            'chart_visible': False,
            'orderbook_visible': False,
            'trades_visible': False
        }

    def save(self):
        try:
            with open(self.filename, 'wb') as f:
                pickle.dump(self.prefs, f)
        except Exception as e:
            print(f"Error saving preferences: {e}")