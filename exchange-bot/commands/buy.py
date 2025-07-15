import logging
import json
import os

from pathlib import Path
from discord.ext import commands
from collections import defaultdict
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from dotenv import load_dotenv

class Buy(commands.Cog):
    def __init__(self, bot):
        BASE_DIR = Path(__file__).resolve().parent.parent
        ENV_FILE = ".env"
        load_dotenv(BASE_DIR / ENV_FILE)

        self.CMC_API_KEY = os.getenv("CMC_API_KEY")
        self.PRICE_URL = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
        self.d = defaultdict(int)
        self.bot = bot

    def get_price(self, coin):
        parameters = {
        'symbol': coin
        }
        headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': self.CMC_API_KEY,
        }

        session = Session()
        session.headers.update(headers)

        try:
            response = session.get(self.PRICE_URL, params=parameters)
            data = json.loads(response.text)
            print(data)
        except (ConnectionError, Timeout, TooManyRedirects) as e:
            print(e)

        price = float(data['data'][coin][0]["quote"]["USD"]["price"])
        return price
    
    @commands.command(name="buy")
    async def buy_command(self, ctx, coin: str, dollars: float):
        # TODO:
        # add support for more coins

        # add exceptions if an invalid coin is entered
        coin = coin.upper()
        amount_purchased = dollars / self.get_price(coin)
        self.d[coin] += amount_purchased

        await ctx.send(f"{coin} purchased, you now have {round(self.d[coin], 2)} {coin}")

def setup(bot):
    logging.info("Running Buy cog setup()")
    bot.add_cog(Buy(bot))