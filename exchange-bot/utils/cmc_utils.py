import json
import os

from pathlib import Path
from collections import defaultdict
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from dotenv import load_dotenv
from hyperliquid import HyperliquidSync

BASE_DIR = Path(__file__).resolve().parent.parent
ENV_FILE = ".env"
load_dotenv(BASE_DIR / ENV_FILE)
CMC_API_KEY = os.getenv("CMC_API_KEY")
PRICE_URL = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"

def get_price(coin):
    parameters = {
    'symbol': coin
    }
    headers = {
    'Accepts': 'application/json',
    'X-CMC_PRO_API_KEY': CMC_API_KEY,
    }

    session = Session()
    session.headers.update(headers)

    try:
        response = session.get(PRICE_URL, params=parameters)
        data = json.loads(response.text)
    except (ConnectionError, Timeout, TooManyRedirects) as e:
        print(e)

    price = float(data['data'][coin][0]["quote"]["USD"]["price"])
    return price

def get_coin_price(symbol="BTC/USDC:USDC"):
    symbol = symbol.upper()
    symbol += "/USDC:USDC"
    
    ex = HyperliquidSync({})
    ticker = ex.fetch_ticker(symbol)
    return float(ticker['last'])

if __name__ == "__main__":
    print("BTC price on Hyperliquid:", get_coin_price())