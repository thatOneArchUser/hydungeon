import discord, time
from discord.ext import commands

client = commands.Bot(command_prefix=".", case_insensitive=True)
client.remove_command("help")

@client.event
async def on_ready():
    print("o")
    await client.change_presence(activity=discord.Game(name=".help", timestamps={"start": time.time()}))

client.load_extension("cogs.dungeon")
client.load_extension("cogs.e")
client.run("imagine thinking i forgor the token here :skull:")
