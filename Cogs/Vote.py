import typing
from discord.ext import commands


class Vote(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot = bot

    async def add_reaction(self, message, item_count: int):
        emoji_list = ['1⃣', '2⃣', '3⃣', '4⃣',
                      '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']

        for i in range(item_count):
            await message.add_reaction(emoji_list[i])

    @commands.group(invoke_without_command=True)
    async def vote(self, ctx):
        await ctx.send('そのうち使い方を実装するよ')

    @vote.command
    async def start(self, ctx, min: typing.Optional[int] = 30, *args):
        emoji_list = ['1⃣', '2⃣', '3⃣', '4⃣',
                      '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']
        if len(args) >= 11:
            await ctx.send('多い')
        elif len(args) <= 1:
            await ctx.send('少ない')

        text = 'とうひょー \n'

        i = 1

        for c in args:
            text += f'{emoji_list[i]} : {c}\n'
            i += 1

        message = await ctx.send(text)

        item_count = len(args)

        await self.add_reaction(message, item_count)

    @vote.command
    async def result(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Vote(bot))
