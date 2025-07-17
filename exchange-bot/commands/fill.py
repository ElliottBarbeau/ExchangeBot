import logging

from discord.ext import commands
from database.balance_queries import update_balance, get_balance, create_user_balance

class Fill(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="fill")
    async def fill_command(self, ctx):
        if self.bot.initialized:
            user_id = str(ctx.author.id)
            balance = get_balance(user_id)
            if balance:
                new_balance = balance + 10000.0
                update_balance(user_id, new_balance)
                await ctx.send("Admin filled $10,000")
            else:
                create_user_balance(user_id)
                await ctx.send("User added with initial balance of $10,000")
        else:
            await ctx.send("Bot not initialized. Did you forget to run $start?")

async def setup(bot):
    logging.info("Running Fill cog setup()")
    await bot.add_cog(Fill(bot))