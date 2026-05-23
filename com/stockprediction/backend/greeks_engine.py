import math
import numpy as np
from scipy.stats import norm

class GreeksEngine:
    """
    Pillar 2: Market Intelligence Engine
    Calculates Options Greeks (Delta, Gamma, Theta, Vega) and Implied Volatility (IV)
    using the Black-Scholes-Merton model.
    """
    
    def __init__(self, risk_free_rate: float = 0.07):
        # 7% risk-free rate is standard for Indian markets
        self.r = risk_free_rate
    
    def _d1_d2(self, S, K, T, r, sigma):
        """Calculate d1 and d2 for Black-Scholes."""
        if T <= 0 or sigma <= 0:
            return 0.0, 0.0
        d1 = (math.log(S / K) + (r + (sigma ** 2) / 2) * T) / (sigma * math.sqrt(T))
        d2 = d1 - sigma * math.sqrt(T)
        return d1, d2
        
    def calculate_greeks(self, S: float, K: float, T: float, sigma: float, option_type: str = "CE"):
        """
        Calculate options Greeks.
        S: Spot Price
        K: Strike Price
        T: Time to Expiry (in years)
        sigma: Implied Volatility (annualized)
        option_type: 'CE' (Call) or 'PE' (Put)
        """
        if T <= 0 or sigma <= 0:
            return {"delta": 0.0, "gamma": 0.0, "theta": 0.0, "vega": 0.0}
            
        d1, d2 = self._d1_d2(S, K, T, self.r, sigma)
        
        # Gamma and Vega are the same for Calls and Puts
        gamma = norm.pdf(d1) / (S * sigma * math.sqrt(T))
        vega = S * norm.pdf(d1) * math.sqrt(T) / 100.0  # Usually expressed per 1% change in IV
        
        if option_type.upper() == "CE":
            delta = norm.cdf(d1)
            theta = (- (S * norm.pdf(d1) * sigma) / (2 * math.sqrt(T)) 
                     - self.r * K * math.exp(-self.r * T) * norm.cdf(d2)) / 365.0
        else:
            delta = norm.cdf(d1) - 1
            theta = (- (S * norm.pdf(d1) * sigma) / (2 * math.sqrt(T)) 
                     + self.r * K * math.exp(-self.r * T) * norm.cdf(-d2)) / 365.0
                     
        return {
            "delta": delta,
            "gamma": gamma,
            "theta": theta,
            "vega": vega
        }
        
    def implied_volatility(self, S: float, K: float, T: float, market_price: float, option_type: str = "CE"):
        """
        Calculate Implied Volatility using Newton-Raphson approximation.
        """
        MAX_ITERATIONS = 100
        PRECISION = 1.0e-5
        
        # Initial guess
        sigma = 0.20 
        
        for i in range(MAX_ITERATIONS):
            d1, d2 = self._d1_d2(S, K, T, self.r, sigma)
            
            if option_type.upper() == "CE":
                price = S * norm.cdf(d1) - K * math.exp(-self.r * T) * norm.cdf(d2)
            else:
                price = K * math.exp(-self.r * T) * norm.cdf(-d2) - S * norm.cdf(-d1)
                
            diff = market_price - price
            
            if abs(diff) < PRECISION:
                return sigma
                
            vega = S * norm.pdf(d1) * math.sqrt(T)
            
            if vega == 0.0:
                break
                
            sigma = sigma + diff / vega
            
            # Keep sigma positive
            if sigma <= 0.0:
                sigma = 0.01
                
        return sigma

if __name__ == "__main__":
    # Test Greeks Engine
    engine = GreeksEngine()
    spot = 22500
    strike = 22500
    expiry_years = 7.0 / 365.0 # 7 days to expiry
    market_price_ce = 150.0
    
    iv = engine.implied_volatility(spot, strike, expiry_years, market_price_ce, "CE")
    greeks = engine.calculate_greeks(spot, strike, expiry_years, iv, "CE")
    
    print(f"[*] Calculated IV: {iv*100:.2f}%")
    print(f"[*] Greeks: {greeks}")
