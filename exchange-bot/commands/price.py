import logging
import json
import os

from discord.ext import commands
from collections import defaultdict
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from dotenv import load_dotenv

class Price(commands.Cog):
    def __init__(self, bot):
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
    
    @commands.command(name="price")
    async def price_command(self, ctx, coin: str):
        coin = coin.upper()
        price = round(self.get_price(coin), 2)
        await ctx.send(f"The price of {coin} is {price}")

def setup(bot):
    logging.info("Running Price cog setup()")
    bot.add_cog(Price(bot))