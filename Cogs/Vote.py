import json
import typing
from datatime import datatime
from discord.ext import commands


class Vote(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot = bot

    async def add_reaction(self, message, item_count: int):
        emoji_list = ['1⃣', '2⃣', '3⃣', '4⃣',
                      '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']

        for i in range(item_count):
            await message.add_reaction(emoji_list[i])

    def save_json(self, json_data):
        pass

    def load_json(self, json_data):
        f = open('vote.json', 'r')
        json_data = json.load(f)
        return json_data

    @commands.Cog.listener
    async def on_reaction_add(self, reaction, user):
        # json読み出し
        json_data = self.load_json()
        # json_dataにメッセージIDが存在するか確認
        if reaction.message.id not in json_data:
            return

        message_id = reaction.message.id

        id_list = json_data[message_id]['id_list']

        if user.id in id_list:
            await reaction.remove(user.id)
            return

        id_list.append(user.id)

    def make_json_data(self, message)

    @commands.Cog.listener
    async def on_reaction_remove(self, reaction, user):
        pass

    @commands.group(invoke_without_command=True)
    async def vote(self, ctx):
        await ctx.send('そのうち使い方を実装するよ')

    @vote.command
    async def start(self, ctx, min: typing.Optional[int] = 30, *args):
        json_data = {}
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

        json_data[message.id] = {"count_time": }

    @vote.command
    async def result(self, ctx):
        pass


def setup(bot):
    bot.add_cog(Vote(bot))
