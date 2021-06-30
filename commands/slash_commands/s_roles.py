from discord.ext import commands
from discord_slash import cog_ext
from discord_slash.utils.manage_commands import create_option
from commands.roles import role_toggle, roles, add_role, remove_role
from methods.embed import create_embed_template
from methods.database import database_connection, role_find


class SlashRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_subcommand(
        base="roles",
        name="role",
        description="Allows a user to toggle a role.",
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
        """/roles role"""
        result = await role_toggle(ctx, role.lower())

        if result is not True:
            await ctx.send(embed=result[1], hidden=True)

    @cog_ext.cog_subcommand(
        base="roles",
        name="list",
        description="Lists all of this server's roles.",
    )
    async def _roles_list(self, ctx):
        result = await roles(ctx, self.bot)

        if result is False:
            await ctx.send(result[1], hidden=True)

    @cog_ext.cog_subcommand(
        base="roles",
        name="create",
        description="Adds a role to this server's list of roles.",
        options=[
            create_option(
                name="name",
                description="The name of the role that users will use to add it.  ie. !role name",
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
        """/roles create"""
        if not name[0].isalpha():
            await ctx.send(
                "Ensure the first letter of your role name is a letter of the alphabet!",
                hidden=True,
            )
            return

        if len(name.split(" ")) >= 2:
            await ctx.send(
                "You cannot have any spaces in the name of your command.", hidden=True
            )
            return

        name = name.lower()

        result = await add_role(ctx, name, role.id)
        await ctx.send(embed=result[1], hidden=True)

    @cog_ext.cog_subcommand(
        base="roles",
        name="remove",
        description="Allows a role to be removed from this server's list of roles.",
        options=[
            create_option(
                name="role_name",
                description="The name of the role in !roles (ie. !hi)",
                option_type=3,
                required=False,
            ),
            create_option(
                name="role",
                description="The actual role to remove.",
                option_type=8,
                required=False,
            ),
        ],
    )
    async def _roles_remove(self, ctx, role_name=None, role=None):
        """/roles remove"""
        if role_name is not None:
            if role_name[0] == "!":
                role_name = role[1::]

            db = await database_connection()
            actual_role = await role_find(ctx.guild.id, db, command=role_name)
            actual_role = actual_role["role_id"]

            if actual_role is None:
                embed = create_embed_template(
                    "You did not provide a proper role command.",
                    "Check all of the role commands with !roles.",
                    "error",
                )
                await ctx.send(embed=embed, hidden=True)
            else:
                result = await remove_role(ctx, actual_role)
                await ctx.send(embed=result[1], hidden=True)
        elif role is not None:
            result = await remove_role(ctx, role.id)
            await ctx.send(embed=result[1], hidden=True)
        else:
            await ctx.send(
                embed=create_embed_template(
                    "You did not provide any values.", "", "error"
                ),
                hidden=True,
            )


def setup(bot):
    bot.add_cog(SlashRoles(bot))
