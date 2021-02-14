import json
import typing
import datetime
from discord.ext import commands


class Vote(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot = bot
        print(__name__)
        self.end_button = '🔚'

    async def add_reaction(self, message, item_count: int):
        # 投票用ボタンを追加
        emoji_list = ['1⃣', '2⃣', '3⃣', '4⃣',
                      '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']

        for i in range(item_count):
            await message.add_reaction(emoji_list[i])

        # 開票用ボタンを追加
        await message.add_reaction(self.end_button)

    def save_json(self, json_data):
        save_file = open('vote.json', 'w')
        json.dump(json_data, save_file)

    def load_json(self):
        f = open('vote.json', 'r')
        json_data = json.load(f)
        return json_data

    def make_json_data(self, message, channel_id, user, min):
        # 最新のデータを読み出し
        json_data = self.load_json()

        # 開票時間を計算
        now = datetime.datetime.now()
        count_time = now + datetime.timedelta(minutes=min)
        # 時間を文字列に変換
        count_time_text = count_time.strftime('%Y%m%d_%H:%M')

        # 既存のjson_dataに新しい要素を追加
        json_data[message.id] = {
            "executor": user.id,
            "channel_id": channel_id,
            "count_time": count_time_text,
            "vote_user": {}
        }

        # json_dataの内容が新しくなったのでファイルに保存
        self.save_json(json_data)

    async def aggregate(self, message_id):
        json_data = self.load_json
        channel_id = json_data[message_id]["channel_id"]
        channel = self.bot.get_channel(channel_id)
        vote_message = await channel.fetch_message(message_id)

        reactions = vote_message.reactions

        result = {}

        for r in reactions:
            result[r.emoji] = r.count

        return result

    @ commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        print('リアクション追加されたよ')
        print(reaction.emoji)
        # json読み出し
        json_data = self.load_json()

        message_id = str(reaction.message.id)
        # json_dataにメッセージIDが存在するか確認
        if message_id not in json_data:
            return

        vote_user = json_data[message_id]['vote_user']
        user_id = str(user.id)
        emoji = reaction.emoji

        # すでに投票済みだった場合、リアクションをremove
        if user_id in vote_user:
            await reaction.remove(user)
            return
        # 投票前だった場合、投票済みリストにidを追加
        json_data[message_id]['vote_user'][user_id] = emoji

        # 投票済みリストが更新されたのでjsonも更新
        print(json_data)
        self.save_json(json_data)

    @ commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        print(user.name)
        # json読み出し
        json_data = self.load_json()

        message_id = str(reaction.message.id)
        user_id = str(user.id)
        # json_dataにメッセージIDが存在するか確認
        if message_id not in json_data:
            return

        vote_user = json_data[message_id]['vote_user']
        remove_data = (user_id, reaction.emoji)

        if remove_data not in vote_user.items():
            return

        # リアクションを外した人のidを投票済みリストから削除
        del vote_user[user_id]

        # 投票済みリストが更新されたのでjsonも更新
        json_data[message_id]['vote_user'] = vote_user
        self.save_json(json_data)

    @ commands.Cog.listener(name='on_reaction_add')
    async def press_end_button(self, reaction, user):
        Received_emoji = reaction.emoji
        # 押されたリアクションがend_buttonと同じか確認
        if Received_emoji != self.end_button:
            return

        json_data = self.load_json()
        message_id = str(reaction.message.id)
        user_id = str(user.id)
        executor = json_data[message_id]['executor']

        # json_dataにメッセージIDが存在するか確認
        if message_id not in json_data:
            return
        # executorとリアクションをつけた人が同じか確認
        elif user_id not in executor:
            return

        result = self.aggregate(reaction.message.id)

    @ commands.group(invoke_without_command=True)
    async def vote(self, ctx):
        await ctx.send('そのうち使い方を実装するよ')

    @ vote.command()
    async def start(self, ctx, min: typing.Optional[int] = 30, *args):
        emoji_list = ['1⃣', '2⃣', '3⃣', '4⃣',
                      '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']
        if len(args) >= 11:
            await ctx.send('多い')
        elif len(args) <= 1:
            await ctx.send('少ない')

        text = 'とうひょー \n'

        i = 0

        for c in args:
            text += f'{emoji_list[i]} : {c}\n'
            i += 1

        message = await ctx.send(text)

        user = ctx.author
        channel_id = ctx.message.channel.id

        item_count = len(args)

        await self.add_reaction(message, item_count)

        self.make_json_data(message, channel_id, user, min)

    @ vote.command()
    async def result(self, ctx, vote_message_id: str):
        json_data = self.load_json
        # json_dataにメッセージIDが存在するか確認
        if vote_message_id not in json_data:
            return

        result = self.aggregate(vote_message_id)

        await ctx.send(result)

    # @ commands.Cog.listener()
    # async def on_command_error(ctx, error):
    #     await ctx.send(error)


def setup(bot):
    bot.add_cog(Vote(bot))
