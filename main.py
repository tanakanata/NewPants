import discord
from discord.ext import commands
import config

TOKEN = config.AT

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', help_command=None, intents=intents)

cog_list = ['Animal', 'ColorImaging', 'Image', 'Jihou',
            'Kotoba', 'Logging', 'Other', 'Steam', 'Poll']

adminlist = [227845640661499905, 713388740990468097, 237261228781600768]


@bot.event
async def on_ready():
    print('Ready')


@bot.command(aliases=['f5', 'F5', 'rld'])
async def reload(ctx):
    for cog in cog_list:
        name = f'Cogs.{cog}'
        bot.reload_extension(name)
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

if __name__ == '__main__':
    for cog in cog_list:
        name = f'Cogs.{cog}'
        bot.load_extension(name)

bot.run(TOKEN)
