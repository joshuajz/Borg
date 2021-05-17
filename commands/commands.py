import discord
import asyncio
from urlextract import URLExtract
from methods.database import database_connection
from typing import List
from methods.embed import create_embed


async def custom_command_list(ctx) -> list:
    """Returns the list of custom commands."""

    # Database
    db = await database_connection(ctx.guild.id)

    # List of commands
    command_list = [
        i[0] for i in db["db"].execute("SELECT command FROM custom_commands").fetchall()
    ]

    # Length of command list
    command_list_length = len(command_list)

    # If there are custom commands
    if command_list_length >= 1:
        message = ""

        # Iterate through the commands
        for i in range(command_list_length):
            # Add to the message
            message += "!" + command_list[i]
            if i != command_list_length - 1:
                message += "\n"
    else:
        return [
            False,
            "There are currently no commands!  Ask an admin to use !create_command.",
        ]

    return [True, message]


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