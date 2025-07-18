import logging

from discord.ext import commands
from database.portfolio_queries import create_portfolio_table
from database.balance_queries import create_balance_table
from database.leverage_queries import create_leverage_table, create_leverage_counter_table
from database.pnl_queries import create_pnl_table

class Start(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="start")
    async def start_command(self, ctx):
        create_portfolio_table()
        create_balance_table()
        create_leverage_table()
        create_leverage_counter_table()
        create_pnl_table()

        self.bot.initialized = True
        await ctx.send("Database initialized and trading enabled.")

async def setup(bot):
    logging.info("Running Start cog setup()")
    await bot.add_cog(Start(bot))