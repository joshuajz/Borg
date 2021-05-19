import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from commands.welcome import welcome_setup, welcome_toggle


class Slash_Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_subcommand(
        base="welcome",
        name="setup",
        description="Allows an administrator to setup a welcome message.",
        options=[
            create_option(
                name="message",
                description="The message, add {{USER}} in place of the bot @ing someone.",
                option_type=3,
                required=True,
            ),
            create_option(
                name="channel",
                description="The channel to send welcome commands.",
                option_type=7,
                required=True,
            ),
        ],
    )
    async def _welcome_setup(self, ctx, message, channel):
        await welcome_setup(ctx, channel.id, message)

    @cog_ext.cog_subcommand(
        base="welcome",
        name="toggle",
        description="Allows an administrator to turn on/off the welcome messages.",
    )
    async def _welcome_toggle(self, ctx):
        await welcome_toggle(ctx)


def setup(bot):
    bot.add_cog(Slash_Welcome(bot))