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


def create_embed(
    title: str, description: str, colour: str, footer="contact"
) -> discord.Embed:
    message = discord.Embed(
        title=title,
        description=description,
        colour=embedColours[colour].value,
        timestamp=datetime.datetime.utcnow(),
    )
    """Creates an Embed Object"""

    if footer == "contact":
        message.set_footer(text="Contact JZ#7252 with concerns.")
    else:
        message.set_footer(text=footer)

    return message


def add_field(embed: discord.embeds.Embed, title: str, value: str, inline: bool):
    """Adds a field to a message"""

    embed.add_field(name=title, value=value, inline=inline)