import logging
import json
import os

from discord.ext import commands
from collections import defaultdict
from requests import Session
from requests.exceptions import ConnectionError, Timeout, TooManyRedirects
from dotenv import load_dotenv
from cmc_interface import get_price

class Price(commands.Cog):
    def __init__(self, bot):
        self.CMC_API_KEY = os.getenv("CMC_API_KEY")
        self.PRICE_URL = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
        self.bot = bot
    
    @commands.command(name="price")
    async def price_command(self, ctx, coin: str):
        coin = coin.upper()
        price = round(get_price(coin), 2)
        await ctx.send(f"The price of {coin} is {price}")

async def setup(bot):
    logging.info("Running Price cog setup()")
    await bot.add_cog(Price(bot))