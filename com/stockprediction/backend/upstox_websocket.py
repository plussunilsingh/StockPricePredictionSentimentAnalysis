import os
import json
import asyncio
import websockets
import redis.asyncio as redis
from datetime import datetime

class UpstoxDataCollector:
    """
    Pillar 1: Reliability & Market Data Infrastructure
    Handles low-latency WebSocket connections to Upstox API for real-time tick data.
    Features: Auto-reconnect, Tick Deduplication, Redis Caching.
    """
    
    def __init__(self):
        self.api_key = os.getenv("UPSTOX_API_KEY")
        self.access_token = os.getenv("UPSTOX_ACCESS_TOKEN")
        self.ws_url = "wss://api.upstox.com/v2/feed/market-data-feed"
        
        # Redis connection for caching ticks (Stage 1 Infrastructure)
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_client = None
        
        self.subscriptions = [
            "NSE_INDEX|Nifty 50",
            "NSE_INDEX|Nifty Bank"
        ]
        
        # Deduplication state
        self.last_tick_timestamp = {}

    async def init_redis(self):
        """Initialize async Redis client."""
        try:
            self.redis_client = await redis.Redis(host=self.redis_host, port=6379, decode_responses=True)
            print("[*] Connected to Redis successfully.")
        except Exception as e:
            print(f"[!] Redis connection failed: {e}")

    async def connect(self):
        """Establishes connection with robust auto-reconnect logic."""
        await self.init_redis()
        
        if not self.access_token:
            print("[ERROR] UPSTOX_ACCESS_TOKEN is missing.")
            print("[SYSTEM] Running in dry-run mode for architecture validation...")
            await self._dry_run_simulation()
            return

        headers = {'Authorization': f'Bearer {self.access_token}'}
        
        while True:
            try:
                print(f"[*] Connecting to Upstox Market Feed...")
                async with websockets.connect(self.ws_url, extra_headers=headers, ping_interval=20, ping_timeout=20) as websocket:
                    print("[*] Connection Established.")
                    
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

                    while True:
                        message = await websocket.recv()
                        await self._process_tick(message)
                        
            except websockets.exceptions.ConnectionClosed as e:
                print(f"[!] WebSocket disconnected: {e}. Reconnecting in 2 seconds...")
                await asyncio.sleep(2)
            except Exception as e:
                print(f"[!] Unexpected error: {e}. Reconnecting in 5 seconds...")
                await asyncio.sleep(5)

    async def _process_tick(self, message):
        """Processes tick, deduplicates, and pushes to Redis."""
        # Note: In production, Upstox sends binary Protobuf data.
        # This is simplified JSON parsing for demonstration.
        try:
            tick = json.loads(message)
            instrument = tick.get("instrument")
            timestamp = tick.get("timestamp")
            
            # Deduplication: Drop tick if timestamp hasn't changed
            if self.last_tick_timestamp.get(instrument) == timestamp:
                return 
            self.last_tick_timestamp[instrument] = timestamp
            
            # Push to Redis for the OHLC Aggregator to consume
            if self.redis_client:
                # Push tick to a Redis stream
                await self.redis_client.xadd(f"ticks:{instrument}", tick)
                
        except Exception as e:
            print(f"[!] Tick processing error: {e}")

    async def _dry_run_simulation(self):
        """Simulates incoming tick data for development."""
        print("[*] Simulating live tick ingestion (1 tick / second)...")
        for i in range(10):
            timestamp = datetime.now().isoformat()
            instrument = "NSE_INDEX|Nifty 50"
            simulated_tick = {
                "timestamp": timestamp,
                "instrument": instrument,
                "ltp": 22500.50 + (i * 2.5),
                "volume": 1200 + i
            }
            print(f" [TICK] {simulated_tick}")
            
            if self.redis_client:
                await self.redis_client.xadd(f"ticks:{instrument}", simulated_tick)
                print(f"   -> Pushed to Redis stream: ticks:{instrument}")
                
            await asyncio.sleep(1)

if __name__ == "__main__":
    collector = UpstoxDataCollector()
    asyncio.run(collector.connect())
