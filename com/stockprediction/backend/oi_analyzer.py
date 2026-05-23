from typing import Dict, List
import pandas as pd

class OIAnalyzer:
    """
    Pillar 2: Market Intelligence Engine
    Analyzes Open Interest (OI) buildup, calculates Live Put-Call Ratio (PCR),
    and maps strike concentrations.
    """
    
    def __init__(self):
        self.live_chain = {}
        self.total_ce_oi = 0
        self.total_pe_oi = 0
        self.pcr = 0.0

    def process_chain_snapshot(self, chain_data: List[dict]):
        """
        Processes a live option chain snapshot to calculate OI metrics.
        chain_data: List of dictionaries containing strike, CE_OI, PE_OI
        """
        self.total_ce_oi = 0
        self.total_pe_oi = 0
        
        for item in chain_data:
            strike = item.get("strike", 0)
            ce_oi = item.get("CE_OI", 0)
            pe_oi = item.get("PE_OI", 0)
            
            self.live_chain[strike] = {
                "CE_OI": ce_oi,
                "PE_OI": pe_oi
            }
            
            self.total_ce_oi += ce_oi
            self.total_pe_oi += pe_oi
            
        self._calculate_pcr()

    def _calculate_pcr(self):
        """Calculates global Put-Call Ratio (PCR)."""
        if self.total_ce_oi > 0:
            self.pcr = self.total_pe_oi / self.total_ce_oi
        else:
            self.pcr = 0.0
            
    def get_max_pain_strike(self) -> float:
        """
        Calculates the 'Max Pain' strike where option buyers lose the most money.
        (Simplified estimation based on highest total OI concentration).
        """
        if not self.live_chain:
            return 0.0
            
        max_oi = 0
        max_pain_strike = 0
        
        for strike, data in self.live_chain.items():
            total_strike_oi = data["CE_OI"] + data["PE_OI"]
            if total_strike_oi > max_oi:
                max_oi = total_strike_oi
                max_pain_strike = strike
                
        return max_pain_strike

    def analyze_sentiment(self) -> str:
        """
        Interprets market sentiment based purely on PCR.
        """
        if self.pcr > 1.2:
            return "BEARISH (Heavy Call Writing)"
        elif self.pcr < 0.8:
            return "BULLISH (Heavy Put Writing)"
        else:
            return "NEUTRAL"

if __name__ == "__main__":
    # Test OI Analyzer
    analyzer = OIAnalyzer()
    mock_data = [
        {"strike": 22400, "CE_OI": 50000, "PE_OI": 150000},
        {"strike": 22500, "CE_OI": 80000, "PE_OI": 120000},
        {"strike": 22600, "CE_OI": 200000, "PE_OI": 40000},
    ]
    
    analyzer.process_chain_snapshot(mock_data)
    
    print(f"[*] Live PCR: {analyzer.pcr:.2f}")
    print(f"[*] Market Sentiment: {analyzer.analyze_sentiment()}")
    print(f"[*] Max Pain Strike: {analyzer.get_max_pain_strike()}")
