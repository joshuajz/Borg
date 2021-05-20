import discord
from discord.ext import commands
import sys

sys.path.append("../..")
from commands.help import help_command


class Classic_Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def _help(self, ctx):
        await help_command(ctx, self.bot)


def setup(bot):
    bot.add_cog(Classic_Help(bot))