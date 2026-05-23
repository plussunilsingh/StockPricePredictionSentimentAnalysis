import pandas as pd
from typing import Dict, List

class OptionsChainParser:
    """
    Pillar 1 & 2: Market Data Infrastructure & Options Intelligence
    Parses real-time options chain data to extract Open Interest (OI), Volume, 
    and Last Traded Price (LTP) for specific strike prices.
    """
    
    def __init__(self, underlying_symbol: str = "NIFTY"):
        self.underlying_symbol = underlying_symbol
        # Store live chain data
        self.live_chain: Dict[float, Dict[str, dict]] = {}
        self.put_call_ratio = 0.0

    def ingest_chain_snapshot(self, raw_chain_data: List[dict]):
        """
        Processes a raw snapshot of the options chain.
        Expects a list of dictionaries containing strike, call_oi, put_oi, etc.
        """
        total_ce_oi = 0
        total_pe_oi = 0
        
        for strike_data in raw_chain_data:
            strike = strike_data.get("strikePrice")
            ce_data = strike_data.get("CE", {})
            pe_data = strike_data.get("PE", {})
            
            self.live_chain[strike] = {
                "CE": {
                    "LTP": ce_data.get("lastPrice", 0),
                    "OI": ce_data.get("openInterest", 0),
                    "Volume": ce_data.get("totalTradedVolume", 0)
                },
                "PE": {
                    "LTP": pe_data.get("lastPrice", 0),
                    "OI": pe_data.get("openInterest", 0),
                    "Volume": pe_data.get("totalTradedVolume", 0)
                }
            }
            
            total_ce_oi += ce_data.get("openInterest", 0)
            total_pe_oi += pe_data.get("openInterest", 0)
            
        # Calculate market-wide Put-Call Ratio
        if total_ce_oi > 0:
            self.put_call_ratio = total_pe_oi / total_ce_oi
            
    def get_atm_strike(self, spot_price: float) -> float:
        """Finds the At-The-Money (ATM) strike price based on the spot."""
        if not self.live_chain:
            return 0.0
        strikes = list(self.live_chain.keys())
        # Return the strike closest to the spot price
        return min(strikes, key=lambda x: abs(x - spot_price))

    def get_strike_data(self, strike: float) -> dict:
        """Returns the specific CE and PE data for a strike."""
        return self.live_chain.get(strike, {})

if __name__ == "__main__":
    print("[*] Options Chain Parser Initialized.")
    # Mock usage:
    parser = OptionsChainParser("NIFTY")
    mock_data = [
        {"strikePrice": 22400, "CE": {"lastPrice": 150, "openInterest": 50000}, "PE": {"lastPrice": 50, "openInterest": 120000}},
        {"strikePrice": 22500, "CE": {"lastPrice": 100, "openInterest": 80000}, "PE": {"lastPrice": 100, "openInterest": 80000}},
        {"strikePrice": 22600, "CE": {"lastPrice": 50, "openInterest": 150000}, "PE": {"lastPrice": 150, "openInterest": 40000}},
    ]
    parser.ingest_chain_snapshot(mock_data)
    print(f"[*] Parsed Data for 22500 Strike: {parser.get_strike_data(22500)}")
    print(f"[*] Current Put-Call Ratio (PCR): {parser.put_call_ratio:.2f}")
