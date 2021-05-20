import discord
from methods.database import database_connection
from methods.embed import create_embed, add_field
from methods.paged_command import page_command


async def role_toggle(ctx, role):
    """The !role {} command."""

    # Grab the user's roles
    user_roles = [i.id for i in ctx.author.roles]

    db = await database_connection(ctx.guild.id)

    # Grab this server's role commands
    role_id = (
        db["db"]
        .execute("SELECT role_id FROM normal_roles WHERE command = (?)", (role,))
        .fetchone()
    )

    if not role_id:
        return [False, "Invalid Roles.  Use !roles to see all of the roles."]

    role_id = role_id[0]

    actual_role = ctx.guild.get_role(role_id)

    if role_id in user_roles:
        # Add the role
        try:
            await ctx.author.remove_roles(actual_role)
        except:
            return [
                False,
                "Borg doesn't have permission to add/remove that role.  Ensure Borg's role is **above** the role you're trying to toggle in the server settings (Contact an administrator).",
            ]

        embed = create_embed(
            "Removed Role", f"You removed the {actual_role.mention} role.", "dark_blue"
        )
        return [True, embed]

    else:
        # Remove the role
        try:
            await ctx.author.add_roles(actual_role)
        except:
            return [
                False,
                "Borg doesn't have permission to add/remove that role.  Ensure Borg's role is **above** the role you're trying to toggle in the server settings (Contact an administrator).",
            ]

        embed = create_embed(
            "Added Role", f"You added the {actual_role.mention} role.", "light_green"
        )
        return [True, embed]


async def roles(ctx, bot):
    """Lists out this server's roles."""

    db = await database_connection(ctx.guild.id)

    all_roles = [
        f"!role {i[1]} - {ctx.guild.get_role(i[0]).mention}"
        for i in db["db"].execute("SELECT * FROM normal_roles").fetchall()
    ]

    if len(all_roles) == 0:
        return [
            False,
            "This server has no roles.  Have an administrator run /roles create.",
        ]

    await page_command(ctx, bot, all_roles, "Roles")
    return True


async def add_role(ctx, name: str, role_id: int):
    """Adds a role to the database."""

    if ctx.author.guild_permissions.administrator != True:
        await ctx.send(
            "You do not have permission to add a role.  Ask an administrator.",
            hidden=True,
        )

    db = await database_connection(ctx.guild.id)

    if role_id not in [
        i[0] for i in db["db"].execute("SELECT role_id FROM normal_roles").fetchall()
    ] and name not in [
        i[0] for i in db["db"].execute("SELECT command FROM normal_roles").fetchall()
    ]:
        for role in ctx.guild.roles:
            if role.name == "Borg" or role.name == "Borg Test":
                borg_role = {"id": role.id, "position": role.position}

        actual_role = ctx.guild.get_role(role_id)

        if borg_role["position"] > actual_role.position:
            db["db"].execute("INSERT INTO normal_roles VALUES (?, ?)", (role_id, name))
            db["con"].commit()

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
    """Removes a role from the database."""

    if ctx.author.guild_permissions.administrator != True:
        await ctx.send(
            "You do not have permission to remove a role.  Ask an administrator.",
            hidden=True,
        )

    db = await database_connection(ctx.guild.id)

    removal_role = (
        db["db"]
        .execute("SELECT * FROM normal_roles WHERE role_id = (?)", (role_id,))
        .fetchall()[0]
    )

    db["db"].execute(
        "DELETE FROM normal_roles WHERE role_id = (?)", (int(removal_role[0]),)
    )
    db["con"].commit()

    embed = create_embed("Role Removed", "", "dark_blue")
    add_field(
        embed, "Role", f"{ctx.guild.get_role(int(removal_role[0])).mention}", True
    )
    add_field(embed, "Command", f"!role {removal_role[1]}", True)

    await ctx.channel.send(embed=embed, hidden=True)
