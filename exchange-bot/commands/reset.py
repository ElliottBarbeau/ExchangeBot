import logging
from discord.ext import commands
from database.cassandra_client import session

class AdminCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="reset")
    @commands.has_permissions(administrator=True)
    async def reset_database(self, ctx):
        tables = [
            "user_portfolio",
            "leverage_portfolio",
            "user_balance",
            "leverage_position_counters"
        ]

        try:
            self.bot.initialized = False
            for table in tables:
                session.execute(f"DROP TABLE IF EXISTS {table}")
            
            await ctx.send("⚠️ **All data wiped!** The database is now empty.")
            logging.warning("Database wiped by admin command.")
        except Exception as e:
            await ctx.send(f"Failed to wipe database: {e}")
            logging.error(f"Database wipe failed: {e}")

async def setup(bot):
    logging.info("Running AdminCommands cog setup()")
    await bot.add_cog(AdminCommands(bot))
