import logging
import datetime

from discord.ext import commands
from cmc_interface import get_price

from database.portfolio_queries import get_portfolio, update_portfolio
from database.balance_queries import get_balance, update_balance

class Buy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="buy")
    async def buy_command(self, ctx, symbol: str, amount: float, type: str):
        if self.bot.initialized:
            user_id = str(ctx.author.id)
            now = datetime.datetime.now()
            symbol = symbol.upper()

            price_per_token = get_price(symbol)
            total_price = amount if type == "dollars" else amount * price_per_token
            amount = (amount / price_per_token) if type == "dollars" else amount
            user_balance = get_balance(user_id)

            if user_balance >= total_price:
                row = get_portfolio(user_id, symbol)
                if row:
                    new_amount = row.amount + amount
                    new_avg = ((row.amount * row.avg_price) + (amount * price_per_token)) / new_amount
                else:
                    new_amount = amount
                    new_avg = price_per_token

                print("balance and price of purchase", user_balance, total_price)
                update_portfolio(user_id, symbol, new_amount, new_avg, now)
                update_balance(user_id, user_balance - total_price)

                await ctx.send(f"{symbol} purchased, you now have {round(new_amount, 2)} {symbol}")
            
            else:
                await ctx.send("Not enough balance to execute this trade")

        else:
            await ctx.send("Bot not initialized. Did you forget to run $start?")

async def setup(bot):
    logging.info("Running Buy cog setup()")
    await bot.add_cog(Buy(bot))