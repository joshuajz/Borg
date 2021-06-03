import discord
from discord.ext import commands
import sys

sys.path.append("../..")

from commands.commands import (
    custom_command_list,
    custom_command_add,
    custom_command_remove,
)
from methods.embed import create_embed


class Classic_Custom_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="commands")
    async def _commands(self, ctx):
        """!commands -> Lists all of the commands."""
        result = await custom_command_list(self.bot, ctx)

        if result != True:
            await ctx.send(embed=result[1])

    @commands.command(name="command")
    async def _command(self, ctx):
        """Classic Commands for the rest of the commands -> !commands add, !commands remove"""
        msg = ctx.message.content.split(" ")

        # Invalid Arguments for the commands -> Display them all
        if len(msg) == 1:
            embed = create_embed(
                "Command: !command",
                "**Description**: Allows you to manage commands.\n**Sub Commands**:\n!command add - Adds a command\n!command remove - Removes a command\n!commands - Lists the commands.\n!commands setup - Allows an admin to setup a programs confirmation channel.",
                "orange",
            )
            await ctx.send(embed=embed)
        else:
            # Subcommand (ie. !commands add -> subcommand = add)
            subcommand = msg[1].strip()
            if subcommand == "add" or subcommand == "a":
                # ex: !command add hello hello

                # We have enough arguments for adding a command
                if len(msg) >= 4:
                    command = msg[2][1::] if msg[2][0] == "!" else msg[2]
                    if msg[-1].startswith("image="):
                        image = msg[-1].split("image=")[1]
                        description = " ".join(msg[3:-1])
                    else:
                        image = None
                        description = " ".join(msg[3::])

                    result = await custom_command_add(ctx, command, description, image)
                    await ctx.send(embed=result[1])
                else:
                    embed = create_embed(
                        "Command: !command add",
                        "**Description**: Allows you to add a command.\n**Usage**:\n!command add !command_name command's description goes here image=linktoimg\n!command add !hello Hello image=https://google.com/image.png\n!command add hi Hello how are you?",
                        "orange",
                    )
                    await ctx.send(embed=embed)
            elif subcommand == "remove" or subcommand == "r":
                #: !command remove hello
                if len(msg) == 3:
                    command = msg[2][1::] if msg[2][0] == "!" else msg[2]
                    result = await custom_command_remove(ctx, command)
                    await ctx.send(embed=result[1])
                else:
                    embed = create_embed(
                        "Command: !command remove",
                        "**Description**: Allows you to remove a command.\n**Usage**:\n!command remove command_name\n!command remove !command_name\n!command remove hi",
                        "orange",
                    )
                    await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Classic_Custom_Commands(bot))
