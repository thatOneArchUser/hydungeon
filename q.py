# modules
import discord
from discord.errors import InvalidArgument
from discord.ext import commands
from discord.ext.commands import *
# end of modules

    
@bot.command()
async def load(ctx, *, arg1):
    if ctx.message.author.id in oid: pass
    else:
        await ctx.reply(f"You can\'t use this command")
        print(f"[Cog] {ctx.author} returned an error: User Missing Permission.")
        return
    try:
        bot.load_extension(f'cogs.{arg1}')
        await ctx.send("Loaded Cog")
        print(f"[Cog] {ctx.author} loaded cog.")
        return
    except Exception as e:
        await ctx.send(e)
        print(f"[Cog] An unexpected error has occurred: {e}")

@bot.command()
async def unload(ctx, *, arg1):
    if ctx.message.author.id in oid: pass
    else:
        await ctx.reply(f"You can\'t use this command")
        print(f"[Cog] {ctx.author} returned an error: User Missing Permission.")
        return
    try:
        bot.unload_extension(f'cogs.{arg1}')
        await ctx.send("Unloaded Cog")
        print(f"[Cog] {ctx.author} unloaded cog.")
        return
    except Exception as e:
        await ctx.send(e)
        print(f"[Cog] An unexpected error has occurred: {e}")
        
@bot.command()
async def reload(ctx, *, arg1):
    if ctx.message.author.id in oid: pass
    else:
        await ctx.reply(f"You can\'t use this command")
        print(f"[Cog] {ctx.author} returned an error: User Missing Permission.")
        return
    try:
        bot.unload_extension(f'cogs.{arg1}')
        bot.load_extension(f'cogs.{arg1}')
        await ctx.send("Reloaded Cog")
        print(f"[log] {ctx.author} reloaded cog.")
        return
    except Exception as e:
        await ctx.send(e)
        print(f"[Cog] An unexpected error has occurred: {e}")
        


# btw i use arch
