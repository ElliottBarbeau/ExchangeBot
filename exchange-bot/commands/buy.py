import logging
import datetime
import uuid

from discord.ext import commands
from cmc_interface import get_price

class Buy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.session = bot.cassandra_session
    
    @commands.command(name="buy")
    async def buy_command(self, ctx, symbol: str, amount: float, type: str):
        # TODO:
        # Fix formatting, store CQL queries elsewhere

        user_id = str(ctx.author.id)
        now = datetime.datetime.now()
        symbol = symbol.upper()
        amount = amount / get_price(symbol) if type == "dollars" else amount
        price = get_price(symbol)
        
        row = self.session.execute("""
            SELECT amount, avg_price FROM user_portfolio
            WHERE user_id = %s AND symbol = %s
        """, (user_id, symbol)).one()

        if row:
            new_amount = row.amount + amount
            new_avg = ((row.amount * row.avg_price) + (amount * price)) / new_amount
        else:
            new_amount = amount
            new_avg = price

        self.session.execute("""
            INSERT INTO user_portfolio (user_id, symbol, amount, avg_price, last_updated)
            VALUES (%s, %s, %s, %s, %s)
        """, (user_id, symbol, new_amount, new_avg, now))

        await ctx.send(f"{symbol} purchased, you now have {round(new_amount, 2)} {symbol}")

async def setup(bot):
    logging.info("Running Buy cog setup()")
    await bot.add_cog(Buy(bot))