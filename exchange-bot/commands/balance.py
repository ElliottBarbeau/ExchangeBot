import logging

from discord.ext import commands
from database.balance_queries import get_balance, create_user_balance

class Balance(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="balance")
    async def balance_command(self, ctx):
        if self.bot.initialized:
            user_id = str(ctx.author.id)
            balance = get_balance(user_id)
            if balance:
                await ctx.send(f"Your balance is ${round(balance, 2)}")
            else:
                create_user_balance(user_id)
                await ctx.send("User added with initial balance of $10,000")
        else:
            await ctx.send("Bot not initialized. Did you forget to run $start?")

async def setup(bot):
    logging.info("Running Balance cog setup()")
    await bot.add_cog(Balance(bot))