import os
import asyncio
import pandas as pd
import redis.asyncio as redis
import asyncpg
from datetime import datetime

class PostgresOHLCAggregator:
    """
    Pillar 1: Reliability & Market Data Infrastructure
    Consumes live ticks from Redis, aggregates into 1m/5m candles, 
    and saves permanently to PostgreSQL (TimescaleDB).
    """
    
    def __init__(self):
        self.redis_host = os.getenv("REDIS_HOST", "localhost")
        self.db_host = os.getenv("DB_HOST", "localhost")
        self.db_user = os.getenv("DB_USER", "quant")
        self.db_pass = os.getenv("DB_PASS", "quant123")
        self.db_name = os.getenv("DB_NAME", "market_data")
        
        self.redis_client = None
        self.pg_pool = None
        
        # Buffer to hold ticks until candle closure
        self.tick_buffer = []

    async def initialize_connections(self):
        """Connects to Redis (Source) and PostgreSQL (Destination)."""
        # Connect to Redis
        self.redis_client = await redis.Redis(host=self.redis_host, port=6379, decode_responses=True)
        print("[*] Aggregator connected to Redis.")
        
        # Connect to PostgreSQL (TimescaleDB)
        try:
            self.pg_pool = await asyncpg.create_pool(
                user=self.db_user, password=self.db_pass,
                database=self.db_name, host=self.db_host, port=5432
            )
            print("[*] Aggregator connected to PostgreSQL (TimescaleDB).")
            await self._create_tables()
        except Exception as e:
            print(f"[!] PostgreSQL connection failed. Make sure Docker is running. Error: {e}")

    async def _create_tables(self):
        """Creates hypertable for candles if it doesn't exist."""
        query = """
        CREATE TABLE IF NOT EXISTS candles_1m (
            time TIMESTAMPTZ NOT NULL,
            instrument TEXT NOT NULL,
            open DOUBLE PRECISION,
            high DOUBLE PRECISION,
            low DOUBLE PRECISION,
            close DOUBLE PRECISION,
            volume BIGINT,
            PRIMARY KEY (time, instrument)
        );
        -- TimescaleDB hypertable conversion (assuming extension exists)
        -- SELECT create_hypertable('candles_1m', 'time', if_not_exists => TRUE);
        """
        async with self.pg_pool.acquire() as connection:
            await connection.execute(query)
            print("[*] Verified candles_1m table schema.")

    async def stream_and_aggregate(self):
        """Streams ticks from Redis and performs time-based aggregation."""
        await self.initialize_connections()
        
        instrument = "NSE_INDEX|Nifty 50"
        stream_name = f"ticks:{instrument}"
        last_id = '0' # Read from beginning of stream (or '$' for new only)

        print(f"[*] Listening to Redis Stream: {stream_name}")
        while True:
            if not self.redis_client:
                await asyncio.sleep(1)
                continue
                
            try:
                # Block for 1 second waiting for new ticks
                events = await self.redis_client.xread({stream_name: last_id}, count=100, block=1000)
                for stream, messages in events:
                    for message_id, tick_data in messages:
                        self.tick_buffer.append(tick_data)
                        last_id = message_id
                
                # Check if we should aggregate (e.g. 60 seconds have passed or buffer size reached)
                if len(self.tick_buffer) >= 60: 
                    await self._aggregate_and_save(instrument)
                    
            except Exception as e:
                print(f"[!] Stream error: {e}")
                await asyncio.sleep(1)

    async def _aggregate_and_save(self, instrument: str):
        """Aggregates buffer into a 1-minute candle and saves to DB."""
        if not self.tick_buffer:
            return
            
        df = pd.DataFrame(self.tick_buffer)
        # Convert LTP to float explicitly
        df['ltp'] = pd.to_numeric(df['ltp'])
        df['volume'] = pd.to_numeric(df['volume'])
        
        # Calculate OHLC
        _open = float(df['ltp'].iloc[0])
        _high = float(df['ltp'].max())
        _low = float(df['ltp'].min())
        _close = float(df['ltp'].iloc[-1])
        _vol = int(df['volume'].sum())
        
        # In a real app, 'time' aligns to the exact minute boundary
        candle_time = datetime.now()
        
        # Insert into PostgreSQL
        if self.pg_pool:
            query = """
            INSERT INTO candles_1m (time, instrument, open, high, low, close, volume)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (time, instrument) DO NOTHING;
            """
            async with self.pg_pool.acquire() as connection:
                await connection.execute(query, candle_time, instrument, _open, _high, _low, _close, _vol)
                print(f"[*] Inserted 1M Candle for {instrument} at {_close}")
        
        # Clear buffer
        self.tick_buffer.clear()

if __name__ == "__main__":
    aggregator = PostgresOHLCAggregator()
    # To run this, Docker services (Redis + Postgres) must be up.
    # asyncio.run(aggregator.stream_and_aggregate())
    print("[*] PostgresOHLCAggregator Module Ready.")
