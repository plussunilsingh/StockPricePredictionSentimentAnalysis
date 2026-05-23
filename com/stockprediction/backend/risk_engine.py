class RiskEngine:
    """
    Pillar 3: Risk Management Layer
    Validates trade signals before execution. Protects capital by filtering out 
    low-liquidity strikes, massive spreads, and enforcing Max Daily Loss.
    """
    
    def __init__(self, max_daily_loss: float = 10000.0, max_spread_pct: float = 0.05):
        self.max_daily_loss = max_daily_loss
        self.max_spread_pct = max_spread_pct
        self.current_daily_pnl = 0.0
        
    def check_trade_validity(self, option_data: dict, current_pnl: float) -> dict:
        """
        Runs the trade through the risk gauntlet.
        option_data must contain: 'ltp', 'bid', 'ask', 'volume'
        """
        self.current_daily_pnl = current_pnl
        
        # 1. Max Loss Check
        if self.current_daily_pnl <= -self.max_daily_loss:
            return {"valid": False, "reason": "Max Daily Loss Reached. System Halted."}
            
        # 2. Liquidity / Volume Check
        volume = option_data.get("volume", 0)
        if volume < 5000:
            return {"valid": False, "reason": "Low Liquidity. Spread risk too high."}
            
        # 3. Bid-Ask Spread Check
        bid = option_data.get("bid", 0)
        ask = option_data.get("ask", 0)
        
        if bid > 0 and ask > 0:
            spread_pct = (ask - bid) / bid
            if spread_pct > self.max_spread_pct:
                return {"valid": False, "reason": f"Spread too high ({spread_pct*100:.1f}%). Exceeds {self.max_spread_pct*100}% limit."}
                
        return {"valid": True, "reason": "Risk checks passed."}

if __name__ == "__main__":
    engine = RiskEngine()
    test_option = {"ltp": 100, "bid": 98, "ask": 105, "volume": 12000}
    # Spread is (105-98)/98 = ~7.1%, which is > 5% limit
    print(engine.check_trade_validity(test_option, -5000))
