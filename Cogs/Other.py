import discord
import random
import datetime
import pytz
from discord.ext import commands
import requests

class Other(commands.Cog):
    def __init__(self, bot: commands.bot):
        print('Other OK')
        self.bot = bot
        self.jst = pytz.timezone('Asia/Tokyo')

    @commands.command()
    async def help(self, ctx):
        with open("help.png", "rb") as fh:
            f = discord.File(fh, filename="help.png")

        await ctx.send(file=f)

    @commands.command()
    async def dice(self, ctx, *args):
        if len(args) == 1:
            try:
                atai = int(args[0])
            except ValueError:
                await ctx.send('変なもの入力してんじゃねーぞ')
                return

        else:
            await ctx.send('使い方知ってる？？？？？？？？？')
            return

        if atai < 0:
            await ctx.send('ダイスに負の値入れようとしてるの、普通に考えて頭逝ってますよ？')
            return

        if len(str(atai)) > 1900:
            await ctx.send('Discordの文字数制限ってご存知ですか？？？？？？？？')
            return
        else:
            kekka = random.randint(0, atai)
            await ctx.send('只今の結果は ' + str(kekka) + ' です。')

    @commands.command()
    async def ping(self, ctx):
        # 日本時間の現在日付を取得
        naive_dt = datetime.datetime.now(self.jst)
        await ctx.send('PONG {0}'.format(
            naive_dt.strftime('%Y-%m-%d %H:%M:%S.%f')
        ))

    @commands.command()
    async def sorry(self, ctx):
        messages = await ctx.channel.history(limit=20).flatten()
        id_list = []
        for msg in messages:
            if msg.author.bot:
                print('bot')
            else:
                id_list.append(msg.author.mention)
                if len(id_list) == 2:
                    break

        mention = id_list[1]

        await ctx.send(f'{mention}さんへ \n ごめんね。\n {ctx.author.mention}より。')

    @commands.command()
    async def mistake(self, ctx, *args):
        # 聞き間違え一覧取得APIのURL
        url = "https://script.google.com/macros/s/AKfycbwB3rETygKzPJwYJi4Or6NE4ho1NDP03MdxukyUoug_HpiYiSA83TbivQnc1KvgYLfE/exec"

        # バリデーションチェック
        if len(args) == 2 or len(args) == 3:
            try:
                year = int(args[0])
                month = int(args[1])
            except ValueError:
                await ctx.send('変なもの入力してんじゃねーぞ')
                return
        elif len(args) == 1 and args[0] != 'spoiler' and args[0] != 'spoiliter':
            await ctx.send('使い方知ってる？？？？？？？？？')
            return
        if len(args) == 3 and args[2] != 'spoiler' and args[2] != 'spoiliter':
            await ctx.send('使い方知ってる？？？？？？？？？')
            return

        # 分割でスポイラーするか
        spoiliter = False
        if (len(args) == 1 and args[0] == 'spoiliter') or (len(args) == 3 and args[2] == 'spoiliter'):
            spoiliter = True

        # 引数が1か0だった場合、ランダム日付で取得
        if len(args) == 0 or len(args) == 1:
            dt_now = datetime.datetime.now()
            year = random.randint(2021, dt_now.year)
            if (dt_now.year == 2021):
                month = random.randint(2, dt_now.month)
            elif (dt_now.year == year):
                month = random.randint(1, dt_now.month)
            else:
                month = random.randint(1, 12)

        # バリデーション続き
        if len(str(year)) > 1900 or len(str(month)) > 1900:
            await ctx.send('Discordの文字数制限ってご存知ですか？？？？？？？？')
            return

        # post実行
        result = requests.post(url, {'year': year, 'month': month})

        # status_codeを代入
        status_code = result.status_code

        if not 200 <= status_code <= 299:
            return status_code

        # リクエストの結果をjsonに格納
        json_data = result.json()

        # 取得結果が0件だった場合
        if len(json_data) == 0:
            if len(args) == 0 or len(args) == 1:
                # 聞き間違えが存在する月がでるまでループ
                while len(json_data) == 0:
                    year = random.randint(2021, dt_now.year)
                    if (dt_now.year == 2021):
                        month = random.randint(2, dt_now.month)
                    elif (dt_now.year == year):
                        month = random.randint(1, dt_now.month)
                    else:
                        month = random.randint(1, 12)
                    # post実行
                    result = requests.post(url, {'year': year, 'month': month})

                    # status_codeを代入
                    status_code = result.status_code

                    if not 200 <= status_code <= 299:
                        return status_code

                    # リクエストの結果をjsonに格納
                    json_data = result.json()
            else:
                await ctx.send("まだ誰も聞き間違えてない月が存在したんですね。")
                return

        # ランダムで聞き間違いを選択
        choice = random.choice(json_data)

        # choice内の各項目が空白だった場合、空文字ではなくスペースに変更（日付は入力前提の為スルー）
        if len(choice['talker']) == 0:
            choice['talker'] = "　"
        if len(choice['listener']) == 0:
            choice['listener'] = "　"
        if len(choice['text']) == 0:
            choice['text'] = "　"
        if len(choice['mistake']) == 0:
            choice['mistake'] = "　"

        # メッセージ送信
        if len(args) == 2 or len(args) == 0:
            await ctx.send('言った人：' + choice['talker'] + '\n'
                           + '聞き間違えた人：' + choice['listener'] + '\n'
                           + '原文：' + choice['text'] + '\n'
                           + '聞き間違え：' + choice['mistake'] + '\n'
                           + '日付：' + choice['date'])
        elif len(args) == 3 or len(args) == 1:
            # スポイラーを切り分けで行う
            if (spoiliter):
                talker = ""
                listener = ""
                text = ""
                mistake = ""
                date = ""
                # 一文字ずつ設定
                for key, value in choice.items():
                    for val in str(value).replace(' ', ''):
                        if(key == 'talker'):
                            talker = talker + "||" + val + "||"
                        elif(key == 'listener'):
                            listener = listener + "||" + val + "||"
                        elif(key == 'text'):
                            text = text + "||" + val + "||"
                        elif(key == 'mistake'):
                            mistake = mistake + "||" + val + "||"
                        elif(key == 'date'):
                            date = date + "||" + val + "||"

                await ctx.send('言った人：' + talker + '\n'
                               + '聞き間違えた人：' + listener + '\n'
                               + '原文：' + text + '\n'
                               + '聞き間違え：' + mistake + '\n'
                               + '日付：' + date)
            else:
                await ctx.send('言った人：||' + choice['talker'] + '||\n'
                               + '聞き間違えた人：||' + choice['listener'] + '||\n'
                               + '原文：||' + choice['text'] + '||\n'
                               + '聞き間違え：||' + choice['mistake'] + '||\n'
                               + '日付：||' + choice['date'] + '||')

    @ commands.Cog.listener(name='on_message')
    async def edit_ping(self, message):
        if message.content.startswith('PONG ') and message.author.id == self.bot.user.id:  # noqa
            time_now = message.content.replace('PONG ', '')
            ping_time = self.jst.localize(
                datetime.datetime.strptime(time_now, '%Y-%m-%d %H:%M:%S.%f'))
            print "###############################################"
            print message.created_at
            print datetime.timedelta(hours=9) 
            print message.created_at + datetime.timedelta(hours=9)
            print "###############################################"
            post_time = self.jst.localize(message.created_at +  # noqa
                                                             datetime.timedelta(hours=9))  # noqa
            diff_time = post_time - ping_time
            await message.edit(content='PONG({0}ms)'.format((diff_time.seconds * 1000) + int(str(diff_time.microseconds)[:3])))  # noqa


def setup(bot):
    bot.add_cog(Other(bot))
