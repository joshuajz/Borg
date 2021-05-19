import discord
from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from discord_slash.utils.manage_commands import create_option
from commands.roles import role, roles, add_role, remove_role


class Slash_Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    guilds = [749360498624954398]

    @cog_ext.cog_subcommand(
        base="roles",
        name="role",
        description="Allows a user to toggle a role.",
        guild_ids=guilds,
        options=[
            create_option(
                name="role",
                description="The name of the role to toggle, check !roles.",
                option_type=3,
                required=True,
            )
        ],
    )
    async def _roles_role(self, ctx, role):
        await role(ctx, role)

    @cog_ext.cog_subcommand(
        base="roles",
        name="list",
        description="Lists all of this server's roles.",
        guild_ids=guilds,
    )
    async def _roles_list(self, ctx):
        await roles(ctx, self.bot)

    @cog_ext.cog_subcommand(
        base="roles",
        name="create",
        description="Adds a role to this server's list of roles.",
        guild_ids=guilds,
        options=[
            create_option(
                name="name",
                description="The name of the role that users will use to add it.  ie. if you make name 'candy' than users will use !role candy.",
                option_type=3,
                required=True,
            ),
            create_option(
                name="role",
                description="The actual role that will be added.",
                option_type=8,
                required=True,
            ),
        ],
    )
    async def _roles_add(self, ctx, name, role):
        await add_role(ctx, name, role.id)

    @cog_ext.cog_subcommand(
        base="roles",
        name="remove",
        description="Allows a role to be removed from this server's list of roles.",
        guild_ids=guilds,
        options=[
            create_option(
                name="role",
                description="The actual role to remove.",
                option_type=8,
                required=True,
            ),
        ],
    )
    async def _roles_remove(self, ctx, role):
        await remove_role(ctx, role.id)