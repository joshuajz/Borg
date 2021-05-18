import discord
from methods.database import database_connection
from methods.embed import create_embed, add_field
from methods.data import parse_user, parse_channel, find_channel


async def programs_add(ctx, client, programs: list, user: int) -> list:
    """Creates a request to add programs for a user"""

    db = await database_connection(ctx.guild.id)

    # Channel for verification
    programs_channel = (
        db["db"].execute("SELECT programs_channel FROM settings").fetchone()[0]
    )

    if programs_channel is None:
        return [
            False,
            "The admins haven't created a programs channel.  Have an admin run /programs setup.",
        ]

    programs_channel = int(programs_channel)

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

    # Sends the messsage to the verification channel
    verify_channel = client.get_channel(programs_channel)
    verification_msg = await verify_channel.send(embed=embed)

    for emoji in ["✅", "❌"]:
        await verification_msg.add_reaction(emoji)

    return [True, "Programs successfully sent to Moderators.", programs_msg]


async def programs_remove(ctx, programs: str, user=None) -> list:
    """Allows a user to remove programs"""

    # Determines the user id
    if user == ctx.author.id:
        user_id = user
    elif user is not None:
        if ctx.author.guild_permissions.administrator == False:
            return [
                False,
                "You do not have permission to remove programs for other users.",
            ]
        else:
            user_id = user
    else:
        user_id = ctx.author.id

    # Deletes ALL the programs
    if ["*", "all"] in programs.lower():
        db["db"].execute("DELETE FROM programs WHERE user_id = (?)", (user_id,))
        db["con"].commit()

        return [True, "Removed **all** programs successfully."]

    remove_programs = []

    for i in programs.split("\n"):
        [remove_programs.append(g.strip()) for g in i.split(",")]

    # Removes duplicates
    remove_programs = list(dict.fromkeys(remove_programs))

    try:
        remove_programs = [int(i) for i in remove_programs]
    except:
        return [False, "Invalid Removal Value(s) provided."]

    all_programs = {}
    i = 1
    for program in db["db"].execute(
        "SELECT description FROM programs WHERE user_id = (?)",
        (user_id).fetchone().split("\n"),
    ):
        all_programs[i] = program
        i += 1

    new_programs = [
        val for key, val in all_programs.items() if key not in remove_programs
    ]

    # Message with the current programs list
    message = ""
    len_programs = len(new_programs)
    for program in range(len_programs):
        message += (
            new_programs[program] + "\n"
            if program != len_programs - 1
            else add_programs[program]
        )

    db["db"].execute(
        "UPDATE programs SET description = (?) WHERE user_id = (?)", (message, user_id)
    )

    return [True, "Programs Removed Successfully.", description]


async def programs_edit(ctx, client, user, before, after):
    """Edits a user's specific program"""

    # Check
    if user is None:
        return [False, "Invalid Arguments (user was Null)."]

    if before is None or after is None:
        return [False, "Invalid Arguments (before or after)."]

    try:
        before = int(before)
    except:
        return [False, "Invalid 'before' value (ie. not a number)."]

    user = parse_user(user)

    db = await databse_connection(ctx.guild.id)

    # Channel for verification
    programs_channel = (
        db["db"].execute("SELECT programs_channel FROM settings").fetchone()[0]
    )

    if programs_channel is None:
        return [
            False,
            "The admins haven't created a programs channel.  Have an admin run /programs setup.",
        ]

    programs = (
        db["db"]
        .execute("SELECT * FROM programs WHERE user_id = (?)", (user,))
        .fetchone()
    )

    p = {}
    i = 1
    for program in programs:
        p[i] = program
        i += 1

    if before not in p.keys():
        return [False, "You do not have a program with that numerical value."]

    embed = create_embed("Programs (Edit) Verification Required", "", "magenta")
    add_field(embed, "Before", p[before], True)
    add_field(embed, "After", after, True)

    verify_channel = client.get_channel(programs_channel)
    verify_msg = await verify_channel.send(embed=embed)

    for emoji in ["✅", "❌"]:
        await verify_msg.add_reaction(emoji)

    return [True, "Programs successfully sent to the Moderators.", embed]


async def programs(ctx, user: str) -> list:
    """Display's a user's programs"""

    # Check
    if user is None:
        return [False, "Invalid Arguments (user was Null)."]

    # Gets the user's id
    user = parse_user(user)

    db = await database_connection(ctx.guild.id)

    # Grabs all of the programs
    programs_list = (
        db["db"]
        .execute("SELECT * FROM programs WHERE user_id = (?)", (user,))
        .fetchone()
    )

    # Empty list
    if programs_list is None:
        return [
            False,
            "That user doesn't have any programs.  That user needs to use /programs add",
        ]

    programs_list = programs_list.split("\n")

    # Creates the message
    message = ""
    space_amount = (len(programs_list) // 10) + 1
    for i in range(len(programs_list)):
        if programs_list[i] != "" and programs_list[i] is not None:
            # Ensure the numbers line up
            number = f"{i + 1}".rjust(space_amount, "")
            # Only add a newline if it's required
            message += (
                f"{number}. {programs_list[i]}" + "\n"
                if i != (len(programs_list) - 1)
                else ""
            )

    return [True, message]


async def programs_setup(ctx, channel: int):
    """Allows an administrator to setup the moderations channel."""

    if ctx.author.guild_permissions.administrator != True:
        return

    if not channel:
        return [False, "Invalid channel."]

    db = await database_connection(ctx.guild_id)

    db["db"].execute("UPDATE settings SET programs_channel = (?)", (channel,))
    db["con"].commit()

    return ["True", f"Programs Setup Successfully.  Channel: <#{channel}>"]


async def programs_reaction_handling(ctx, client):
    """Handles reaction adding for programs commands."""

    db = await database_connection(ctx.guild_id)

    # Grabs the verification channel
    mod_channel_id = (
        db["db"].execute("SELECT programs_channel FROM settings").fetchone()[0]
    )

    if mod_channel_id is None:
        return False

    mod_channel_id = int(mod_channel_id)

    if mod_channel_id != ctx.channel_id:
        return False

    m = await client.get_channel(ctx.channel_id).fetch_message(ctx.message_id)
    embeds = m.embeds[0]

    reactions = m.reactions

    if not (
        (reactions[0].count == 1 and reactions[1].count == 2)
        or (reactions[0].count == 2 and reactions[1].count == 1)
    ):
        # An administrator/moderator has already reacted, no need to perform the action twice
        return False

    # Deals with programs
    if m.embeds[0].title == "Programs Verification Required":
        if ctx.emoji.name == "❌":
            await m.delete()
            return True
        elif ctx.emoji.name == "✅":
            user_id = parse_user(m.embeds.fields[0].value)

            if not user_id:
                return True

            if (
                db["db"]
                .execute(
                    "SELECT COUNT(user_id) FROM programs WHERE user_id = (?)",
                    (user_id,),
                )
                .fetchone()[0]
                != 1
            ):
                programs = m.embeds.fields[2].value
                await m.delete()

                if not programs:
                    return False

                db["db"].execute(
                    "INSERT INTO programs (user_id, description) VALUES (?, ?)",
                    (user_id, programs),
                )
                db["con"].commit()
            else:
                program_additions = m.embeds.fields[2].value
                await m.delete()

                if not program_additions:
                    return False

                current_programs = (
                    db["db"]
                    .execute(
                        "SELECT description FROM programs WHERE user_id = (?)",
                        (user_id,),
                    )
                    .fetchone()
                )[0]

                current_programs += "\n"

                len_program_additions = len(program_additions)

                for program in len_program_additions:
                    current_programs += program_additions[program] + (
                        "\n" if program + 1 != len_program_additions else ""
                    )

                db["db"].execute(
                    "UPDATE programs SET description = ? WHERE user_id = ?",
                    (current_programs, user_id),
                )
                db["con"].commit()

                user = client.get_user(user_id)
                dm_channel = user.dm_channel
                if dm_channel is None:
                    await user.create_dm()
                    dm_channel = user.dm_channel

                embed = create_embed(
                    "!Programs Command Created Successfully", "", "light_green"
                )
                add_field(embed, "Programs", current_programs, True)

                try:
                    await dm_channel.send(embed=embed)
                except:
                    return True

                return True
    elif m.embeds[0].title == "Programs Edit Verification Required":
        if ctx.emoji.name == "❌":
            await m.delete()
            return True
        elif ctx.emoji.name == "✅":
            user_id = parse_user(m.embeds.fields[0].value)

            if not user_id:
                await m.delete()
                return True

            programs_newmsg = m.embeds.fields[1].value
            program_change = m.embeds.fields[2].value

            await m.delete()

            if not programs_newmsg or not program_change:
                return True

            current_programs = (
                db["db"]
                .execute(
                    "SELECT description FROM programs WHERE user_id = (?)",
                    (user_id,),
                )
                .fetchone()
            )[0]

            programs = {}
            i = 1
            for p in current_programs.split("\n"):
                if programs[i] == program_change:
                    programs[i] = programs_newmsg
                else:
                    programs[i] = p
                i += 1

            final_programs = ""
            p_values = programs.values()
            len_p_values = len(p_values)
            for i in range(len_p_values):
                final_programs += p_values[i] + ("\n" if i + 1 != len_p_values else "")

            db["db"].execute(
                "UPDATE programs SET description = ? WHERE user_id = ?",
                (final_programs, user_id),
            )
            db["con"].commit()

            user = client.get_user(user_id)
            dm_channel = user.dm_channel
            if dm_channel is None:
                await user.create_dm()
                dm_channel = user.dm_channel

            embed = create_embed("!Programs Edit Was Successful", "", "light_green")
            add_field(embed, "Programs", final_programs, True)

            try:
                await dm_channel.send(embed=embed)
            except:
                return True

            return True