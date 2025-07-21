import logging
import datetime
import math

from discord.ext import commands
from utils.cmc_utils import get_price

from database.portfolio_queries import get_portfolio, update_portfolio
from database.balance_queries import get_balance, update_balance

class Sell(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="sell")
    async def sell_command(self, ctx, symbol: str, amount: str):
        if not self.bot.initialized:
            await ctx.send("Bot not initialized. Did you forget to run $start?")
            return
        
        user_id = str(ctx.author.id)
        now = datetime.datetime.now()
        symbol = symbol.upper()
        price_per_token = get_price(symbol)
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

        print('TKN AMOUNT', token_amount)
            
        row = get_portfolio(user_id, symbol)
        user_balance = get_balance(user_id)

        if not row or row.amount < token_amount:
            await ctx.send(f"You don't have enough {symbol} to sell!")
            return
        
        new_amount = row.amount - token_amount
        
        update_portfolio(user_id, symbol, new_amount, row.avg_price, now)
        update_balance(user_id, user_balance + total_price)

        new_balance = get_balance(user_id)

        await ctx.send(f"{token_amount:,.4f} {symbol} sold. Your new balance is {new_balance:,.4f}")

async def setup(bot):
    logging.info("Running Sell cog setup()")
    await bot.add_cog(Sell(bot))