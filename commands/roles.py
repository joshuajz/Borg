import discord
from methods.database import Guild_Info
from methods.embed import create_embed, add_field
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

    db = Guild_Info(ctx.guild.id)

    # Grab this server's role commands
    role_id = db.grab_role(command=role)

    if role_id is None:
        return (False, "Invalid Roles.  Use !roles to see all of the roles.")

    role_id = role_id[1]

    actual_role = ctx.guild.get_role(role_id)

    if role_id in user_roles:
        # Add the role
        try:
            await ctx.author.remove_roles(actual_role)
        except:
            return (
                False,
                "Borg doesn't have permission to add/remove that role.  Ensure Borg's role is **above** the role you're trying to toggle in the server settings (Contact an administrator).",
            )

        embed = create_embed(
            "Removed Role", f"You removed the {actual_role.mention} role.", "dark_blue"
        )
        return (True, embed)

    else:
        # Remove the role
        try:
            await ctx.author.add_roles(actual_role)
        except:
            return (
                False,
                "Borg doesn't have permission to add/remove that role.  Ensure Borg's role is **above** the role you're trying to toggle in the server settings (Contact an administrator).",
            )

        embed = create_embed(
            "Added Role", f"You added the {actual_role.mention} role.", "light_green"
        )
        return (True, embed)


async def roles(
    ctx: discord.ext.commands.Context, bot: discord.ClientUser.bot
) -> Tuple[bool, discord.Embed]:
    """Lists out this server's roles

    Args:
        ctx (discord.ext.commands.Context): Context
        bot (discord.ClientUser.bot): Bot

    Returns:
        Union(bool, discord.Embed): [Status: bool, Embed: discord.Embed]
    """

    db = Guild_Info(ctx.guild.id)

    try:
        all_roles = [
            f"!role {i[1]} - {ctx.guild.get_role(i[0]).mention}"
            for i in db.grab_roles()
        ]
    except:
        return (
            False,
            "This server has no roles.  Have an administrator run /roles create.",
        )

    if len(all_roles) == 0:
        return (
            False,
            "This server has no roles.  Have an administrator run /roles create.",
        )

    await page_command(ctx, bot, all_roles, "Roles")
    return True


async def add_role(ctx: discord.ext.commands.Context, name: str, role_id: int):
    """Adds a role to the dataabase

    Args:
        ctx (discord.ext.commands.Context): Context
        name (str): Name of the role (denominator)
        role_id (int): The role's ID
    """

    if ctx.author.guild_permissions.administrator != True:
        await ctx.send(
            "You do not have permission to add a role.  Ask an administrator.",
            hidden=True,
        )

    db = Guild_Info(ctx.guild.id)

    if db.check_role(role_id, name):
        for role in ctx.guild.roles:
            if role.name == "Borg" or role.name == "Borg Test":
                borg_role = {"id": role.id, "position": role.position}

        actual_role = ctx.guild.get_role(role_id)

        if borg_role["position"] > actual_role.position:
            db.add_role(role_id, name)

            embed = create_embed("Role Added", "", "light_green")
            add_field(embed, "Role", actual_role.mention, True)
            add_field(embed, "Command", f"!role {name}", True)

            await ctx.send(embed=embed, hidden=True)
        else:
            await ctx.send(
                "The bot does not have permission to give that role to users.  Ensure the bot's role (@Borg) is **ABOVE** the role in the 'Roles' part of your server's dashboard.",
                hidden=True,
            )
    else:
        await ctx.send(
            "There is already a command associated with **either** that role or command name.  Check with !roles."
        )


async def remove_role(ctx, role_id: int):
    """Removes a role from the database

    Args:
        ctx (discord.ext.commands.Context): Context
        role_id (int): The ID of the role
    """

    if ctx.author.guild_permissions.administrator != True:
        await ctx.send(
            "You do not have permission to remove a role.  Ask an administrator.",
            hidden=True,
        )

    db = Guild_Info(ctx.guild.id)

    removal_role = db.grab_role(role_id=role_id)

    if removal_role is None:
        await ctx.channel.send(
            "There is no command associated with that role in this server.", hidden=True
        )
        return

    db.remove_role(role_id)

    embed = create_embed("Role Removed", "", "dark_blue")
    add_field(
        embed, "Role", f"{ctx.guild.get_role(int(removal_role[1])).mention}", True
    )
    add_field(embed, "Command", f"!role {removal_role[2]}", True)

    await ctx.channel.send(embed=embed, hidden=True)
