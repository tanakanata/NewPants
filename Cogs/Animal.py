import requests
from discord.ext import commands


class Animal(commands.Cog):
    def __init__(self, bot: commands.bot) -> None:
        print(__name__)
        self.bot = bot

    @commands.command(name='cat', aliases=['neko'])
    async def _cat(self, ctx):
        res = requests.get('https://thatcopy.pw/catapi/rest/')
        cat_img = res.json()['webpurl']

        if res.status_code != 200:
            await ctx.send('いんたーなる な さーばー の えらー')
            return

        await ctx.send(cat_img)


def setup(bot):
    bot.add_cog(Animal(bot))
