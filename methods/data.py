import discord
from typing import Union


def parse_id(data: str) -> int:
    """Finds a user given some sort of user data -> userid (178543252637483009) user @ (<@178543252637483009> OR <@!178543252637483009>)"""

    if type(data) == int:
        return data

    try:
        data = data.strip()
    except:
        return False

    if data.isnumeric() and len(data) == 18:
        # User ID is given
        user_id = int(data)
    elif data[0:3] == "<@!" or data[0:3] == "<@&":
        user_id = int(data[3:-1])
    elif data[0:2] == "<@" or data[0:2] == "<#":
        user_id = int(data[2:-1])
    else:
        return False

    return user_id


def parse_channel(data: str) -> int:
    """Finds a channel given some sort of data.  ie. <#839744778517872650> -> 839744778517872650"""

    if type(data) == int:
        return data

    try:
        data = data.strip()
    except:
        return False

    if data.isnumeric() and len(data) == 18:
        user_id = int(data)
    elif data[0:2] == "<#":
        user_id = int(data[2:-1])
    else:
        return False

    return user_id


def find_channel(ctx, channel: str) -> Union[int, list]:
    """Finds a channel given it's name."""

    channel_id = [i.id for i in ctx.guild.channels if i.name == channel]

    if len(channel_id) == 1:
        return int(channel_id[0])
    else:
        return ["False", "There are multiple channels with that name."]
