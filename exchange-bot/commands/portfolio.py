import logging
import discord

from discord.ext import commands
from database.portfolio_queries import get_full_portfolio
from cmc_interface import get_price

class Portfolio(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="portfolio")
    async def portfolio_command(self, ctx):
        if self.bot.initialized:
            user_id = str(ctx.author.id)
            portfolio = get_full_portfolio(user_id)
            if not portfolio:
                await ctx.send("Portfolio empty. Use $buy to purchase something first!")
                return
            
            embed = discord.Embed(
                title=f"{ctx.author.display_name}'s Portfolio",
                color = discord.Color.gold()
            )

            total_symbols = 0
            pnl, total_cost, total_value = 0, 0, 0
            for row in portfolio:
                symbol = row.symbol.upper()
                cost = row.avg_price * row.amount
                total_cost += cost
                value = get_price(symbol) * row.amount
                total_value += value
                amount = row.amount
                avg_price = row.avg_price
                pnl += value - cost
                
                amount = round(amount, 2)
                avg_price = round(avg_price, 2)
                value = round(value, 2)
                cost = round(cost, 2)

                embed.add_field(
                    name = f"💠 {symbol}",
                    value = f"Amount: `{amount}`\nAvg Price: `${avg_price}`\nValue: `${value}`\nCost: `${cost}`",
                    inline = False
                )
                total_symbols += 1

            pnl_sign = "📈" if pnl >= 0 else "📉"
            embed.add_field(
                name="Portfolio Summary",
                value=f"Total Value: `${round(total_value, 2)}`\n"
                      f"PnL: {pnl_sign} `${round(pnl, 2)}`",
                inline=False
            )

            embed.set_footer(text=f"Total positions: {total_symbols}")
            await ctx.send(embed=embed)

                
        else:
            await ctx.send("Bot not initialized. Did you forget to run $start?")

async def setup(bot):
    logging.info("Running Portfolio cog setup()")
    await bot.add_cog(Portfolio(bot))