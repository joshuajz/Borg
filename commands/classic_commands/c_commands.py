import discord
from discord.ext import commands
import sys

sys.path.append("../..")

from commands.commands import custom_command_list
from methods.embed import create_embed


class Classic_Custom_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="commands")
    async def _commands(self, ctx):
        await custom_command_list(self.bot, ctx)


def setup(bot):
    bot.add_cog(Classic_Custom_Commands(bot))
