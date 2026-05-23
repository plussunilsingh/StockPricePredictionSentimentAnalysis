import os
import json
import time
import asyncio
import logging
import threading
from datetime import datetime, timedelta
import redis.asyncio as redis
from SmartApi.smartWebSocketV2 import SmartWebSocketV2

logger = logging.getLogger(__name__)

class AngelOneDataCollector:
    """
    Pillar 1: Reliability & Market Data Infrastructure
    Ported from Vega App. Handles robust connection to AngelOne.
    Pushes ticks to Redis Streams.
    """
    def __init__(self):
        self.api_key = os.getenv("ANGEL_API_KEY")
        self.client_code = os.getenv("ANGEL_CLIENT_CODE")
        self.jwt_token = os.getenv("ANGEL_JWT_TOKEN")
        self.feed_token = os.getenv("ANGEL_FEED_TOKEN")
        
        # Redis setup
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.redis_client = None
        
        self.ws = None
        self.is_running = False
        
        # Retry Logic Configuration
        self.retry_count = 0
        self.max_retries = 5
        self.rate_limited = False
        
        # Mock tokens for Nifty
        self.tokens = [
            {"exchangeType": 1, "tokens": ["26000"]} # NIFTY 50 Token
        ]

    async def init_redis(self):
        try:
            self.redis_client = await redis.Redis(host=self.redis_host, port=6379, decode_responses=True)
            print("[*] Connected to Redis successfully.")
        except Exception as e:
            print(f"[!] Redis connection failed: {e}")

    def start(self):
        """Starts the WebSocket connection with automatic token retrieval and guardrails."""
        if self.is_running:
            return

        if not self.jwt_token or not self.feed_token:
            print("[!] Missing AngelOne tokens. Running in simulation mode.")
            asyncio.run(self._dry_run_simulation())
            return

        print("[*] Initializing AngelOne WebSocket...")
        self.ws = SmartWebSocketV2(self.jwt_token, self.api_key, self.client_code, self.feed_token)
        
        self.ws.onOpen = self._on_open
        self.ws.onData = self._on_data
        self.ws.onError = self._on_error
        self.ws.onClose = self._on_close

        self.is_running = True
        
        # Run in thread
        threading.Thread(target=self.ws.connect, daemon=True).start()

    def _on_open(self, wsapp):
        print("[*] AngelOne WebSocket Connected. Subscribing to market feeds...")
        self.retry_count = 0
        self.ws.subscribe("vega_production_feed", 3, self.tokens)

    def _on_data(self, wsapp, message):
        """Handles incoming ticks and pushes to Redis."""
        try:
            if not isinstance(message, dict) or "token" not in message:
                return

            token = message["token"]
            ltp = float(message.get("lastTradedPrice", 0)) / 100.0
            if ltp <= 0:
                return

            # Push tick to a Redis stream async-ly
            tick_data = {
                "timestamp": datetime.now().isoformat(),
                "instrument": f"ANGELONE:{token}",
                "ltp": ltp,
                "volume": message.get("volume", 0)
            }
            
            # Since _on_data is sync, we use a fire-and-forget task
            if self.redis_client:
                asyncio.run_coroutine_threadsafe(
                    self.redis_client.xadd(f"ticks:ANGELONE:{token}", tick_data),
                    asyncio.get_event_loop()
                )
            else:
                print(f"[TICK] {tick_data}")

        except Exception as e:
            print(f"[!] Tick Processing Error: {e}")

    def _on_error(self, wsapp, error):
        errorStr = str(error)
        print(f"[!] WebSocket Error: {errorStr}")
        if "429" in errorStr or "Connection Limit Exceeded" in errorStr:
            print("[!] RATE LIMIT DETECTED (429).")
            self.rate_limited = True
            if wsapp:
                wsapp.close()

    def _on_close(self, wsapp, *args, **kwargs):
        print("[!] WebSocket Connection Closed.")
        if self.rate_limited:
            return

        if self.retry_count < self.max_retries:
            self.retry_count += 1
            backoff = min(60, 5 * (2 ** (self.retry_count - 1)))
            print(f"[*] Reconnecting in {backoff}s (Attempt {self.retry_count}/{self.max_retries})...")
            time.sleep(backoff)
            self.start()

    async def _dry_run_simulation(self):
        """Simulates incoming tick data if no tokens provided."""
        await self.init_redis()
        print("[*] Simulating AngelOne tick ingestion (1 tick / second)...")
        for i in range(10):
            timestamp = datetime.now().isoformat()
            instrument = "ANGELONE:26000"
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
    collector = AngelOneDataCollector()
    
    # We need a running event loop for Redis async pushing
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    loop.run_until_complete(collector.init_redis())
    
    # Normally collector.start() connects WebSocket if tokens exist
    # For now, it will default to dry_run_simulation due to no tokens.
    collector.start()
    
    # Keep loop running
    try:
        loop.run_forever()
    except KeyboardInterrupt:
        pass
