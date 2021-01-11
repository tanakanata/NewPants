import asyncio
import datetime
import os
import random
import pytz
import json
from discord.ext import commands, tasks
import discord


class Jihou(commands.Cog):
    """時報関連"""

    def __init__(self, bot: commands.bot):
        print('Jihou OK')
        self.bot = bot
        self.guild_id = 610568927768084499
        self.channel_id = None
        self.guild = None
        self.channel = None
        self.channel_list = []
        self.channel_index = 1
        self.channel_count = None
        self.channel = None
        self.time_zone = 'Asia/Tokyo'
        self.m_dice = random.randint(1, 7)
        self.d_dice = random.randint(8, 11)
        self.n_dice = random.randint(12, 15)
        self.now = datetime.datetime.now(
            pytz.timezone(self.time_zone)).strftime('%H:%M:%S')
        self.sound_base_path = os.path.normpath(os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '..')) + '/'
        self.playing = False
        self.interval = None
        self.r_message = None
        self.read_json()
        self.loop.start()

    def initialize(self):
        self.guild = self.bot.get_guild(self.guild_id)
        LIST1 = self.guild.voice_channels
        for c_list in LIST1:
            self.channel_list.append(c_list.id)
        self.channel_count = len(self.channel_list)
        self.channel_count = self.channel_count - 1
        self.channel_id = self.channel_list[0]
        self.channel = self.bot.get_channel(self.channel_id)
        self.write_json()

    def write_json(self):
        json_date = {}
        json_date["channel_list"] = self.channel_list
        json_date["channel_id"] = self.channel_id
        wf = open('channels.json', 'w')
        json.dump(json_date, wf)

    def read_json(self):
        rf = open('channels.json', 'r')
        json_date = json.load(rf)
        self.channel_list = json_date['channel_list']
        self.channel_count = len(self.channel_list)
        self.channel_count = self.channel_count - 1
        self.channel_id = json_date['channel_id']

    @commands.Cog.listener(name='on_ready')
    async def change_presence(self):
        self.initialize()
        await self.bot.change_presence(
            activity=discord.Game(self.time_zone))

    @ commands.command()
    async def nowtime(self, ctx):
        await ctx.send(self.now)

    @ commands.command()
    async def count(self, ctx):
        await ctx.send(self.channel_count)

    @ commands.command()
    async def lst(self, ctx):
        await ctx.send(self.channel_list)

    @ commands.command()
    async def timezone(self, ctx):
        await ctx.send(self.time_zone)

    @ commands.command()
    async def list_timezone(self, ctx):
        timeZoneList = pytz.common_timezones
        timeZoneListJoined = '\n'.join(timeZoneList)

        discordTextMaxLength = 1950
        if len(timeZoneListJoined) <= discordTextMaxLength:
            # 2000以下
            await ctx.send(f'```{timeZoneList}```')
        else:
            partMessageBody = ""
            partMessageNum = 1

            for line in timeZoneList:
                if len(partMessageBody) + len(line) >= discordTextMaxLength:
                    await ctx.send(f'```{partMessageBody}```')
                    partMessageBody = ""
                    partMessageNum += 1
                partMessageBody += line + '\n'

            await ctx.send(f'```{partMessageBody}```')

    @ commands.command()
    async def set_timezone(self, ctx, new_timezone: str):
        if new_timezone in pytz.common_timezones:
            self.time_zone = new_timezone
            self.now = datetime.datetime.now(
                pytz.timezone(self.time_zone)).strftime('%H:%M:%S')
            await ctx.send('新しいタイムゾーンを' + self.time_zone + 'にセットしました')
            await self.bot.change_presence(
                activity=discord.Game(self.time_zone))
        else:
            await ctx.send("そんなもの存在しませ〜んw")

    @ commands.command()
    async def toggle_channel(self, ctx):
        self.channel_id = self.channel_list[self.channel_index]
        self.channel = self.bot.get_channel(self.channel_id)
        await ctx.send(self.channel.name + 'に変更しました。')

        if self.channel_index == self.channel_count:
            self.channel_index = 0
        else:
            self.channel_index = self.channel_index + 1

    @commands.command()
    async def set_channel(self, ctx, *args):
        max_index = self.channel_count + 1
        # 引数の数を確認
        if len(args) == 1:
            try:
                new_index = int(args[0])
            except ValueError:
                await ctx.send('数字しかはいりませ～～ん')
                return

        else:
            await ctx.send(':thinking::thinking::thinking:')
            return
        # チャンネル数と比較
        if 0 <= new_index and new_index > max_index:
            await ctx.send(':thinking::thinking::thinking:')
            return
        else:
            self.channel_id = self.channel_list[new_index]
            self.channel = self.bot.get_channel(self.channel_id)
            await ctx.send(self.channel.name + 'に変更しました。')

    @ commands.command()
    async def now_channel(self, ctx):
        await ctx.send(self.channel.name + 'です。')

    @ commands.command()
    async def save(self, ctx):
        self.write_json()
        await ctx.send('セーブしました。')

    @ commands.command()
    async def load(self, ctx):
        self.read_json()
        await ctx.send('ロードしました。')

    @ commands.command()
    async def SV(self, ctx):
        await discord.VoiceChannel.connect(self.channel)

    async def play_audio(self, pre_filepath, post_filepath):
        audio1 = discord.FFmpegPCMAudio(pre_filepath)
        audio2 = discord.FFmpegPCMAudio(post_filepath)
        emoji = '\N{BLACK RIGHT-POINTING TRIANGLE}'

        if self.channel is None:
            self.channel = self.bot.get_channel(self.channel_id)
        else:
            pass

        while(self.playing):
            await asyncio.sleep(1)

        self.playing = True

        voice = await discord.VoiceChannel.connect(self.channel)

        asyncio.sleep(0.5)

        voice.play(audio1)

        while voice.is_playing():
            await asyncio.sleep(1)

        audio1.cleanup()
        voice.play(audio2)

        while voice.is_playing():
            await asyncio.sleep(1)

        audio2.cleanup()

        asyncio.sleep(self.interval)

        await voice.disconnect()

        try:
            await self.r_message.add_reaction(emoji)
        except NameError:
            pass

        self.playing = False

        return

    @ commands.command()
    async def test_join(self, ctx, *args):
        now_datetime = datetime.datetime.now(
            pytz.timezone(self.time_zone)).strftime('%H:%M:%S')
        today = datetime.datetime.now(
            pytz.timezone(self.time_zone)).strftime('%m%d')
        split_time = now_datetime.split(':')
        actorlist = ['Donglong', 'Chico']
        Vactor = random.choice(actorlist)

        if len(args) == 0:
            jikoku = int(split_time[0])

        elif len(args) == 1:
            try:
                jikoku = int(args[0])
            except ValueError:
                await ctx.send('引数間違えないでください！！！！！')
                return
        elif len(args) == 2:
            try:
                jikoku = int(args[0])
            except ValueError:
                await ctx.send('引数間違えないでください！！！！！')
                return
            if args[1] == 'Donglong' or args[1] == 'Chico':
                Vactor = args[1]

        else:
            await ctx.send('使い方知ってる？？？？？？？？？')
            return

        if jikoku < 0:
            await ctx.send('1日って0時から24時までってしってます？？？？？？？？')
            return

        if jikoku > 24:
            await ctx.send('地球上では1日って24時間なんですよ。\
                            そんなことも知らないんですか？？？\
                            小学校からやり直したほうがいいですよ？？？？')
            return

        if Vactor == 'Donglong':
            self.interval = 2

        else:
            self.interval = 0.5

        jikoku = str(jikoku)
        jikoku = jikoku.zfill(2)
        V1 = Vactor

        if '05' <= jikoku <= '10':
            pre_filepath = self.sound_base_path + \
                '{0}/pre/{1}.wav'.format(Vactor, self.m_dice)
            post_filepath = self.sound_base_path + \
                '{0}/{1}.wav'.format(Vactor, jikoku)
            self.m_dice = random.randint(1, 7)
            Vactor = random.choice(actorlist)
        elif '11' <= jikoku <= '17':
            pre_filepath = self.sound_base_path + \
                '{0}/pre/{1}.wav'.format(Vactor, self.d_dice)
            post_filepath = self.sound_base_path + \
                '{0}/{1}.wav'.format(Vactor, jikoku)
            self.d_dice = random.randint(8, 11)
            Vactor = random.choice(actorlist)
        elif '18' <= jikoku <= '24' or '00' <= jikoku <= '04':
            pre_filepath = self.sound_base_path + \
                '{0}/pre/{1}.wav'.format(Vactor, self.n_dice)
            post_filepath = self.sound_base_path + \
                '{0}/{1}.wav'.format(Vactor, jikoku)
            self.n_dice = random.randint(12, 15)
            Vactor = random.choice(actorlist)

        if today == '1225' and V1 == 'Donglong':
            pre_filepath = self.sound_base_path + 'Donglong/me.wav'

        while(self.playing):
            await asyncio.sleep(1)

        self.r_message = ctx.message

        await self.play_audio(pre_filepath, post_filepath)

    @ tasks.loop(seconds=1)
    async def loop(self):
        now_datetime = datetime.datetime.now(
            pytz.timezone(self.time_zone)).strftime('%H:%M:%S')
        today = datetime.datetime.now(
            pytz.timezone(self.time_zone)).strftime('%m%d')
        split_time = now_datetime.split(':')
        actorlist = ['Donglong', 'Chico']
        Vactor = random.choice(actorlist)

        if Vactor == 'Donglong':
            self.interval = 2

        else:
            self.interval = 0.5

        V1 = Vactor

        if split_time[1] == '00' and split_time[2] == '00':
            if '05' <= split_time[0] <= '10':
                pre_filepath = self.sound_base_path + \
                    '/{0}/pre/{1}.wav'.format(Vactor, self.m_dice)
                post_filepath = self.sound_base_path + \
                    '{0}/{1}.wav'.format(Vactor, split_time[0])
                self.m_dice = random.randint(1, 7)
                Vactor = random.choice(actorlist)
            elif '11' <= split_time[0] <= '17':
                pre_filepath = self.sound_base_path + \
                    '{0}/pre/{1}.wav'.format(Vactor, self.d_dice)
                post_filepath = self.sound_base_path + \
                    '{0}/{1}.wav'.format(Vactor, split_time[0])
                self.d_dice = random.randint(8, 11)
                Vactor = random.choice(actorlist)
            elif '18' <= split_time[0] <= '24' \
                    or '00' <= split_time[0] <= '04':
                pre_filepath = self.sound_base_path + \
                    '{0}/pre/{1}.wav'.format(Vactor, self.n_dice)
                post_filepath = self.sound_base_path + \
                    '{0}/{1}.wav'.format(Vactor, split_time[0])
                self.n_dice = random.randint(12, 15)
                Vactor = random.choice(actorlist)

            if split_time[0] == '24':
                self.initialize()

            if today == '1225' and V1 == 'Donglong':
                pre_filepath = self.sound_base_path + 'Donglong/me.wav'

            await self.play_audio(pre_filepath, post_filepath)


def setup(bot):
    bot.add_cog(Jihou(bot))
