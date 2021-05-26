import discord
from discord.ext import commands
import sys

sys.path.append("../..")

from commands.commands import custom_command_list, custom_command_add
from methods.embed import create_embed


class Classic_Custom_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="commands")
    async def _commands(self, ctx):
        result = await custom_command_list(self.bot, ctx)

        if result != True:
            await ctx.send(result[1])

    @commands.command(name="command")
    async def _command(self, ctx):
        # ex: !command add
        msg = ctx.message.content.split(" ")
        if len(msg) >= 4 and msg[1] == "add":
            image = None
            command = msg[2].replace("!", "")
            if msg[-1].startswith("http"):
                image = msg[-1]
                description = " ".join(msg[2:-1])
            else:
                description = " ".join(msg[2::])

            result = await custom_command_add(ctx, command, description, image)

            await ctx.send(result[1])

        else:
            embed = create_embed(
                "Command: !command",
                "**Description**: Allows you to manage the server's custom commands.\n**Sub Commands**:\n!command add - Adds a command\n**Usage**:\n!command add !hello Hello everyone how are you https://google.com/image.png\n!command add !hi Hello how are you?",
                "orange",
            )
            await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Classic_Custom_Commands(bot))
