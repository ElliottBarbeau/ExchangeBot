import logging
import json
import os

from pathlib import Path
from discord.ext import commands
from collections import defaultdict
from requests import Request, Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from dotenv import load_dotenv
from cmc_interface import get_price

class Buy(commands.Cog):
    def __init__(self, bot):
        BASE_DIR = Path(__file__).resolve().parent.parent
        ENV_FILE = ".env"
        load_dotenv(BASE_DIR / ENV_FILE)
        self.CMC_API_KEY = os.getenv("CMC_API_KEY")
        self.PRICE_URL = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
        self.d = defaultdict(int)
        self.bot = bot
    
    @commands.command(name="buy")
    async def buy_command(self, ctx, coin: str, dollars: float):
        # TODO:
        # Hook up to DB to have user profiles
        coin = coin.upper()
        amount_purchased = dollars / get_price(coin)
        self.d[coin] += amount_purchased

        await ctx.send(f"{coin} purchased, you now have {round(self.d[coin], 2)} {coin}")

def setup(bot):
    logging.info("Running Buy cog setup()")
    bot.add_cog(Buy(bot))