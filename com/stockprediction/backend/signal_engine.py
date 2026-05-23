class SignalEngine:
    """
    Pillar 5: Decision & Signal Engine
    Generates deterministic, rule-based signals before AI enhancement.
    Implements the exact Label logic requested for historical backtesting and live scoring.
    """
    
    def __init__(self):
        self.active_signals = {}
        
    def generate_live_signal(self, spot_price: float, vwap: float, pcr: float, max_pain: float) -> dict:
        """
        Baseline deterministic logic for Live Market.
        Checks for a breakout condition to initiate a trade.
        """
        signal = {"action": "HOLD", "confidence": 0, "reasoning": []}
        
        # Bullish Breakout Rule
        if spot_price > vwap and pcr < 0.8 and spot_price > max_pain:
            signal["action"] = "BUY_CE"
            signal["confidence"] = 80
            signal["reasoning"] = [
                f"Spot ({spot_price}) > VWAP ({vwap})",
                f"Bullish PCR ({pcr})",
                f"Spot > Max Pain ({max_pain})"
            ]
            
        # Bearish Breakdown Rule
        elif spot_price < vwap and pcr > 1.2 and spot_price < max_pain:
            signal["action"] = "BUY_PE"
            signal["confidence"] = 80
            signal["reasoning"] = [
                f"Spot ({spot_price}) < VWAP ({vwap})",
                f"Bearish PCR ({pcr})",
                f"Spot < Max Pain ({max_pain})"
            ]
            
        return signal

    def generate_historical_label(self, entry_spot: float, current_spot: float, 
                                  entry_premium: float, current_premium: float, 
                                  minutes_elapsed: int, stop_loss_hit: bool) -> int:
        """
        Exact Mathematical Labeling for AI Training Data.
        Label = 1 IF:
        - NIFTY moves +40 points within 15 mins
        - AND option premium increases > 20%
        - AND move occurs before stop-loss threshold
        """
        spot_moved = (current_spot - entry_spot) >= 40
        premium_increased = (current_premium - entry_premium) / entry_premium > 0.20
        within_time = minutes_elapsed <= 15
        
        if spot_moved and premium_increased and within_time and not stop_loss_hit:
            return 1
        return 0

if __name__ == "__main__":
    engine = SignalEngine()
    print("[*] Testing Live Baseline Rule:")
    print(engine.generate_live_signal(spot_price=22550, vwap=22500, pcr=0.7, max_pain=22400))
    
    print("\n[*] Testing Exact Mathematical Labeling (Backtesting/Training):")
    label = engine.generate_historical_label(
        entry_spot=22500, current_spot=22545,
        entry_premium=100, current_premium=125,
        minutes_elapsed=12, stop_loss_hit=False
    )
    print(f"Generated Label: {label} (Expected 1)")
