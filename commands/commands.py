import discord
import asyncio
from urlextract import URLExtract
from methods.database import database_connection
from typing import List
from methods.embed import create_embed, create_embed_template
from methods.paged_command import page_command


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
            create_embed_template(
                "No Commands",
                "There are currently no commands, ask an admin to use /commands create or !commands add.",
                "error",
            ),
        ]

    await page_command(ctx, bot, message.split("\n"), "Commands")

    return True


async def custom_command_add(ctx, name: str, description: str, image: str or None):
    """Adds a command to the database."""
    name = name.lower()
    name = name[1::] if name[0] == "!" else name

    # Permissions check
    if ctx.author.guild_permissions.administrator != True:
        return [
            False,
            create_embed_template(
                "No Permission",
                "You do not have permission to create a command.",
                "error",
            ),
        ]

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
                create_embed_template(
                    "Invalid Image", "Make sure your link is to an image.", "error"
                ),
            ]
    elif len(urls) == 2:
        # Too many URLs
        return [
            False,
            create_embed_template(
                "Too many Links", "Borg can only support 1 image per command.", "error"
            ),
        ]
    else:
        urls = None

    db = await database_connection(ctx.guild.id)

    # Find all of the current commands
    command_list = [
        i[0] for i in db["db"].execute("SELECT command FROM custom_commands").fetchall()
    ]

    # Ensure the current command is unique
    if name in command_list:
        return [False, "There is already a command with that denominator."]

    # Add it to the database
    db["db"].execute(
        "INSERT INTO custom_commands VALUES (?, ?, ?)", (name, description, image)
    )
    db["con"].commit()

    return [
        True,
        create_embed(
            "Success",
            f"Command successfully created, run it with !{name}",
            "light_green",
        ),
    ]


async def custom_command_remove(ctx, command: str) -> list:
    """Removes a custom command from that server's database"""

    # Permissions check
    if ctx.author.guild_permissions.administrator != True:
        return [
            False,
            create_embed_template(
                "No Permission",
                "You do not have permission to create commands.",
                "error",
            ),
        ]

    db = await database_connection(ctx.guild.id)

    # Removes the ! from the command -> !hello turns into hello
    if command[0] == "!":
        command = command[1::]

    # Grabs all of the commands
    command_list = [
        i[0] for i in db["db"].execute("SELECT command FROM custom_commands").fetchall()
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

        return [
            True,
            create_embed(
                "Command Successfully Deleted", f"Command Deleted: {command_delete}"
            ),
        ]
    else:
        return [
            False,
            create_embed_template(
                "Invalid Command", "Check the commands with !commands.", "error"
            ),
        ]


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