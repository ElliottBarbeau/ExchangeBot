import logging

from discord.ext import commands
from database.pnl_queries import get_pnl

class Pnl(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="pnl")
    async def pnl_command(self, ctx):
        if not self.bot.initialized:
            await ctx.send("Bot not initialized. Did you forget to run $start?")
            return
        
        user_id = str(ctx.author.id)
        pnl = get_pnl(user_id)
        if pnl is not None:
            await ctx.send(f"Your realized PnL is ${pnl:,.2f}")
        else:
            await ctx.send("User hasn't joined the game. Try $join to enable trading.")

async def setup(bot):
    logging.info("Running Pnl cog setup()")
    await bot.add_cog(Pnl(bot))