import logging

from discord.ext import commands
from database.balance_queries import get_balance

class Bal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="bal")
    async def balance_command(self, ctx):
        user_id = str(ctx.author.id)
        if not self.bot.initialized:
            await ctx.send("Bot not initialized. Did you forget to run $start?")
            return
        
        balance = get_balance(user_id)
        
        if balance is None:
            await ctx.send("User has not joined the game. Type $join to get started!")
            return
        
        await ctx.send(f"Your balance is ${balance:,.2f}")

async def setup(bot):
    logging.info("Running Bal cog setup()")
    await bot.add_cog(Bal(bot))