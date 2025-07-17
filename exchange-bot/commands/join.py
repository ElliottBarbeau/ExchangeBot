import logging

from discord.ext import commands
from database.balance_queries import create_user_balance, get_balance

class Join(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="join")
    async def join_command(self, ctx):
        if self.bot.initialized:
            user_id = str(ctx.author.id)
            balance = get_balance(user_id)

            if not balance:
                create_user_balance(user_id)
                await ctx.send("User added with initial balance of $10,000")
            else:
                await ctx.send("User already exists! Use $fill to get an admin fill")

        else:
            await ctx.send("Bot not initialized. Did you forget to run $start?")

async def setup(bot):
    logging.info("Running Join cog setup()")
    await bot.add_cog(Join(bot))