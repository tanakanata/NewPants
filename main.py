import discord
from discord.ext import commands
import config

TOKEN = config.AT

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', help_command=None, intents=intents)

bot.load_extension('vote')

adminlist = [227845640661499905, 713388740990468097, 237261228781600768]


@bot.event
async def on_ready():
    print('Ready')


@bot.command()
async def reload(ctx):
    bot.reload_extension('vote')
    await ctx.send('reload')


@bot.command()
async def shutdown(ctx):
    if ctx.message.author.id in adminlist:
        print("shutdown")
        await ctx.send('shutdown')
    try:
        await bot.logout()
    except:  # noqa
        print("EnvironmentError")
        bot.clear()
    else:
        await ctx.send("You do not own this bot!")

bot.run(TOKEN)
