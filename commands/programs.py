import discord
from methods.database import database_connection
from embed import create_embed, add_field


async def programs_add(ctx, client, programs: str, user=None) -> list:
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

    # Determines the user to add the programs to
    if user == ctx.author.id:
        user_id = user
    elif user is not None:
        if ctx.author.guild_permissions.administrator == False:
            return [
                False,
                "You do not have permission to add programs for other users.",
            ]
        else:
            user_id = user
    else:
        user_id = ctx.author.id

    # Creates a list of all of the programs
    add_programs = []

    for i in programs.split("\n"):
        [add_programs.append(g.strip()) for g in i.split(",")]

    # Creates an embed
    embed = create_embed("Programs Verification Required", "", "magenta")
    add_field(embed, "User", client.get_user(user_id).mention, False)

    # Message with all of the programs
    programs_msg = ""
    len_programs = len(add_programs)
    for program in range(len_programs):
        programs_msg += (
            add_programs[program] + "\n"
            if program != len_programs - 1
            else add_programs[program]
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
