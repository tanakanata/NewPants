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
        self.guild_id: int = 610568927768084499
        self.channel_id: int = None
        self.guild = None
        self.channel = None
        self.channel_list: list = []
        self.channel_index: int = 1
        self.channel_count: int = None
        self.channel = None
        self.member_count: dict = {}
        self.time_zone: str = 'Asia/Tokyo'
        self.m_dice: int = random.randint(1, 7)
        self.d_dice: int = random.randint(8, 11)
        self.n_dice: int = random.randint(12, 15)
        self.now: str = datetime.datetime.now(
            pytz.timezone(self.time_zone)).strftime('%H:%M:%S')
        self.sound_base_path: str = os.path.normpath(os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '..')) + '/'
        self.playing: bool = False
        self.auto_channel_select: bool = False
        self.interval: int = None
        self.r_message = None
        self.actorlist: list = []
        self.vactor: str = None
        self.read_json()
        self.vactor_select()
        self.time_check.start()

    def initialize(self):
        self.channel_list = []
        self.guild = self.bot.get_guild(self.guild_id)
        LIST1 = self.guild.voice_channels
        for c_list in LIST1:
            self.channel_list.append(c_list.id)
        self.channel_count = len(self.channel_list)
        self.channel_count = self.channel_count - 1
        self.channel_id = self.channel_list[0]
        self.channel = self.bot.get_channel(self.channel_id)
        self.write_json()

    def vactor_select(self):
        self.actorlist = ['Donglong', 'Chico']
        self.vactor = random.choice(self.actorlist)
        if self.vactor == 'Donglong':
            self.interval = 2
        else:
            self.interval = 0.5

    def write_json(self):
        json_data = {}
        json_data["channel_list"] = self.channel_list
        json_data["channel_id"] = self.channel_id
        wf = open('channels.json', 'w')
        json.dump(json_data, wf)

    def read_json(self):
        rf = open('channels.json', 'r')
        json_data = json.load(rf)
        self.channel_list = json_data['channel_list']
        self.channel_count = len(self.channel_list)
        self.channel_count = self.channel_count - 1
        self.channel_id = json_data['channel_id']

    def cog_unload(self):
        self.time_check.cancel()

    def vc_counter(self):
        self.member_count = {}
        for ch_id in self.channel_list:
            id_list = []
            channel = self.bot.get_channel(ch_id)
            members = channel.members
            # ゼロクリア
            self.member_count[ch_id] = 0
            for member_id in members:
                if member_id.bot:
                    pass
                else:
                    id_list.append(member_id.id)
                    self.member_count[ch_id] = len(id_list)

        print('OK')
        # カウントが一番大きいチャンネルを取得
        max_user_channel = max(self.member_count, key=self.member_count.get)
        print(max_user_channel)
        self.channel_id = max_user_channel

    @commands.Cog.listener(name='on_ready')
    async def change_presence(self):
        self.initialize()
        await self.bot.change_presence(
            activity=discord.Game(self.time_zone))

    @commands.guild_only()
    @commands.command(name='start')
    async def start_loop(self, ctx):
        try:
            self.time_check.start()
            await ctx.send('started!!')
        except RuntimeError:
            await ctx.send('すでに動いてるで')

    @commands.guild_only()
    @commands.command(name='stop')
    async def stop_loop(self, ctx):
        self.time_check.stop()
        await ctx.send('stopping!!!!')

    @commands.guild_only()
    @commands.command(name='auto_select', aliases=['as'])
    async def toggle_auto_channel_select(self, ctx):
        if self.auto_channel_select:
            self.auto_channel_select = False
            await ctx.send('выключен')
        else:
            self.auto_channel_select = True
            await ctx.send('на')

    @ commands.command()
    async def test(self, ctx):
        await ctx.send('なにも起きないよ')

    @ commands.command()
    async def nowtime(self, ctx):
        await ctx.send(self.now)

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

    @commands.guild_only()
    @ commands.command()
    async def toggle_channel(self, ctx):
        self.channel_id = self.channel_list[self.channel_index]
        self.channel = self.bot.get_channel(self.channel_id)
        await ctx.send(self.channel.name + 'に変更しました。')

        if self.channel_index == self.channel_count:
            self.channel_index = 0
        else:
            self.channel_index = self.channel_index + 1

    @commands.guild_only()
    @commands.command()
    async def set_channel(self, ctx, *args):
        max_index = self.channel_count
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
        if new_index > max_index:
            await ctx.send(':thinking::thinking::thinking:')
            return
        if 0 > new_index:
            await ctx.send(':thinking::thinking::thinking:')
            return

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
        if self.auto_channel_select:
            self.vc_counter()

        self.channel = self.bot.get_channel(self.channel_id)

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

        self.vactor_select()

        try:
            await self.r_message.add_reaction(emoji)
        except AttributeError:
            pass

        self.playing = False

        return

    @commands.guild_only()
    @ commands.command()
    async def test_join(self, ctx, *args):
        now_datetime = datetime.datetime.now(
            pytz.timezone(self.time_zone)).strftime('%H:%M:%S')
        split_time = now_datetime.split(':')

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
                self.vactor = args[1]

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

        jikoku = str(jikoku)
        jikoku = jikoku.zfill(2)

        if '05' <= jikoku <= '10':
            pre_filepath = self.sound_base_path + \
                '{0}/pre/{1}.wav'.format(self.vactor, self.m_dice)
            post_filepath = self.sound_base_path + \
                '{0}/{1}.wav'.format(self.vactor, jikoku)
            self.m_dice = random.randint(1, 7)
        elif '11' <= jikoku <= '17':
            pre_filepath = self.sound_base_path + \
                '{0}/pre/{1}.wav'.format(self.vactor, self.d_dice)
            post_filepath = self.sound_base_path + \
                '{0}/{1}.wav'.format(self.vactor, jikoku)
            self.d_dice = random.randint(8, 11)
        elif '18' <= jikoku <= '24' or '00' <= jikoku <= '04':
            pre_filepath = self.sound_base_path + \
                '{0}/pre/{1}.wav'.format(self.vactor, self.n_dice)
            post_filepath = self.sound_base_path + \
                '{0}/{1}.wav'.format(self.vactor, jikoku)
            self.n_dice = random.randint(12, 15)

        while(self.playing):
            await asyncio.sleep(1)

        self.r_message = ctx.message

        await self.play_audio(pre_filepath, post_filepath)

    @ tasks.loop(seconds=1)
    async def time_check(self):
        now_datetime = datetime.datetime.now(
            pytz.timezone(self.time_zone)).strftime('%H:%M:%S')
        split_time = now_datetime.split(':')

        if split_time[1] == '00' and split_time[2] == '00':
            if '05' <= split_time[0] <= '10':
                pre_filepath = self.sound_base_path + \
                    '/{0}/pre/{1}.wav'.format(self.vactor, self.m_dice)
                post_filepath = self.sound_base_path + \
                    '{0}/{1}.wav'.format(self.vactor, split_time[0])
                self.m_dice = random.randint(1, 7)
            elif '11' <= split_time[0] <= '17':
                pre_filepath = self.sound_base_path + \
                    '{0}/pre/{1}.wav'.format(self.vactor, self.d_dice)
                post_filepath = self.sound_base_path + \
                    '{0}/{1}.wav'.format(self.vactor, split_time[0])
                self.d_dice = random.randint(8, 11)
            elif '18' <= split_time[0] <= '24' \
                    or '00' <= split_time[0] <= '04':
                pre_filepath = self.sound_base_path + \
                    '{0}/pre/{1}.wav'.format(self.vactor, self.n_dice)
                post_filepath = self.sound_base_path + \
                    '{0}/{1}.wav'.format(self.vactor, split_time[0])
                self.n_dice = random.randint(12, 15)

            if split_time[0] == '24':
                self.initialize()

            await self.play_audio(pre_filepath, post_filepath)


def setup(bot):
    bot.add_cog(Jihou(bot))
