import os
import json
from pathlib import Path

# Static Knowledge Nodes for Market Indices
MARKET_INDICES_KNOWLEDGE = {
    "NIFTY_50": {
        "description": "The NIFTY 50 is a benchmark Indian stock market index that represents the weighted average of 50 of the largest Indian companies listed on the National Stock Exchange (NSE).",
        "inception_year": 1996,
        "max_historical_data": "Approx 28 years",
        "sectors": ["Financial Services", "IT", "Oil & Gas", "Consumer Goods", "Automobile"]
    },
    "SENSEX": {
        "description": "The BSE SENSEX is a free-float market-weighted stock market index of 30 well-established and financially sound companies listed on the Bombay Stock Exchange (BSE).",
        "base_year": "1978-79",
        "max_historical_data": "Approx 45 years",
        "sectors": ["Financials", "Information Technology", "Energy", "FMCG"]
    },
    "BANKNIFTY": {
        "description": "The NIFTY Bank Index comprises the most liquid and large capitalized Indian banking stocks. It provides investors and market intermediaries with a benchmark that captures the capital market performance of Indian Banks.",
        "inception_year": 2000,
        "max_historical_data": "Approx 24 years",
        "sectors": ["Public Sector Banks", "Private Sector Banks"]
    },
    "DJIA": {
        "description": "The Dow Jones Industrial Average is a stock market index that measures the stock performance of 30 large, publicly owned companies listed on stock exchanges in the United States.",
        "inception_year": 1896,
        "max_historical_data": "100+ years",
        "sectors": ["Various (Excludes Transportation and Utilities)"]
    },
    "SP500": {
        "description": "The Standard and Poor's 500 is a stock market index tracking the stock performance of 500 of the largest companies listed on stock exchanges in the United States.",
        "inception_year": 1957,
        "max_historical_data": "Data back to 1920s available synthetically",
        "sectors": ["Technology", "Health Care", "Financials", "Consumer Discretionary"]
    }
}

def build_context_graph(project_root: str, output_path: str):
    """
    Scans the project directory and builds a context graph (JSON) mapping 
    files, purposes, and injecting market index knowledge.
    """
    graph = {
        "project_metadata": {
            "name": "Stock Price Prediction & Sentiment Analysis System",
            "description": "System for deep market analysis, utilizing 100-year data, options strategies, and advanced LLMs (FinBERT, TimeGPT)."
        },
        "market_knowledge": MARKET_INDICES_KNOWLEDGE,
        "nodes": [],
        "edges": []
    }
    
    root_path = Path(project_root)
    
    # Simple file scanning for the graph
    for ext in ['*.py', '*.md', '*.sh', 'Dockerfile*']:
        for file_path in root_path.rglob(ext):
            if 'venv' in file_path.parts or '.git' in file_path.parts or '.pytest_cache' in file_path.parts:
                continue
                
            relative_path = file_path.relative_to(root_path)
            node_id = str(relative_path)
            
            graph["nodes"].append({
                "id": node_id,
                "type": "file",
                "extension": file_path.suffix
            })
            
            # Simple implicit edges (e.g. backend files depend on data)
            if 'backend' in file_path.parts:
                graph["edges"].append({"source": node_id, "target": "data_layer", "relation": "reads_from"})
            
    with open(output_path, 'w') as f:
        json.dump(graph, f, indent=4)
        
    print(f"Context Graph successfully generated at {output_path}")

if __name__ == "__main__":
    PROJECT_ROOT = "/Users/suniltomar/Desktop/workspace/StockPricePredictionSentimentAnalysis"
    DOCS_DIR = os.path.join(PROJECT_ROOT, "docs")
    os.makedirs(DOCS_DIR, exist_ok=True)
    OUTPUT_FILE = os.path.join(DOCS_DIR, "context_graph.json")
    build_context_graph(PROJECT_ROOT, OUTPUT_FILE)
