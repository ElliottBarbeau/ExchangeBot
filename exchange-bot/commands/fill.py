import logging

from discord.ext import commands
from database.balance_queries import update_balance, get_balance, create_user_balance
from database.pnl_queries import create_user_pnl

class Fill(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="fill")
    async def fill_command(self, ctx):
        if not self.bot.initialized:
            await ctx.send("Bot not initialized. Did you forget to run $start?")
            return

        FILL_AMOUNT = 10000
        user_id = str(ctx.author.id)
        balance = get_balance(user_id)

        if balance is None:
            await ctx.send("User has not joined the game. Type $join to get started!")
            return
        
        if balance:
            new_balance = balance + FILL_AMOUNT
            update_balance(user_id, new_balance)
            await ctx.send(f"Admin filled {FILL_AMOUNT:,.2f}")
        else:
            create_user_pnl(user_id)
            create_user_balance(user_id, FILL_AMOUNT)
            await ctx.send(f"User added with initial balance of {FILL_AMOUNT:,.2f}")
            

async def setup(bot):
    logging.info("Running Fill cog setup()")
    await bot.add_cog(Fill(bot))