import discord
import asyncio
from urlextract import URLExtract
from methods.database import database_connection
from typing import List
from methods.embed import create_embed, add_field
from math import ceil


async def custom_command_list(bot, ctx) -> list:
    """Returns the list of custom commands."""

    # Database
    db = await database_connection(ctx.guild.id)

    # List of commands
    command_list = [
        i[0] for i in db["db"].execute("SELECT command FROM custom_commands").fetchall()
    ]

    # Length of command list
    command_list_length = len(command_list)

    message = ""
    if command_list_length >= 1:
        for i in range(command_list_length):
            message += (
                "!" + command_list[i] + ("\n" if i + 1 != command_list_length else "")
            )
    else:
        return [
            False,
            "There are currently no commands!  Ask an admin to use !create_command.",
        ]
    #! Temp
    print(message)
    await custom_commands(ctx, bot, message.split("\n"))
    return [True, message]


async def custom_commands(ctx, bot, commands: list):
    def check(reaction, user):
        return user == ctx.author and str(reaction) in ["◀️", "▶️"]

    commands.sort()

    pages_lists = []
    for i in range(0, len(commands), 20):
        pages_lists.append(commands[i : i + 20])

    if len(pages_lists) == 1:
        l1, l2 = pages_lists[0][0:10], pages_lists[0][10::]
        embed = create_embed("Commands", "", "orange")
        add_field(embed, "List 1:", "\n".join(l1), True)
        if l2:
            add_field(embed, "List 2:", "\n".join(l2), True)
        await ctx.send(embed=embed)
        return

    messages = {}
    i = 1
    for m in pages_lists:
        embed = create_embed("Commands", "", "orange")
        add_field(embed, "List 1:", "\n".join(m[0:10]), True)
        if m[10::]:
            add_field(embed, "List 2:", "\n".join(m[10::]), True)
        messages[i] = embed
        i += 1

    msg = await ctx.send(embed=messages[1])
    await msg.add_reaction("◀️")
    await msg.add_reaction("▶️")

    current_page = 1
    amount_pages = len(messages)

    while True:
        try:
            # Waiting for a reaction to be added
            reaction, user = await bot.wait_for(
                "reaction_add", timeout=60 * 2.5, check=check
            )
            print(current_page, amount_pages, reaction)
            if current_page != amount_pages and str(reaction) == "▶️":
                current_page += 1
                await msg.edit(embed=messages[current_page])
                await msg.remove_reaction(reaction, user)
            elif current_page != 1 and str(reaction) == "◀️":
                current_page -= 1
                await msg.edit(embed=messages[current_page])
                await msg.remove_reaction(reaction, user)
            else:
                await msg.remove_reaction(reaction, user)

        except asyncio.TimeoutError:
            # Timeout over
            await msg.delete()
            break


async def custom_command_add(ctx, name: str, description: str, image: str or None):
    """Adds a command to the database."""
    name = name.lower()
    name = name[1::] if name[0] == "!" else name

    # Permissions check
    if ctx.author.guild_permissions.administrator != True:
        return [False, "You do not have permission to create commands."]

    urls = []
    if image:
        # Checks for an actual photo in "image"
        photo_indicators = (
            "tenor",
            "jpeg",
            "jpg",
            "png",
            "gif",
            "webp",
            "giphy",
            "tiff",
            "nef",
            "cr2",
            "arw",
        )

        # Extracts the urls from the "image" variable
        urls = URLExtract().find_urls(image)

    if len(urls) == 1:
        # Check to ensure the single URL is actually an image
        image = urls[0]
        if not (
            image.startswith("http")
            and set(image.split(".")).intersection(set(photo_indicators))
        ):
            return [
                False,
                "Invalid image supplied.  Make sure your link is to an image.",
            ]
    elif len(urls) == 2:
        # Too many URLs
        return [
            False,
            "You provided too many links!  Borg can only support 1 link per image.",
        ]
    else:
        urls = None

    db = await database_connection(ctx.guild.id)

    # Find all of the current commands
    command_list = [
        i[0][1::]
        for i in db["db"].execute("SELECT command FROM custom_commands").fetchall()
    ]

    # Ensure the current command is unique
    if name in command_list:
        return [False, "There is already a command with that denominator."]

    # Add it to the database
    db["db"].execute(
        "INSERT INTO custom_commands VALUES (?, ?, ?)", (name, description, image)
    )
    db["con"].commit()

    return [True, f"Command Successfully Created!  Run it with !{name}"]


async def custom_command_remove(ctx, command: str) -> list:
    """Removes a custom command from that server's database"""

    # Permissions check
    if ctx.author.guild_permissions.administrator != True:
        return [False, "You do not have permission to create commands."]

    db = await database_connection(ctx.guild.id)

    # Removes the ! from the command -> !hello turns into hello
    if command[0] == "!":
        command = command[1::]

    # Grabs all of the commands
    command_list = [
        i for i in db["db"].execute("SELECT * FROM custom_commands").fetchall()
    ]

    if command in command_list:
        # Grabs the info for the command to be deleted
        command_delete = (
            db["db"]
            .execute("SELECT * FROM custom_commands WHERE command = (?)", (command,))
            .fetchone()
        )

        # Deletes & Commits
        db["db"].execute("DELETE FROM custom_commands WHERE command = (?)", (command,))
        db["con"].commit()

        return [True, "Command Successfully Deleted.", command_delete]
    else:
        return [False, "Invalid Command, check with !commands."]


async def custom_command_handling(ctx, command: str):
    """Handling for custom commands -> Calls the commands"""

    db = await database_connection(ctx.guild.id)

    # List of commands
    command_list = [
        i for i in db["db"].execute("SELECT * FROM custom_commands").fetchall()
    ]

    # Checks
    for c in command_list:
        if command.lower() == c[0]:

            embed = create_embed(f"{command.capitalize()}", f"{c[1]}", "orange")
            if c[2] != None:
                embed.set_image(url=c[2])
            await ctx.channel.send(embed=embed)