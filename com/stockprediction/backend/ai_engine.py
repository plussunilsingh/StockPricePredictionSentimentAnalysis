import xgboost as xgb
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

class AIEngine:
    """
    Pillar 4: AI Prediction Layer
    Trains an XGBoost classifier locally to score the baseline Rule-Based Signals.
    Outputs a Probability Score (0 to 1) for a successful breakout.
    """
    def __init__(self):
        self.model = xgb.XGBClassifier(
            objective='binary:logistic',
            eval_metric='logloss',
            learning_rate=0.05,
            max_depth=6,
            n_estimators=100
        )
        self.is_trained = False
        
    def train(self, labeled_data: pd.DataFrame):
        """
        Trains the XGBoost model on the engineered feature set.
        Target variable is 'AI_Label' (1 = Profitable, 0 = Loss/Flat).
        """
        print("[*] Initiating AI Training Sequence...")
        
        # Features: Greeks, PCR, VWAP distance, Spot
        features = ['spot_close', 'vwap', 'pcr', 'max_pain', 'ce_premium', 'pe_premium']
        
        # Check if we have the necessary columns
        missing = [f for f in features if f not in labeled_data.columns]
        if missing:
            print(f"[!] Cannot train. Missing features: {missing}")
            return
            
        X = labeled_data[features]
        y = labeled_data['AI_Label']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)
        
        print(f"[*] Training on {len(X_train)} samples, validating on {len(X_test)} samples...")
        self.model.fit(X_train, y_train)
        
        # Validation
        preds = self.model.predict(X_test)
        acc = accuracy_score(y_test, preds)
        print(f"[*] XGBoost Training Complete. Validation Accuracy: {acc*100:.2f}%")
        print("[*] Classification Report:")
        print(classification_report(y_test, preds, zero_division=0))
        
        self.is_trained = True

    def score_live_signal(self, live_features: dict) -> float:
        """
        Runs live data through the model to get a probabilistic confidence score.
        """
        if not self.is_trained:
            # Fallback to rule-based confidence if AI isn't trained
            return 0.50
            
        df = pd.DataFrame([live_features])
        # predict_proba returns [[prob_class_0, prob_class_1]]
        probability = self.model.predict_proba(df)[0][1]
        return probability

if __name__ == "__main__":
    # Mock Training
    engine = AIEngine()
    
    # Generate some mock data where low PCR and high spot leads to Label=1
    import numpy as np
    n_samples = 1000
    mock_df = pd.DataFrame({
        'spot_close': np.random.uniform(22000, 23000, n_samples),
        'vwap': np.random.uniform(22000, 23000, n_samples),
        'pcr': np.random.uniform(0.5, 1.5, n_samples),
        'max_pain': np.random.uniform(22000, 23000, n_samples),
        'ce_premium': np.random.uniform(50, 200, n_samples),
        'pe_premium': np.random.uniform(50, 200, n_samples)
    })
    
    # Create artificial label: 1 if spot > vwap and pcr < 0.8
    mock_df['AI_Label'] = ((mock_df['spot_close'] > mock_df['vwap']) & (mock_df['pcr'] < 0.8)).astype(int)
    
    engine.train(mock_df)
    
    # Test Live Scoring
    test_live = {
        'spot_close': 22550, 'vwap': 22500, 'pcr': 0.6, 
        'max_pain': 22400, 'ce_premium': 150, 'pe_premium': 80
    }
    prob = engine.score_live_signal(test_live)
    print(f"\n[*] Live Signal Confidence Score (Probability of Success): {prob*100:.2f}%")
