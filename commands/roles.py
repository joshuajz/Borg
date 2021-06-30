import discord.ext
from methods.database import (
    database_connection,
    role_grab,
    role_check,
    role_add,
    role_find,
    role_remove,
)
from methods.embed import create_embed, add_field, create_embed_template
from methods.paged_command import page_command
from typing import Tuple


async def role_toggle(
    ctx: discord.ext.commands.Context, role: str
) -> Tuple[bool, discord.Embed]:
    """Handling for the !role command

    Args:
        ctx (discord.ext.commands.Context): Context
        role (str): The role's denominator

    Returns:
        Tuple[bool, discord.Embed]: [Status: bool, Embed: discord.Embed]
    """

    # Grab the user's roles
    user_roles = [i.id for i in ctx.author.roles]

    db = await database_connection()

    # Grab this server's role commands
    role_id = await role_grab(ctx.guild.id, db)

    if role_id is None:
        return (
            False,
            create_embed_template(
                "Invalid Role", "Use !roles to see all of the roles.", "error"
            ),
        )

    role_id = role_id[1]

    actual_role = ctx.guild.get_role(role_id)

    if role_id in user_roles:
        # Add the role
        try:
            await ctx.author.remove_roles(actual_role)
        except:
            return (
                False,
                create_embed_template(
                    "No Permission.",
                    "Borg doesn't have permission to add/remove that role.  Ensure Borg's role is **above** the role you're trying to toggle in the server settings (Contact an administrator)",
                    "error",
                ),
            )

        embed = create_embed(
            "Removed Role", f"You removed the {actual_role.mention} role.", "dark_blue"
        )
        return True, embed

    else:
        # Remove the role
        try:
            await ctx.author.add_roles(actual_role)
        except:
            return (
                False,
                create_embed_template(
                    "No Permission.",
                    "Borg doesn't have permission to add/remove that role.  Ensure Borg's role is **above** the role you're trying to toggle in the server settings (Contact an administrator).",
                    "error",
                ),
            )

        embed = create_embed(
            "Added Role", f"You added the {actual_role.mention} role.", "light_green"
        )
        return True, embed


async def roles(
    ctx: discord.ext.commands.Context, bot: discord.ClientUser.bot
) -> Tuple[bool, discord.Embed] or bool:
    """Lists out this server's roles

    Args:
        ctx (discord.ext.commands.Context): Context
        bot (discord.ClientUser.bot): Bot

    Returns:
        Union(bool, discord.Embed): [Status: bool, Embed: discord.Embed]
    """

    db = await database_connection()

    try:
        all_roles = [
            f"!role {i[1]} - {ctx.guild.get_role(i[0]).mention}"
            for i in await role_grab(ctx.guild.id, db)
        ]
    except:
        return (
            False,
            create_embed_template(
                "No Roles",
                "This server has no roles.  Have an administrator run /roles create.",
                "error",
            ),
        )

    if len(all_roles) == 0:
        return (
            False,
            create_embed_template(
                "No Roles",
                "This server has no roles.  Have an administrator run /roles create.",
                "error",
            ),
        )

    await page_command(ctx, bot, all_roles, "Roles")
    return True


async def add_role(ctx: discord.ext.commands.Context, name: str, role_id: int):
    """Adds a role to the database

    Args:
        ctx (discord.ext.commands.Context): Context
        name (str): Name of the role (denominator)
        role_id (int): The role's ID
    """

    if ctx.author.guild_permissions.administrator is False:
        return (
            False,
            create_embed_template(
                "No Permission",
                "You do not have permission to add a role.  Contact an administrator.",
                "error",
            ),
        )

    db = await database_connection()

    if await role_check(ctx.guild.id, role_id, name, db):
        for role in ctx.guild.roles:
            if role.name == "Borg" or role.name == "Borg Test":
                borg_role = {"id": role.id, "position": role.position}

        actual_role = ctx.guild.get_role(role_id)

        if borg_role["position"] > actual_role.position:
            await role_add(ctx.guild.id, role_id, name, db)

            embed = create_embed("Role Added", "", "light_green")
            add_field(embed, "Role", actual_role.mention, True)
            add_field(embed, "Command", f"!role {name}", True)

            return True, embed

        else:
            return (
                False,
                create_embed_template(
                    "Bot Doesn't have Permission.",
                    "The bot does not have permission to give that role to users.  Ensure the bot's role (@Borg) is **ABOVE** the role in the 'Roles' part of your server's dashboard.",
                    "error",
                ),
            )

    else:
        return (
            False,
            create_embed_template(
                "Already Created",
                "There is already a command associated with **either** that role or command name.  Check with !roles.",
                "error",
            ),
        )


async def remove_role(ctx, role_id: int):
    """Removes a role from the database

    Args:
        ctx (discord.ext.commands.Context): Context
        role_id (int): The ID of the role
    """

    if ctx.author.guild_permissions.administrator is False:
        return (
            False,
            create_embed_template(
                "No Permission.",
                "You do not have permission to remove a role.  Ask an administrator.",
                "error",
            ),
        )

    db = await database_connection()

    removal_role = await role_find(ctx.guild.id, role_id=role_id)

    if removal_role is None:
        return (
            False,
            create_embed_template(
                "No Command.",
                "There is no command associated with that role in this server.",
                "error",
            ),
        )

    await role_remove(ctx.guild.id, role_id, db)

    embed = create_embed("Role Removed", "", "dark_blue")

    add_field(
        embed, "Role", f"{ctx.guild.get_role(removal_role['role_id']).mention}", True
    )
    add_field(embed, "Command", f"!role {removal_role['command']}", True)

    return [True, embed]
