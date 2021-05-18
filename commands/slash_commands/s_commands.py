import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from commands.commands import (
    custom_command_list,
    custom_command_add,
    custom_command_remove,
    custom_command_handling,
)
from methods.embed import create_embed


class Slash_Custom_Commands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    guilds = [749360498624954398]

    @cog_ext.cog_subcommand(
        base="command",
        name="list",
        description="Lists all of the server's custom commands.",
        guild_ids=guilds,
    )
    async def _command_list(self, ctx):
        await custom_command_list(self.bot, ctx)

    @cog_ext.cog_subcommand(
        base="command",
        name="add",
        description="Adds a new command to the server (admin only).",
        guild_ids=guilds,
        options=[
            create_option(
                name="name",
                description="The discriminator to call the command.",
                option_type=3,
                required=True,
            ),
            create_option(
                name="description",
                description="The text that will display when the command is called.",
                option_type=3,
                required=True,
            ),
            create_option(
                name="image",
                description="An image link to be displayed",
                option_type=3,
                required=False,
            ),
        ],
    )
    async def _command_add(self, ctx, name, description, image=None):
        command_add = await custom_command_add(ctx, name, description, image)

        await ctx.send(command_add[1])

    @cog_ext.cog_subcommand(
        base="command",
        name="remove",
        description="Removes a command from the server (admin only).",
        guild_ids=guilds,
        options=[
            create_option(
                name="name",
                description="The name of the command to remove.",
                option_type=3,
                required=True,
            )
        ],
    )
    async def _command_remove(self, ctx, remove):
        command_remove = await custom_command_remove(ctx, remove)

        await ctx.send(command_remove[1])

    @cog_ext.cog_subcommand(
        base="command",
        name="use",
        description="Calls one of the custom commands for the server.",
        guild_ids=guilds,
        options=[
            create_option(
                name="name",
                description="The name of the command to call.",
                option_type=3,
                required=True,
            )
        ],
    )
    async def _command_use(self, ctx, command):
        await custom_command_handling(ctx, command)


def setup(bot):
    bot.add_cog(Slash_Custom_Commands(bot))