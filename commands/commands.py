import discord.ext
from urlextract import URLExtract
from methods.database import Commands_DB
from typing import Tuple
from methods.embed import create_embed, create_embed_template
from methods.paged_command import page_command


async def custom_command_list(
    bot: discord.ClientUser.bot, ctx: discord.ext.commands.Context
):
    """Displays the custom commands.

    Args:
        bot (discord.ClientUser.bot): Bot instance
        ctx (discord.ext.commands.Context): Context for the call

    Returns:
        - bool: Whether the command list was displayed
        - Tuple[bool, discord.Embed]: bool is the status code, embed is the response message
    """

    # Database
    db = await Commands_DB(ctx.guild.id)

    # List of commands
    grab_commands = await db.grab_commands()

    if grab_commands is None:
        return (
            False,
            create_embed_template(
                "No Commands",
                "There are currently no commands, ask an admin to use /command create or !command add.",
                "error",
            ),
        )

    command_list = [i[0] for i in grab_commands]

    # Length of command list
    command_list_length = len(command_list)

    message = ""

    # Display the commands with the denominator
    for i in range(command_list_length):
        message += (
            "!" + command_list[i] + ("\n" if i + 1 != command_list_length else "")
        )

    await page_command(ctx, bot, message.split("\n"), "Commands")

    return True


async def custom_command_add(
    ctx: discord.ext.commands.Context, name: str, description: str, image: str or None
) -> Tuple[bool, discord.Embed]:
    """Adds a command to the database

    Args:
        ctx (discord.ext.commands.Context): Context
        name (str): Name of the command to add
        description (str): Description of the command
        image (str or None): Image link for the command

    Returns:
        Tuple[bool, discord.Embed]: [Status: bool, Embed: discord.Embed]
    """
    name = name.lower()
    name = name[1::] if name[0] == "!" else name

    # Permissions check
    if ctx.author.guild_permissions.administrator is False:
        return (
            False,
            create_embed_template(
                "No Permission",
                "You do not have permission to create a command.",
                "error",
            ),
        )

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
            return (
                False,
                create_embed_template(
                    "Invalid Image", "Make sure your link is to an image.", "error"
                ),
            )
    elif len(urls) == 2:
        # Too many URLs
        return (
            False,
            create_embed_template(
                "Too many Links", "Borg can only support 1 image per command.", "error"
            ),
        )
    else:
        urls = None

    db = await Commands_DB(ctx.guild.id)

    # Find all of the current commands
    grab_commands = await db.grab_commands()

    if grab_commands is not None:
        command_list = [i[0] for i in grab_commands]

        # Ensure the current command is unique
        if name in command_list:
            return (
                False,
                create_embed_template(
                    "Invalid Command Name",
                    "There is already a command with that denominator.",
                    "error",
                ),
            )

    # Add it to the database
    await db.add_command(name, description, image)

    return (
        True,
        create_embed(
            "Success",
            f"Command successfully created, run it with !{name}",
            "light_green",
        ),
    )


async def custom_command_remove(
    ctx: discord.ext.commands.Context, command: str
) -> Tuple[bool, discord.Embed]:
    """Removes a custom command from the server's database

    Args:
        ctx (discord.ext.commands.Context): Context
        command (str): The name of the command to remove

    Returns:
        Tuple[bool, discord.Embed]: [Status: bool, Embed: discord.Embed]
    """

    # Permissions check
    if ctx.author.guild_permissions.administrator is False:
        return (
            False,
            create_embed_template(
                "No Permission",
                "You do not have permission to create commands.",
                "error",
            ),
        )

    db = await Commands_DB(ctx.guild.id)

    # Removes the ! from the command -> !hello turns into hello
    if command[0] == "!":
        command = command[1::]

    # Grabs all of the commands
    grab_commands = await db.grab_commands()
    if grab_commands is None:
        return (
            False,
            create_embed_template(
                "Invalid Command",
                "This server has no commands therefore you cannot remove one.",
                "error",
            ),
        )

    command_list = [i[0] for i in grab_commands]

    if command in command_list:
        # Grabs the info for the command to be deleted
        command_delete = await db.fetch_command(command)

        # Deletes
        await db.remove_command(command)

        return (
            True,
            create_embed(
                "Command Successfully Deleted",
                f"Command Deleted: !{command_delete[0]}",
                "light_green",
            ),
        )
    else:
        return (
            False,
            create_embed_template(
                "Invalid Command", "Check the commands with !commands.", "error"
            ),
        )


async def custom_command_handling(ctx: discord.ext.commands.Context, command: str):
    """Handling for custom commands

    Args:
        ctx (discord.ext.commands.Context): Context
        command (str): The command that was called
    """

    db = await Commands_DB(ctx.guild.id)

    # List of commands
    command_list = await db.grab_commands()

    if command_list is None:
        return

    # Checks
    for c in command_list:
        if command.lower() == c[0]:

            embed = create_embed(f"{command.capitalize()}", f"{c[1]}", "orange")
            if c[2] is not None:
                embed.set_image(url=c[2])
            await ctx.channel.send(embed=embed)
