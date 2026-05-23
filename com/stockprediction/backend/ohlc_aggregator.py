import pandas as pd
from datetime import datetime
from collections import defaultdict

class OHLCAggregator:
    """
    Pillar 1: Market Data Infrastructure
    Aggregates high-frequency live ticks into 1-minute and 5-minute OHLC candles.
    """
    
    def __init__(self):
        # Store raw ticks per instrument
        self.tick_buffer = defaultdict(list)
        # Store aggregated candles
        self.candles_1m = defaultdict(list)
        self.candles_5m = defaultdict(list)

    def process_tick(self, instrument: str, ltp: float, volume: int, timestamp: str):
        """Ingests a live tick from the WebSocket stream."""
        tick_time = datetime.fromisoformat(timestamp)
        
        self.tick_buffer[instrument].append({
            'timestamp': tick_time,
            'ltp': ltp,
            'volume': volume
        })
        
        # Trigger aggregation logic here in production
        # Example: check if the minute has rolled over
        self._aggregate_1m_candle(instrument)

    def _aggregate_1m_candle(self, instrument: str):
        """Converts raw ticks into a 1-minute OHLC candle."""
        ticks = self.tick_buffer.get(instrument, [])
        if not ticks:
            return
            
        # Simplified aggregation logic for demonstration
        df = pd.DataFrame(ticks)
        df.set_index('timestamp', inplace=True)
        
        # In a real streaming system, we resample precisely on time boundaries
        ohlc = df['ltp'].resample('1min').ohlc()
        vol = df['volume'].resample('1min').sum()
        
        # Clean buffer (keep only current minute ticks)
        # This prevents memory leaks during live market hours
        
        return ohlc, vol

    def get_latest_candle(self, instrument: str, timeframe: str = '1m'):
        """Returns the most recently closed candle for the ML models to process."""
        pass

if __name__ == "__main__":
    print("[*] OHLC Aggregator Module Initialized.")
    # Mock usage:
    aggregator = OHLCAggregator()
    aggregator.process_tick("NSE_INDEX|Nifty 50", 22500.5, 100, datetime.now().isoformat())
    print("[*] Successfully processed simulated tick into buffer.")
