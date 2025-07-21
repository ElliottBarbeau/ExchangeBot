# utils/hl_utils.py
import asyncio
import json
import logging
import websockets

# Cache for latest prices
price_cache = {}

# Hyperliquid WebSocket URL
WS_URL = "wss://api.hyperliquid.xyz/ws"

async def connect_allmids():
    global price_cache

    while True:
        try:
            async with websockets.connect(WS_URL, ping_interval=20, ping_timeout=20) as ws:
                logging.info("[Hyperliquid] Connected to WebSocket (allMids)")

                # Subscribe to all mid-market prices
                await ws.send(json.dumps({
                    "method": "subscribe",
                    "subscription": {"type": "allMids"}
                }))
                logging.info("[Hyperliquid] Subscribed to allMids")

                async for message in ws:
                    try:
                        data = json.loads(message)
                        logging.debug(f"[Hyperliquid] WS message: {data}")

                        if data.get("channel") == "allMids":
                            mids = data.get("data", {})
                            price_cache = mids
                            
                    except Exception as e:
                        logging.error(f"[Hyperliquid] Error parsing WebSocket message: {e}")

        except Exception as e:
            logging.error(f"[Hyperliquid] WebSocket disconnected: {e}. Reconnecting in 5s...")
            await asyncio.sleep(5)


async def get_price(symbol: str):
    print(price_cache)
    return float(price_cache.get(symbol.upper()))


def start_price_feed(loop: asyncio.AbstractEventLoop):
    loop.create_task(connect_allmids())
