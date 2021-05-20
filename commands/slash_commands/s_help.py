import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from commands.help import help_command


class Slash_Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    guilds = [749360498624954398]

    @cog_ext.cog_slash(
        name="help",
        description="Displays the help command.",
        guild_ids=guilds,
    )
    async def _help(self, ctx):
        await help_command(ctx, self.bot)


def setup(bot):
    bot.add_cog(Slash_Help(bot))