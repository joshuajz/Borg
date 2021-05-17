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
        commands = await custom_command_list(ctx)
        if commands[0]:
            embed = create_embed("Commands", commands[1], "orange")
            await ctx.channel.send(embed=embed)

    @commands.command(name="helpplx")
    async def _help(self, ctx):
        ctx.send("Help")


def setup(bot):
    bot.add_cog(Classic_Custom_Commands(bot))
