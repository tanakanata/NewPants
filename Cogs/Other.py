import discord
import random
import datetime
import pytz
from discord.ext import commands


class Other(commands.Cog):
    def __init__(self, bot: commands.bot):
        print('Other OK')
        self.bot = bot

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
        await ctx.send('PONG {0}'.format(
            pytz.timezone('Asia/Tokyo').localize(
                (ctx.message.created_at + datetime.timedelta(hours=9))
            ).strftime('%Y-%m-%d %H:%M:%S.%f')
        ))

    @commands.command()
    async def sorry(self,ctx):
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



    @commands.Cog.listener(name='on_message')
    async def edit_ping(self, message):
        if message.content.startswith('PONG ') and message.author.id == self.bot.user.id:  # noqa
            time_now = message.content.replace('PONG ', '')
            ping_time = pytz.timezone('Asia/Tokyo').localize(
                datetime.datetime.strptime(time_now, '%Y-%m-%d %H:%M:%S.%f'))
            post_time = pytz.timezone('Asia/Tokyo').localize(message.created_at +  # noqa
                                                             datetime.timedelta(hours=9))  # noqa
            diff_time = post_time - ping_time
            await message.edit(content='PONG({0}ms)'.format((diff_time.seconds * 1000) + int(str(diff_time.microseconds)[:3])))  # noqa


def setup(bot):
    bot.add_cog(Other(bot))
