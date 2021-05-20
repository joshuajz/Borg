import discord
from dotenv import load_dotenv
from discord.ext import commands
from methods.embed import create_embed
import os

load_dotenv()

bot = commands.Bot(command_prefix="!")

bot.remove_command("help")


@bot.command()
async def broadcast(ctx, msg):
    if ctx.author.id != 178543252637483009:
        return

    embed = create_embed("Message from JZ", msg, "orange")
    print(msg)
    for server in bot.guilds:
        print(server)
        for channel in server.channels:
            print(channel)
            try:
                await channel.send(embed=embed)
            except Exception:
                continue
            else:
                break


bot.run(os.environ.get("bot_token"))
