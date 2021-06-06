import discord
import datetime
import enum


class embedColours(enum.Enum):
    """Colours for embeds"""

    red = 0xB30012
    orange = 0xFF7B00
    light_green = 0x1DBF38
    dark_blue = 0x1D58BF
    magenta = 0xA832A4
    cyan = 0x28C0D4


def create_embed_template(title: str, description: str, template: str) -> discord.Embed:
    """Creates an embed from a template

    Args:
        title (str): Title of the embed
        description (str): Description of the embed
        template (str): Which template to use

    Returns:
        discord.Embed: The embed with the given information
    """

    if template.lower() == "error":
        message = discord.Embed(
            title=title,
            description=description,
            colour=embedColours["red"].value,
            timestamp=datetime.datetime.utcnow(),
        )
        message.set_footer(
            text="Contact JZ#7252 with bugs.",
            icon_url="https://art.pixilart.com/a212f48d4198f72.png",
        )
    return message


def create_embed(
    title: str, description: str, colour: str, footer="contact", thumbnail=None
) -> discord.Embed:
    """Creates an embed object

    Args:
        title (str): Title of the embed
        description (str): Description of the embed
        colour (str): The colour (reference enmbedColours)
        footer (str, optional): An optional footer. Defaults to "contact".
        thumbnail (str, optional): An optional thumbnail image (link). Defaults to None.

    Returns:
        discord.Embed: Embed with the given information
    """

    message = discord.Embed(
        title=title,
        description=description,
        colour=embedColours[colour].value,
        timestamp=datetime.datetime.utcnow(),
    )

    if thumbnail is not None:
        message.set_thumbnail(url=thumbnail)

    if footer == "contact":
        message.set_footer(
            text="Created by JZ#7252.",
            icon_url="https://art.pixilart.com/a212f48d4198f72.png",
        )
    else:
        message.set_footer(text=footer)

    return message


def add_field(embed: discord.embeds.Embed, title: str, value: str, inline: bool):
    """Adds a field to a message

    Args:
        embed (discord.embeds.Embed): The embed to add to
        title (str): Title of the field
        value (str): Description of the field
        inline (bool): If it's inline
    """

    embed.add_field(name=title, value=value, inline=inline)