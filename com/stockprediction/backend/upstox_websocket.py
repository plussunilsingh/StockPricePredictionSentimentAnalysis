import os
import json
import asyncio
import websockets
from datetime import datetime

class UpstoxDataCollector:
    """
    Pillar 1: Market Data Infrastructure
    Handles low-latency WebSocket connections to Upstox API for real-time tick data.
    """
    
    def __init__(self):
        self.api_key = os.getenv("UPSTOX_API_KEY")
        self.access_token = os.getenv("UPSTOX_ACCESS_TOKEN")
        # Base Upstox WebSocket URL for market data
        self.ws_url = "wss://api.upstox.com/v2/feed/market-data-feed"
        
        # Subscriptions list (e.g. NIFTY 50 Index, specific Option strikes)
        self.subscriptions = [
            "NSE_INDEX|Nifty 50",
            "NSE_INDEX|Nifty Bank"
        ]

    async def connect(self):
        """Establishes connection and handles the real-time stream."""
        if not self.access_token:
            print("[ERROR] UPSTOX_ACCESS_TOKEN is missing. Please set environment variable.")
            print("[SYSTEM] Running in dry-run mode for architecture validation...")
            await self._dry_run_simulation()
            return

        headers = {
            'Authorization': f'Bearer {self.access_token}'
        }
        
        try:
            print(f"[*] Connecting to Upstox Market Feed...")
            async with websockets.connect(self.ws_url, extra_headers=headers) as websocket:
                print("[*] Connection Established.")
                
                # Send subscription request
                sub_request = {
                    "guid": "sub_1",
                    "method": "sub",
                    "data": {
                        "mode": "full",
                        "instrumentKeys": self.subscriptions
                    }
                }
                await websocket.send(json.dumps(sub_request))
                print(f"[*] Subscribed to: {self.subscriptions}")

                # Listen for live ticks
                while True:
                    message = await websocket.recv()
                    # In a production setup, we parse protobuf/binary to JSON
                    # and push to a queue (like Redis or local buffer)
                    await self._process_tick(message)
                    
        except Exception as e:
            print(f"[!] WebSocket connection error: {e}")
            # Real institutional systems would have auto-reconnect logic here

    async def _process_tick(self, message):
        """Processes raw tick data and feeds it to the OHLC aggregator."""
        # Parsing logic goes here.
        # This will feed into Task 1.2: OHLC Aggregation.
        pass

    async def _dry_run_simulation(self):
        """Simulates incoming tick data for development purposes when API keys are absent."""
        print("[*] Simulating live tick ingestion (1 tick / second)...")
        for i in range(5):
            simulated_tick = {
                "timestamp": datetime.now().isoformat(),
                "instrument": "NSE_INDEX|Nifty 50",
                "ltp": 22500.50 + (i * 2.5),
                "volume": 1200 + i
            }
            print(f" [TICK] {simulated_tick}")
            await asyncio.sleep(1)

if __name__ == "__main__":
    collector = UpstoxDataCollector()
    asyncio.run(collector.connect())
