import discord
from discord.ext import commands
import os

TOKEN = os.environ["TOKEN"]

intents = discord.Intents.all()

bot = commands.Bot(command_prefix='!', help_command=None, intents=intents)

cog_list = ['Animal', 'ColorImaging', 'Image', 'Jihou','Kotoba',
            'Logging', 'Other', 'Steam', 'Poll', 'Translate',
            'Killer']

adminlist = [227845640661499905, 713388740990468097, 237261228781600768, 809576158240571454]

@bot.event
async def on_ready():
    print('Ready')

@bot.slash_command()
async def reload(ctx: discord.ApplicationContext):
    if ctx.author.id not in adminlist:
        await ctx.respond("You do not own this bot!")
        return
    for cog in cog_list:
        name = f'Cogs.{cog}'
        bot.reload_extension(name)
    await ctx.respond('Reloaded')

@bot.slash_command()
async def shutdown(ctx: discord.ApplicationContext):
    if ctx.author.id not in adminlist:
        await ctx.respond("You do not own this bot!")
        return
    else:
        for cog in cog_list:
            name = f'Cogs.{cog}'
            bot.unload_extension(name)
        try:
            print("shutdown")
            await ctx.respond('Bye-Bye')
            await bot.close()
        except Exception as e:
            print(e)
            bot.clear()

if __name__ == '__main__':
    for cog in cog_list:
        name = f'Cogs.{cog}'
        bot.load_extension(name)

bot.run(TOKEN)
