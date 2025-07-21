import logging

from discord.ext import commands
from database.balance_queries import create_user_balance, get_balance
from database.pnl_queries import create_user_pnl

class Join(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="join")
    async def join_command(self, ctx):
        if not self.bot.initialized:
            await ctx.send("Bot not initialized. Did you forget to run $start?")
            return
        
        user_id = str(ctx.author.id)
        balance = get_balance(user_id)

        if balance is None:
            create_user_balance(user_id)
            create_user_pnl(user_id)
            await ctx.send("User added with initial balance of $10,000")
        else:
            await ctx.send("User already exists! Use $fill to get an admin fill")

async def setup(bot):
    logging.info("Running Join cog setup()")
    await bot.add_cog(Join(bot))