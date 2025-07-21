import logging
import datetime
import math

from discord.ext import commands
from utils.hl_utils import get_price

from database.portfolio_queries import get_portfolio, update_portfolio
from database.balance_queries import get_balance, update_balance

class Buy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="buy")
    async def buy_command(self, ctx, symbol: str, amount: str):
        if not self.bot.initialized:
            await ctx.send("Bot not initialized. Did you forget to run $start?")
            return
        
        user_id = str(ctx.author.id)
        user_balance = get_balance(user_id)

        if user_balance is None:
            await ctx.send("User has not joined the game. Type $join to get started!")
            return

        now = datetime.datetime.now()
        symbol = symbol.upper()
        price_per_token = await get_price(symbol)
        total_price = 0

        # If amount starts with '$' => dollar amount
        if amount.startswith('$'):
            try:
                total_price = float(amount[1:])
                token_amount = total_price / price_per_token
            except ValueError:
                await ctx.send("Invalid dollar amount format.")
                return
        else:
            try:
                token_amount = float(amount)
                total_price = token_amount * price_per_token
            except ValueError:
                await ctx.send("Invalid token amount format.")
                return
            
        if token_amount <= 0 or math.isnan(token_amount):
            await ctx.send(f"Amount must be greater than 0.")
            return

        if not user_balance or user_balance < total_price:
            await ctx.send("Not enough balance to execute this trade. $join to join the game, or $fill to get extra money!")
            return
        
        row = get_portfolio(user_id, symbol)
        if row:
            new_amount = row.amount + token_amount
            new_avg = ((row.amount * row.avg_price) + (token_amount * price_per_token)) / new_amount
        else:
            new_amount = token_amount
            new_avg = price_per_token

        update_portfolio(user_id, symbol, new_amount, new_avg, now)
        update_balance(user_id, user_balance - total_price)

        await ctx.send(f"{token_amount:,.4f} {symbol} purchased, you now have {new_amount:,.4f} {symbol}")
            

async def setup(bot):
    logging.info("Running Buy cog setup()")
    await bot.add_cog(Buy(bot))