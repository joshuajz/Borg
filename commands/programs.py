import discord.ext
from methods.database import (
    database_connection,
    settings_grab,
    program_delete,
    program_grab,
    program_update,
    settings_update,
)
from methods.embed import create_embed, add_field, create_embed_template
from methods.data import parse_id
from typing import Tuple


async def programs_add(
    ctx: discord.ext.commands.Context,
    client: discord.ClientUser.bot,
    programs: list,
    user: int,
) -> Tuple[bool, discord.Embed]:
    """Creates a request to add programs for a user

    Args:
        ctx (discord.ext.commands.Context): Context
        client (discord.ClientUser.bot): Discord Bot
        programs (list): List of programs to add
        user (int): User's ID to add

    Returns:
        Tuple(bool, discord.Embed): [Status: bool, Embed: discord.Embed]
    """

    db = await database_connection()

    # Channel for verification
    settings = await settings_grab(ctx.guild.id, db)

    if settings is None or settings["programs_channel"] is None:
        return (
            False,
            create_embed_template(
                "No Programs Channel",
                "The admins haven't created a programs channel.  Have an admin run /programs setup.",
                "error",
            ),
        )

    programs_channel = settings["programs_channel"]

    # Creates an embed
    embed = create_embed("Programs Verification Required", "", "magenta")
    add_field(embed, "User", client.get_user(user).mention, False)

    # Message with all of the programs
    programs_msg = ""
    len_programs = len(programs)
    for program in range(len_programs):
        programs_msg += (
            programs[program] + "\n"
            if program != len_programs - 1
            else programs[program]
        )

    add_field(embed, "Program Additions", programs_msg, True)

    # Sends the message to the verification channel
    verify_channel = client.get_channel(programs_channel)
    verification_msg = await verify_channel.send(embed=embed)

    # Adds the verification emoji
    for emoji in ["✅", "❌"]:
        await verification_msg.add_reaction(emoji)

    return (
        True,
        create_embed(
            "Programs successfully sent to Moderators.", programs_msg, "light_green"
        ),
    )


async def programs_remove(
    ctx: discord.ext.commands.Context, programs: str, user=None
) -> Tuple[bool, discord.Embed]:
    """Allows a user to remove programs

    Args:
        ctx (discord.ext.commands.Context): Context
        programs (str): The programs to remove
        user (int, optional): The user ID to remove programs from. Defaults to None.

    Returns:
        Tuple[bool, discord.Embed]: [Status: bool, Embed: discord.Embed]
    """

    # Determines the user id
    if user == ctx.author.id:
        user_id = user
    elif user is not None:
        if ctx.author.guild_permissions.administrator is False:
            return (
                False,
                create_embed_template(
                    "No Permission",
                    "You do not have permission to remove programs for other users.",
                    "error",
                ),
            )

        else:
            user_id = user
    else:
        user_id = ctx.author.id

    db = await database_connection()

    # Deletes ALL the programs
    if programs.lower() in ["*", "all"]:
        await program_delete(ctx.guild.id, user_id, db)

        return (
            True,
            create_embed("Removed **all** program successfully.", "", "light_green"),
        )

    remove_programs = []

    for i in programs.split("\n"):
        [remove_programs.append(g.strip()) for g in i.split(",")]

    # Removes duplicates
    remove_programs = list(dict.fromkeys(remove_programs))
    try:
        remove_programs = [int(i) for i in remove_programs]
    except ValueError:
        return (
            False,
            create_embed_template(
                "Invalid Values",
                "Invalid removal values were provided.  Provide a number corrosponding to the program(s) you would like to remove.",
                "error",
            ),
        )

    # All programs
    all_programs = {}
    i = 1
    for program in (await program_grab(user_id, ctx.guild.id, db)).split("\n"):
        all_programs[i] = program
        i += 1

    # New list w/o removals
    new_programs = [
        val for key, val in all_programs.items() if key not in remove_programs
    ]

    if len(new_programs) == 0:
        await db.delete_all_programs(user_id)

        return (
            True,
            create_embed(
                "Programs removed Successfully.",
                "You now have no programs!",
                "light_green",
            ),
        )

    # Message with the current programs list
    message = ""
    len_programs = len(new_programs)
    for program in range(len_programs):
        message += new_programs[program] + ("\n" if program != len_programs - 1 else "")

    await program_update(ctx.guild.id, user_id, message, db)

    return (
        True,
        create_embed(
            "Programs Removed Successfully.",
            f"**Current Programs**:\n {message}"
            if message
            else f"All of your programs have been removed.",
            "light_green",
        ),
    )


async def programs_edit(
    ctx: discord.ext.commands.Context,
    client: discord.ClientUser.bot,
    user: int,
    before: str,
    after: str,
) -> Tuple[bool, discord.Embed]:
    """Edits one of a user's programs

    Args:
        ctx (discord.ext.commands.Context): Context
        client (discord.ClientUser.bot): Bot instance
        user (int): User's ID
        before (str): The program to edit
        after (str): The new text to replace the program

    Returns:
        Tuple[bool, discord.Embed]: [Status: bool, Embed: discord.Embed]
    """

    # Check user
    if user is None:
        return (
            False,
            create_embed_template("Invalid Arguments", "User was null.", "error"),
        )

    # Check before and after
    if before is None or after is None:
        return (
            False,
            create_embed_template(
                "Invalid Arguments", "*Before* or *after* value is invalid.", "error"
            ),
        )

    try:
        before = int(before)
    except ValueError:
        return (
            False,
            create_embed_template(
                "Invalid Arguments",
                "*Before* value is invalid (not a number).",
                "error",
            ),
        )

    user = parse_id(user)

    db = await database_connection()

    # Channel for verification
    settings = await settings_grab(ctx.guild.id, db)
    if settings is None or settings["programs_channel"] is None:
        return (
            False,
            create_embed_template(
                "Invalid Channel",
                "The admins haven't created a programs channel.  Have an admin run /programs setup.",
                "error",
            ),
        )

    programs_channel = settings["programs_channel"]

    programs = (await program_grab(user, ctx.guild.id, db)).split("\n")

    # Entire programs list
    p = {}
    i = 1
    for program in programs:
        p[i] = program
        i += 1

    if before not in p.keys():
        return (
            False,
            create_embed_template(
                "Invalid Program",
                "You do not have a program with that *before* value.",
                "error",
            ),
        )

    # Create a verification Embed
    embed = create_embed("Programs (Edit) Verification Required", "", "magenta")
    add_field(embed, "User", f"{(await client.fetch_user(user)).mention}", True)
    add_field(embed, "Before", p[before], True)
    add_field(embed, "After", after, True)

    verify_channel = client.get_channel(int(programs_channel))
    verify_msg = await verify_channel.send(embed=embed)

    # Add emojis
    for emoji in ["✅", "❌"]:
        await verify_msg.add_reaction(emoji)

    embed = create_embed(
        "Program Edit successfully sent to the moderators.", "", "light_green"
    )
    add_field(embed, "Before", p[before], True)
    add_field(embed, "After", after, True)

    return True, embed


async def programs(ctx, bot, user: str) -> Tuple[bool, discord.Embed]:
    """Display's a user's programs

    Args:
        ctx (discord.ext.commands.Context): Context
        bot (discord.ClientUser.bot): Bot
        user (str): User's programs to display

    Returns:
        Tuple[bool, discord.Embed]: [Status: bool, Embed: discord.Embed]
    """

    # Check
    if user is None:
        return (
            False,
            create_embed_template("Invalid Arguments", "User was Null.", "error"),
        )

    # Gets the user's id
    user = parse_id(user)

    db = await database_connection()

    # Grabs all of the programs
    programs_list = await program_grab(user, ctx.guild.id, db)

    # Empty list
    if programs_list is None:
        return (
            False,
            create_embed_template(
                "Invalid User",
                "That user doesn't have any programs, have them use /programs add.",
                "error",
            ),
        )

    programs_list = programs_list.split("\n")

    # Creates the message
    message = ""
    space_amount = (len(programs_list) // 10) + 1
    for i in range(len(programs_list)):
        if programs_list[i] != "" and programs_list[i] is not None:
            # Ensure the numbers line up
            number = f"{i + 1}".rjust(space_amount, " ")
            # Only add a newline if it's required
            message += f"{number}. {programs_list[i]}" + (
                "\n" if i != (len(programs_list) - 1) else ""
            )

    user = bot.get_user(user)

    return (
        True,
        create_embed(f"{user.name}#{user.discriminator}'s Programs", message, "orange"),
    )


async def programs_setup(
    ctx: discord.ext.commands.Context, channel: int
) -> Tuple[bool, discord.Embed]:
    """Allows an administrator to setup a programs channel

    Args:
        ctx (discord.ext.commands.Context): Context
        channel (int): The channel for programs verification commands

    Returns:
        Tuple[bool, discord.Embed]: [Status: bool, Embed: discord.Embed]
    """

    if ctx.author.guild_permissions.administrator is False:
        return False, create_embed_template(
            "Invalid Permissions",
            "You do not have permission to setup programs.",
            "error",
        )

    if not channel:
        return False, create_embed_template(
            "Invalid Channel", "You provided an invalid channel.", "error"
        )

    db = await database_connection()
    await settings_update(ctx.guild.id, "programs_channel", channel, db)

    return True, create_embed(
        f"Programs Setup Successfully.", f"Channel: <#{channel}>", "light_green"
    )


async def programs_reaction_handling(
    ctx: discord.RawReactionActionEvent, client: discord.ClientUser.bot
) -> bool:
    """Handles Reactions for programs verification

    Args:
        ctx (discord.ext.commands.Context): Context
        client (discord.ClientUser.bot): Bot

    Returns:
        bool: If it was a programs related reaction
    """

    db = await database_connection()

    # Grabs the verification channel
    settings = await settings_grab(ctx.guild_id, db)
    if settings is None or settings["programs_channel"] is None:
        return False

    mod_channel_id = settings["programs_channel"]

    if mod_channel_id != ctx.channel_id:
        return False

    # Grabs the message & embeds
    m = await client.get_channel(ctx.channel_id).fetch_message(ctx.message_id)
    embeds = m.embeds[0]

    reactions = m.reactions

    # Checks to ensure no one else has already added the reactions
    if not (
        (reactions[0].count == 1 and reactions[1].count == 2)
        or (reactions[0].count == 2 and reactions[1].count == 1)
    ):
        # An administrator/moderator has already reacted, no need to perform the action twice
        return False

    # Deals with programs
    if m.embeds[0].title == "Programs Verification Required":
        if ctx.emoji.name == "❌":
            # Delete
            await m.delete()
            return True
        elif ctx.emoji.name == "✅":
            user_id = parse_id(embeds.fields[0].value)

            if not user_id:
                return True

            # Checks to see if the user already has a programs list

            # If they don't
            count = await db.programs_check_exist(
                user_id,
            )

            if count != 1:
                # Delete the message
                programs = embeds.fields[1].value
                await m.delete()

                if not programs:
                    return False

                # Add the programs
                await db.add_programs(user_id, programs)

            # If they do
            else:
                # Delete the message
                program_additions = embeds.fields[1].value.split("\n")
                await m.delete()

                if not program_additions:
                    return False

                # Grabs the current programs
                current_programs = await program_grab(user_id, ctx.guild_id, db)

                current_programs += "\n"

                # Adds the additions
                len_program_additions = len(program_additions)

                for program in range(len_program_additions):
                    current_programs += program_additions[program] + (
                        "\n" if program + 1 != len_program_additions else ""
                    )

                # Updates the database to the newer longer version
                await program_update(ctx.guild_id, user_id, current_programs, db)

                # Grabs the user & makes a DM channel
                user = client.get_user(user_id)
                dm_channel = user.dm_channel
                if dm_channel is None:
                    await user.create_dm()
                    dm_channel = user.dm_channel

                # Sends an embed w/ the new programs
                embed = create_embed(
                    "!Programs Command Created Successfully", "", "light_green"
                )
                add_field(embed, "Programs", current_programs, True)

                try:
                    await dm_channel.send(embed=embed)
                except Exception as e:
                    return True

                return True
    elif m.embeds[0].title == "Programs (Edit) Verification Required":
        if ctx.emoji.name == "❌":
            # Delete
            await m.delete()
            return True
        elif ctx.emoji.name == "✅":
            # User
            user_id = parse_id(embeds.fields[0].value)

            if not user_id:
                await m.delete()
                return True

            # New addition & Current
            program_change = embeds.fields[1].value
            programs_newmsg = embeds.fields[2].value

            # Delete
            await m.delete()

            # Invalid
            if not programs_newmsg or not program_change:
                return True

            # Grabs current programs
            current_programs = await program_grab(user_id, ctx.guild_id, db)

            # All programs into a dictionary
            programs = {}
            i = 1
            for p in current_programs.split("\n"):

                if p == program_change:
                    programs[i] = programs_newmsg
                else:
                    programs[i] = p
                i += 1

            # Creates a message w/ the programs
            final_programs = ""
            p_values = list(programs.values())
            len_p_values = len(p_values)
            for i in range(len_p_values):
                final_programs += p_values[i] + ("\n" if i + 1 != len_p_values else "")

            # Update in the databse
            await program_update(ctx.guild_id, user_id, final_programs, db)

            # Open a DM
            user = client.get_user(user_id)
            dm_channel = user.dm_channel
            if dm_channel is None:
                await user.create_dm()
                dm_channel = user.dm_channel

            # Send a status message
            embed = create_embed("Programs Edit Was Successful", "", "light_green")
            add_field(embed, "Programs", final_programs, True)

            try:
                await dm_channel.send(embed=embed)
            except:
                return True

            return True
