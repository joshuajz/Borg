from discord.ext import commands
from discord_slash import cog_ext
from commands.help import help_command


class SlashHelp(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(
        name="help",
        description="Displays the help command.",
    )
    async def _help(self, ctx):
        """/help"""
        await help_command(ctx, self.bot)


def setup(bot):
    bot.add_cog(SlashHelp(bot))
