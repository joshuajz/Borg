import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from methods.data import parse_channel
from commands.programs import programs_add, programs_setup, programs
from methods.embed import create_embed


class Slash_Programs(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    guilds = [749360498624954398]

    @cog_ext.cog_subcommand(
        base="programs",
        name="add",
        description="Adds programs to your programs command.",
        guild_ids=guilds,
        options=[
            create_option(
                name="programs",
                description="A list of comma seperated programs. ie. Queens CS, Queens Math",
                option_type=3,
                required=True,
            ),
            create_option(
                name="user",
                description="Add programs to another user. (admin required)",
                option_type=3,
                required=False,
            ),
        ],
    )
    async def _programs_add(self, ctx, programs, user=None):

        # Determines the user to add the programs to
        if user is not None and ctx.author.guild_permissions.administrator:
            user = parse_channel(user)
        elif user:
            await ctx.send(
                "You do not have permission to add programs for other users."
            )
        else:
            user = ctx.author.id

        # Creates a list of programs
        programs = programs.split(",")
        programs = [i.strip() for i in programs]

        result = await programs_add(ctx, self.bot, programs, user)

        if result[0] == False:
            await ctx.send(result[1], hidden=True)
        else:
            embed = create_embed(
                "Programs Successfully Sent to the Moderators.",
                result[2],
                "light_green",
            )
            await ctx.send(embed=embed, hidden=True)

    @cog_ext.cog_subcommand(
        base="programs",
        name="setup",
        description="Setup the moderation channel.",
        guild_ids=guilds,
        options=[
            create_option(
                name="channel",
                description="The channel for messages to approve.",
                option_type=7,
                required=True,
            )
        ],
    )
    async def _programs_setup(self, ctx, channel):
        if ctx.author.guild_permissions.administrator != True:
            await ctx.send(
                "You cannot run this command as you do not have administrator permissions.  Ask an admin to run /programs setup.",
                hidden=True,
            )

        channel = channel.id

        result = await programs_setup(ctx, channel)

        if result[0] == True:
            embed = create_embed(result[1], result[2], "light_green")
            await ctx.send(embed=embed, hidden=True)
        else:
            await ctx.send(result[1], hidden=True)

    @cog_ext.cog_subcommand(
        base="programs",
        name="programs",
        description="Displays a user's programs.",
        guild_ids=guilds,
        options=[
            create_option(
                name="user",
                description="User's programs you'd like to see.",
                option_type=6,
                required=True,
            )
        ],
    )
    async def _programs(self, ctx, user):
        result = await programs(ctx, user.id)

        if result[0] == True:
            embed = create_embed(f"{user.mention}'s Programs", result[1], True)
            await ctx.send(embed)
        else:
            await ctx.send(result[1])


def setup(bot):
    bot.add_cog(Slash_Programs(bot))