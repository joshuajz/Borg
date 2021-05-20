import discord
from dotenv import load_dotenv
from discord.ext import commands
from methods.embed import create_embed
import os

load_dotenv()

bot = commands.Bot(command_prefix="!")

bot.remove_command("help")


@bot.command()
async def broadcast(ctx):
    if ctx.author.id != 178543252637483009:
        return

    msg = ctx.message.content.split("!broadcast")[1]

    embed = create_embed("Message from JZ", msg, "orange")

    for server in bot.guilds:
        channel_names = [channel.name for channel in server.channels]

        if "general" in channel_names or "chat" in channel_names:
            for channel in server.channels:
                if channel.name == "chat" or channel.name == "general":
                    try:
                        await channel.send(embed=embed)
                    except Exception:
                        print("Didn't work.")
                    else:
                        break

        else:
            for channel in server.channels:
                print(channel)
                try:
                    await channel.send(embed=embed)
                except Exception:
                    continue
                else:
                    break


bot.run(os.environ.get("broadcast_token"))
