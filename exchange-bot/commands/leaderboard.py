import logging
from discord.ext import commands
from database.pnl_queries import get_pnl_leaderboard

class Leaderboard(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="leaderboard")
    async def leaderboard_command(self, ctx, top: int = 3):
        if top <= 0 or top > 50:
            await ctx.send("Please request between 1 and 50 top users.")
            return
        
        try:
            leaderboard = get_pnl_leaderboard(limit=top)
            if not leaderboard:
                await ctx.send("No PnL data available.")
                return

            embed = commands.Embed(title="PnL Leaderboard", color=0x00ff00)
            description = ""
            for rank, (user_id, pnl) in enumerate(leaderboard, start=1):
                member = ctx.guild.get_member(int(user_id))
                display_name = member.display_name if member else f"User {user_id}"
                description += f"**{rank}. {display_name}** — PnL: ${pnl:,.2f}\n"

            embed.description = description
            await ctx.send(embed=embed)

        except Exception as e:
            logging.error(f"Error fetching leaderboard: {e}")
            await ctx.send("An error occurred while fetching the leaderboard.")

async def setup(bot):
    logging.info("Running Leaderboard cog setup()")
    await bot.add_cog(Leaderboard(bot))
