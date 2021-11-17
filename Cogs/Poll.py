import json
import typing
import datetime
from discord.ext import commands


class Poll(commands.Cog):
    def __init__(self, bot: commands.bot):
        self.bot = bot
        print(__name__)
        self.emoji_list = ['1⃣', '2⃣', '3⃣', '4⃣',
                           '5⃣', '6⃣', '7⃣', '8⃣', '9⃣', '🔟']
        self.progress_button = '🔁'
        self.end_button = '🔚'

    async def add_reaction(self, message, item_count: int):
        # 選択肢の数だけ投票用ボタンを追加
        for i in range(item_count):
            await message.add_reaction(self.emoji_list[i])

        # 途中経過確認ボタンを追加
        await message.add_reaction(self.progress_button)

        # 開票用ボタンを追加
        await message.add_reaction(self.end_button)

    def save_json(self, json_data):
        save_file = open('poll.json', 'w')
        json.dump(json_data, save_file)

    def load_json(self):
        f = open('poll.json', 'r')
        json_data = json.load(f)
        return json_data

    def make_json_data(self, message, channel_id, user, min, mode=0):
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
            "mode": mode,
            "poll_user": {}
        }

        # json_dataの内容が新しくなったのでファイルに保存
        self.save_json(json_data)

    async def aggregate(self, message_id):
        json_data = self.load_json()
        channel_id = json_data[message_id]['channel_id']
        channel = self.bot.get_channel(channel_id)
        poll_message = await channel.fetch_message(int(message_id))

        reactions = poll_message.reactions

        result = {}

        for r in reactions:
            if r.emoji in self.emoji_list:
                result[r.emoji] = r.count

        return result

    async def get_message(self, channel_id, message_id):
        channel = self.bot.get_channel(channel_id)
        message = await channel.fetch_message(int(message_id))
        content = message.content

        return content

    @ commands.Cog.listener(name='on_reaction_add')
    async def press_choices_button(self, reaction, user):
        Received_emoji = reaction.emoji
        # 追加されたリアクションがemoji_listになかった場合処理終了
        if Received_emoji not in self.emoji_list:
            return

        # json読み出し
        json_data = self.load_json()
        message_id = str(reaction.message.id)

        # json_dataにメッセージIDが存在するか確認
        if message_id not in json_data:
            return

        poll_user = json_data[message_id]['poll_user']
        user_id = str(user.id)
        emoji = reaction.emoji
        mode = json_data[message_id]['mode']

        # モードがマルチではなかった場合投票済みユーザか確認
        if str(mode) != "1":
            # すでに投票済みだった場合、リアクションをremove
            if user_id in poll_user:
                await reaction.remove(user)
                return
        # 投票前だった場合、投票済みリストにidを追加
        json_data[message_id]['poll_user'][user_id] = emoji

        # 投票済みリストが更新されたのでjsonも更新
        self.save_json(json_data)

    @ commands.Cog.listener(name='on_reaction_add')
    async def press_progress_button(self, reaction, user):
        # リアクションを追加したユーザーがBotだったらreturn
        if user.bot:
            return

        # 押されたリアクションがprogress_buttonと同じか確認
        if reaction.emoji != self.progress_button:
            return

        # jsonの内容を読み出し
        json_data = self.load_json()
        message_id = str(reaction.message.id)

        # json_dataにメッセージIDが存在するか確認
        if message_id not in json_data:
            return

        # 対象投票の作成者を取得
        executor = json_data[message_id]['executor']

        # executorとリアクションをつけた人違う場合処理終了
        if str(user.id) != str(executor):
            return

        # 結果を集計
        result = await self.aggregate(message_id)

        # オリジナルメッセージを取得&送信
        channel_id = json_data[message_id]["channel_id"]
        channel = self.bot.get_channel(channel_id)
        original_message = await self.get_message(channel_id, message_id)
        await channel.send(content=original_message)

        # 集計結果を成形&送信
        text = ''
        for k, v in result.items():
            if k != self.end_button:
                v = int(v) - 1
                text += f'{k} : {v}　'
        await channel.send(content=text)

        # リアクション追加をなかったことにする
        await reaction.remove(user)

    @ commands.Cog.listener(name='on_reaction_add')
    async def press_end_button(self, reaction, user):
        # リアクションを追加したユーザーがBotだったらreturn
        if user.bot:
            return

        # 押されたリアクションがend_buttonと同じか確認
        if reaction.emoji != self.end_button:
            return

        # jsonの内容を読み出し
        json_data = self.load_json()
        message_id = str(reaction.message.id)

        # json_dataにメッセージIDが存在するか確認
        if message_id not in json_data:
            return

        # 対象投票の作成者を取得
        executor = json_data[message_id]['executor']

        # executorとリアクションをつけた人違う場合処理終了
        if str(user.id) != str(executor):
            return

        # 結果を集計
        result = await self.aggregate(message_id)

        # オリジナルメッセージを取得&送信
        channel_id = json_data[message_id]["channel_id"]
        channel = self.bot.get_channel(channel_id)
        original_message = await self.get_message(channel_id, message_id)
        await channel.send(content=original_message)

        # 集計結果を成形&送信
        text = ''
        for k, v in result.items():
            if k != self.end_button:
                v = int(v) - 1
                text += f'{k} : {v}　'
        await channel.send(content=text)

        # jsonから削除
        json_data = json_data.pop(message_id)
        self.save_json(json_data)

        # progress&endボタンを削除
        poll_message = await channel.fetch_message(int(message_id))
        await poll_message.clear_reaction(self.progress_button)
        await poll_message.clear_reaction(self.end_button)

    @ commands.Cog.listener()
    async def on_reaction_remove(self, reaction, user):
        # json読み出し
        json_data = self.load_json()

        message_id = str(reaction.message.id)
        user_id = str(user.id)
        # json_dataにメッセージIDが存在するか確認
        if message_id not in json_data:
            return

        poll_user = json_data[message_id]['poll_user']
        remove_data = (user_id, reaction.emoji)

        if remove_data not in poll_user.items():
            return

        # リアクションを外した人のidを投票済みリストから削除
        del poll_user[user_id]

        # 投票済みリストが更新されたのでjsonも更新
        json_data[message_id]['poll_user'] = poll_user
        self.save_json(json_data)

    @ commands.group(invoke_without_command=True)
    async def poll(self, ctx):
        await ctx.send('!poll')

    @ poll.command()
    async def single(self, ctx, min: typing.Optional[int] = 30, question='くえすちょん？', *items):  # noqa
        if len(items) >= 11:
            await ctx.send('多い')
            return
        elif len(items) <= 1:
            await ctx.send('少ない')
            return

        text = question + '\n'

        i = 0

        for c in items:
            text += f'{self.emoji_list[i]} : {c}\n'
            i += 1

        message = await ctx.send(text)

        user = ctx.author
        channel_id = ctx.message.channel.id

        item_count = len(items)

        await self.add_reaction(message, item_count)

        self.make_json_data(message, channel_id, user, min)

    @ poll.command()
    async def multi(self, ctx, min: typing.Optional[int] = 30, question='くえすちょん？', *items):  # noqa
        mode = 1
        if len(items) >= 11:
            await ctx.send('多い')
            return
        elif len(items) <= 1:
            await ctx.send('少ない')
            return

        text = question + '\n'

        i = 0

        for c in items:
            text += f'{self.emoji_list[i]} : {c}\n'
            i += 1

        message = await ctx.send(text)

        user = ctx.author
        channel_id = ctx.message.channel.id

        item_count = len(items)

        self.make_json_data(message, channel_id, user, min, mode)

        await self.add_reaction(message, item_count)


def setup(bot):
    bot.add_cog(Poll(bot))
