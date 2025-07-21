import logging

from discord.ext import commands
from database.balance_queries import get_balance, create_user_balance

class Bal(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="bal")
    async def balance_command(self, ctx):
        if not self.bot.initialized:
            await ctx.send("Bot not initialized. Did you forget to run $start?")
            return
        
        if not get_balance(user_id):
            await ctx.send("User has not joined the game. Type $join to get started!")
            return
        
        user_id = str(ctx.author.id)
        balance = get_balance(user_id)
        await ctx.send(f"Your balance is ${balance:,.2f}")

async def setup(bot):
    logging.info("Running Bal cog setup()")
    await bot.add_cog(Bal(bot))