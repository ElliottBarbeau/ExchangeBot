# utils/price_utils.py
import asyncio
import json
import websockets
import logging

# Store latest prices
price_cache = {}
# Track subscribed coins
subscribed_coins = set()

# WebSocket connection
ws_conn = None
ws_url = "wss://api.hyperliquid.xyz/ws"

async def connect_ws():
    global ws_conn
    while True:
        try:
            async with websockets.connect(ws_url, ping_interval=20, ping_timeout=20) as ws:
                ws_conn = ws
                logging.info("[Hyperliquid] WebSocket connected")

                async for message in ws:
                    try:
                        data = json.loads(message)
                        logging.debug(f"[Hyperliquid] WS message: {data}")
                        if data.get("channel") == "ticker":
                            coin = data.get("coin", "").upper()
                            price = float(data.get("markPx", 0))
                            price_cache[coin] = price
                            logging.debug(f"[Hyperliquid] Updated {coin}: {price}")
                    except Exception as e:
                        logging.error(f"[Hyperliquid] Error parsing message: {e}")
        except Exception as e:
            logging.error(f"[Hyperliquid] WebSocket disconnected: {e}. Reconnecting in 5s...")
            await asyncio.sleep(5)

async def subscribe_coin(coin: str):
    global ws_conn
    if ws_conn is None:
        logging.warning(f"[Hyperliquid] Can't subscribe to {coin} — WebSocket not ready")
        return

    if coin.upper() not in subscribed_coins:
        try:
            payload = {
                "method": "subscribe",
                "subscriptions": [{"type": "ticker", "coin": coin.upper()}]
            }
            await ws_conn.send(json.dumps(payload))
            subscribed_coins.add(coin.upper())
            logging.info(f"[Hyperliquid] Subscribed to {coin}")
        except Exception as e:
            logging.error(f"[Hyperliquid] Failed to subscribe to {coin}: {e}")

async def get_price(symbol: str):
    symbol = symbol.upper()
    await subscribe_coin(symbol)
    for _ in range(30):
        if symbol in price_cache:
            return price_cache[symbol]
        await asyncio.sleep(0.1)
    return None

def start_price_feed(loop: asyncio.AbstractEventLoop):
    loop.create_task(connect_ws())
