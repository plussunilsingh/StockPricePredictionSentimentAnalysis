import pandas as pd
from typing import List
from .signal_engine import SignalEngine

class BacktestEngine:
    """
    Pillar 4: AI Prediction & Reasoning Layer (Data Prep)
    Runs historical data through the baseline rule logic and mathematical labeler.
    Generates the final 'labeled' dataset required for training XGBoost.
    """
    
    def __init__(self):
        self.signal_engine = SignalEngine()
        
    def backtest_and_label(self, historical_data: pd.DataFrame) -> pd.DataFrame:
        """
        historical_data must contain 1-minute intervals with:
        'time', 'spot_close', 'vwap', 'pcr', 'max_pain', 'ce_premium', 'pe_premium'
        """
        if historical_data.empty:
            return historical_data
            
        print(f"[*] Starting Backtest on {len(historical_data)} historical rows...")
        
        # We will append the Label and the Rule-Based Signal to the dataframe
        labels = []
        rule_signals = []
        
        for index, row in historical_data.iterrows():
            # 1. Generate the baseline Rule Signal based on the *current* row
            signal = self.signal_engine.generate_live_signal(
                spot_price=row.get('spot_close', 0),
                vwap=row.get('vwap', 0),
                pcr=row.get('pcr', 0),
                max_pain=row.get('max_pain', 0)
            )
            rule_signals.append(signal["action"])
            
            # 2. Look ahead 15 minutes to mathematically Label the exact outcome
            # Ensure we don't go out of bounds
            if index + 15 < len(historical_data):
                future_row = historical_data.iloc[index + 15]
                
                # Check for stop-loss hit in the 15 min window (simplified)
                window = historical_data.iloc[index:index+15]
                min_spot_in_window = window['spot_close'].min()
                stop_loss_hit = (row['spot_close'] - min_spot_in_window) >= 20 # 20 pt stop loss
                
                label = self.signal_engine.generate_historical_label(
                    entry_spot=row.get('spot_close', 0),
                    current_spot=future_row.get('spot_close', 0),
                    entry_premium=row.get('ce_premium', 100),
                    current_premium=future_row.get('ce_premium', 100),
                    minutes_elapsed=15,
                    stop_loss_hit=stop_loss_hit
                )
                labels.append(label)
            else:
                # Can't look ahead 15 mins for the end of the dataset
                labels.append(0)
                
        historical_data['Rule_Signal'] = rule_signals
        historical_data['AI_Label'] = labels
        
        # Filter to see how many successful trades we labeled
        successes = historical_data[historical_data['AI_Label'] == 1]
        print(f"[*] Backtest Complete. Found {len(successes)} Highly Profitable (Label=1) Setups.")
        
        return historical_data

if __name__ == "__main__":
    # Mock Backtest
    engine = BacktestEngine()
    
    # Create 20 minutes of mock historical data
    mock_data = {
        'time': pd.date_range(start='2024-01-01 09:15', periods=20, freq='1min'),
        'spot_close': [22500 + i*5 for i in range(20)], # steadily rising spot
        'vwap': [22500]*20,
        'pcr': [0.7]*20,
        'max_pain': [22400]*20,
        'ce_premium': [100 + i*3 for i in range(20)], # rising premium
        'pe_premium': [100 - i*2 for i in range(20)]
    }
    
    df = pd.DataFrame(mock_data)
    labeled_df = engine.backtest_and_label(df)
    print("\nSample Labeled Output (Last 5 Rows):")
    print(labeled_df[['spot_close', 'Rule_Signal', 'AI_Label']].tail())
