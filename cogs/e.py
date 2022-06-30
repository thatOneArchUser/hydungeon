import traceback, math, discord, sys
from discord.ext import commands
from discord.ext.commands import *

class e(commands.Cog):
    def __init__(self, client:commands.Bot):
        self.client = client

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'): return
        cog = ctx.cog
        if cog:
            if cog._get_overridden_method(cog.cog_command_error) is not None: return
        ignored = (commands.CommandNotFound)
        error = getattr(error, 'original', error)
        if isinstance(error, ignored): return
        if isinstance(error, commands.DisabledCommand): await ctx.send(f'{ctx.command} has been disabled.')
        elif isinstance(error, commands.NoPrivateMessage):
            try: await ctx.author.send(f'{ctx.command} can not be used in Private Messages.')
            except discord.HTTPException: pass       
        if isinstance(error, commands.CommandOnCooldown):
            print(f"{self.gettime()}CommandOnCooldown triggered by {ctx.author} in {ctx.command}")
            if math.ceil(error.retry_after) < 60:
                await ctx.reply(f'This command is on cooldown. Please try after {math.ceil(error.retry_after)} seconds')
            elif math.ceil(error.retry_after) < 3600:
                ret = math.ceil(error.retry_after) / 60
                await ctx.reply(f'This command is on cooldown. Please try after {math.ceil(ret)} minutes')
            elif math.ceil(error.retry_after) >= 3600:
                ret = math.ceil(error.retry_after) / 3600
                if ret >= 24:
                    r = math.ceil(ret) / 24
                    await ctx.reply(f"This command is on cooldown. Please try after {r} days")
                else: await ctx.reply(f'This command is on cooldown. Please try after {math.ceil(ret)} hours')
        elif isinstance(error, commands.BadArgument):
            if ctx.command.qualified_name == 'tag list': await ctx.send('I could not find that member. Please try again.')
            else: await ctx.send("Invalid argument")
        elif isinstance(error, commands.MissingRequiredArgument): await ctx.send("Missing required argument")
        elif isinstance(error, commands.MissingPermissions): await ctx.reply("You can\'t use this")
        elif isinstance(error, commands.BotMissingPermissions): await ctx.reply("I don\'t have permissions to use this")
        elif isinstance(error, commands.errors.NSFWChannelRequired): await ctx.reply("This command only works in a nsfw channel")
        else:
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


def setup(client): client.add_cog(e(client))
