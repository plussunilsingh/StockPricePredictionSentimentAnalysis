import os
import asyncio
import pandas as pd
import redis.asyncio as redis
import asyncpg
from typing import Dict, Any

class LiveDBClient:
    """
    Fetches real-time market data exclusively from Redis (Ticks)
    and PostgreSQL/TimescaleDB (Historical Aggregation).
    Contains strictly ZERO mock data.
    """
    def __init__(self):
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_user = os.getenv("DB_USER", "quant")
        self.db_pass = os.getenv("DB_PASS", "quant123")
        self.db_name = os.getenv("DB_NAME", "market_data")
        
        self.redis_client = None
        self.pg_pool = None

    async def connect(self):
        """Establishes connections to databases if not already connected."""
        if not self.redis_client:
            try:
                self.redis_client = await redis.Redis(host=self.redis_host, port=6379, decode_responses=True)
            except Exception as e:
                print(f"[!] DBClient Redis Error: {e}")
                
        if not self.pg_pool:
            try:
                self.pg_pool = await asyncpg.create_pool(
                    user=self.db_user, password=self.db_pass,
                    database=self.db_name, host=self.db_host, port=5432
                )
            except Exception as e:
                print(f"[!] DBClient PostgreSQL Error: {e}")

    async def get_latest_spot(self, instrument: str = "ANGELONE:26000") -> float:
        """Fetches the absolute latest LTP from the Redis stream."""
        if not self.redis_client:
            return 0.0
            
        try:
            # XREVRANGE to get the very last tick from the stream
            result = await self.redis_client.xrevrange(f"ticks:{instrument}", max="+", min="-", count=1)
            if result:
                # result is [(message_id, {dict_of_data})]
                tick_data = result[0][1]
                return float(tick_data.get("ltp", 0.0))
        except Exception:
            pass
            
        return 0.0

    async def get_latest_candles(self, instrument: str = "ANGELONE:26000", limit: int = 50) -> pd.DataFrame:
        """Fetches the latest aggregated OHLC candles from TimescaleDB."""
        if not self.pg_pool:
            return pd.DataFrame()
            
        query = """
        SELECT time, open, high, low, close, volume 
        FROM candles_1m 
        WHERE instrument = $1 
        ORDER BY time DESC 
        LIMIT $2
        """
        
        try:
            async with self.pg_pool.acquire() as connection:
                records = await connection.fetch(query, instrument, limit)
                
            if not records:
                return pd.DataFrame()
                
            df = pd.DataFrame([dict(r) for r in records])
            # Reverse to maintain chronological order for charting
            df = df.sort_values(by="time").reset_index(drop=True)
            return df
        except Exception:
            return pd.DataFrame()

    async def get_system_health(self) -> Dict[str, str]:
        """Returns the actual connection status of the DB infrastructure."""
        health = {
            "Redis": "OFFLINE",
            "TimescaleDB": "OFFLINE"
        }
        
        if self.redis_client:
            try:
                await self.redis_client.ping()
                health["Redis"] = "ONLINE"
            except Exception:
                pass
                
        if self.pg_pool:
            health["TimescaleDB"] = "ONLINE"
            
        return health
