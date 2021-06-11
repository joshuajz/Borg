import discord
from discord.ext import commands
import sys

sys.path.append("../..")

from commands.roles import role_toggle, roles


class Classic_Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="roles")
    async def _roles(self, ctx):
        """!roles command"""
        result = await roles(ctx, self.bot)

        if result != True:
            await ctx.send(result[1])

    @commands.command(name="role")
    async def _role(self, ctx, role: str):
        """!role command"""
        result = await role_toggle(ctx, role.lower())

        if result[0] == False:
            await ctx.send(result[1])
        else:
            await ctx.send(embed=result[1])


def setup(bot):
    bot.add_cog(Classic_Roles(bot))
