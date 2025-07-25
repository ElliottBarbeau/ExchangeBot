import logging
import os

from discord.ext import commands
from utils.hl_utils import get_price

class Price(commands.Cog):
    def __init__(self, bot):
        self.CMC_API_KEY = os.getenv("CMC_API_KEY")
        self.PRICE_URL = "https://pro-api.coinmarketcap.com/v2/cryptocurrency/quotes/latest"
        self.bot = bot
    
    @commands.command(name="price")
    async def price_command(self, ctx, coin: str):
        coin = coin.upper()
        price = await get_price(coin)
        await ctx.send(f"The price of {coin} is {price}")

async def setup(bot):
    logging.info("Running Price cog setup()")
    await bot.add_cog(Price(bot))