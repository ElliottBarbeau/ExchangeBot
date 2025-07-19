import logging
import discord

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

            embed = discord.Embed(title="PnL Leaderboard", color=0x00ff00)
            for rank, (user_id, pnl) in enumerate(leaderboard):
                user = await ctx.bot.fetch_user(int(user_id))
                username = user.name if user else user_id
                if rank == 1:
                    embed.add_field(
                        name=f"#{rank + 1} 👑 {username}",
                        value=(
                            f"PnL: `{'+' if pnl >= 0 else ''}{pnl:,.2f}`"
                        ),
                        inline=False
                    )
                else:
                    embed.add_field(
                        name=f"#{rank + 1} 🐀 {username}",
                        value=(
                            f"PnL: `{'+' if pnl >= 0 else ''}{pnl:,.2f}`"
                        ),
                        inline=False
                    )

            await ctx.send(embed=embed)

        except Exception as e:
            logging.error(f"Error fetching leaderboard: {e}")
            await ctx.send("An error occurred while fetching the leaderboard.")

async def setup(bot):
    logging.info("Running Leaderboard cog setup()")
    await bot.add_cog(Leaderboard(bot))
