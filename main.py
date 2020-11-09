import config
import time
import asyncio
import datetime
import math
import sys
import os
import random
import json
import subprocess
import pytz
from discord.ext import commands, tasks
import discord
from pathlib import Path

# -----------------------------------------------------------------------------------------
TOKEN = config.AT
tz = config.TZ
client = discord.Client()
CHANNEL_ID = int(config.VC_id1)
SOUND_BASE_PATH = os.path.dirname(os.path.abspath(__file__)) + '/'
# -----------------------------------------------------------------------------------------

tokyo_timezone = pytz.timezone('Asia/Tokyo')

bot = commands.Bot(command_prefix='_')
# print(dir(bot))

@bot.event
async def on_ready():
    global channel,now,dice
    
    channel = bot.get_channel(CHANNEL_ID)
    now = datetime.datetime.now(pytz.timezone(tz)).strftime('%H:%M:%S')
    dice = random.randint(0, 9)

    print('--------------------')
    print('ログインしました')
    print(bot.user.name)
    print(bot.user.id)
    print(discord.__version__)
    print('起動時刻')
    print(config.TZ)
    print(now)
    print(dice)
    print('--------------------')
    await bot.change_presence(activity=discord.Game(tz))

@bot.command()
async def nowtime(ctx):
    await ctx.send(now)

@bot.command()
async def timezone(ctx):
    await ctx.send(tz)

@bot.command()
async def list_timezone(ctx):
    timeZoneList = pytz.common_timezones
    timeZoneListJoined = '\n'.join(timeZoneList)

    discordTextMaxLength = 1950
    if len(timeZoneListJoined) <= discordTextMaxLength :
        #2000以下
        await ctx.send(f'```{timeZoneList}```')
    else :
        partMessageBody = ""
        partMessageNum = 1

        for line in timeZoneList :
            if len(partMessageBody) + len(line) >= discordTextMaxLength :
                await ctx.send(f'```{partMessageBody}```')
                partMessageBody = ""
                partMessageNum += 1
            partMessageBody += line + '\n'

        await ctx.send(f'```{partMessageBody}```')

@bot.command()
async def set_timezone(ctx, new_timezone: str):
    if new_timezone in pytz.common_timezones:
        global tz, now
        tz = new_timezone
        now = datetime.datetime.now(pytz.timezone(tz)).strftime('%H:%M:%S')
        await ctx.send('新しいタイムゾーンを' + tz + 'にセットしました')
        await bot.change_presence(activity=discord.Game(tz))
    else:
        await ctx.send("そんなもの存在しませ〜んw")


@bot.command()
async def set_dice(ctx,*args):
    global dice
    if len(args) == 0:
        dice = random.randint(0,9)
    else:
        try:
            dice = int(args[0])
        except:
            await ctx.send('数字を入力してね')
            return
    await ctx.send(dice)

@bot.command()
async def ping(ctx):
    await ctx.send('PONG {0}'.format(
        tokyo_timezone.localize(
            (ctx.message.created_at + datetime.timedelta(hours=9))
        ).strftime('%Y-%m-%d %H:%M:%S.%f')
    ))

@bot.command()
async def toggle_channel(ctx):
    global CHANNEL_ID,channel
    if CHANNEL_ID == 610568928233521152:
        CHANNEL_ID = 618082304484442123
        channel = bot.get_channel(CHANNEL_ID)
        await ctx.send(channel.name + 'に変更しました。')
    elif CHANNEL_ID == 407151800060346368:
        CHANNEL_ID = 769665765283463208
        channel = bot.get_channel(CHANNEL_ID)
        await ctx.send(channel.name + 'に変更しました。')
    elif CHANNEL_ID == 769665765283463208:
        CHANNEL_ID = 610569245025239080
        channel = bot.get_channel(CHANNEL_ID)
        await ctx.send(channel.name + 'に変更しました。')
    elif CHANNEL_ID == 610569245025239080:
        CHANNEL_ID = 610568928233521152
        channel = bot.get_channel(CHANNEL_ID)
        await ctx.send(channel.name + 'に変更しました。')

@bot.command()
async def now_channel(ctx):
    global channel
    await ctx.send(channel.name + 'です。')

@bot.command()
async def test_join(ctx, *args):
    global dice
    filepath = ""
    # repeat = 12
    # if len(args) >= 1:
    #     try:
    #         repeat = int(args[0])
    #     except:
    #         await ctx.send('1-12の数字を入力してね')
    #         return
    # else:
    #     repeat = random.randint(1,12)
    
    # if dice == 0:
    #     filepath = SOUND_BASE_PATH + "uguisu.mp3"
    # elif 1<=repeat and repeat <= 12:
    #     filepath = SOUND_BASE_PATH + \
    #         '{0:02d}.mp3'.format(repeat)
    # else :
    #     await ctx.send('1-12の数字を入力してね')
    #     return
    filepath = SOUND_BASE_PATH + "hato.mp3"
    await play_audio(filepath)

async def play_audio(filepath):
    global dice
    print('play_audio {}'.format(filepath))
    audio = discord.FFmpegPCMAudio(filepath)
    voice = await discord.VoiceChannel.connect(channel)
    voice.play(audio)

    while voice.is_playing():
        await asyncio.sleep(1)

    audio.cleanup()
    await voice.disconnect()

    dice = random.randint(0, 9)
    return


@tasks.loop(seconds=1)
async def loop():
    global dice
    now_datetime = datetime.datetime.now(pytz.timezone(tz)).strftime('%I:%M:%S')
    split_time = now_datetime.split(':')
    if split_time[1] == '00' and split_time[2] == '00':
#    if split_time[2] == '00':
        if dice == 0:
            filepath = SOUND_BASE_PATH + "uguisu.mp3"
        else:
            # %I = 12時間表記♡
            filepath = SOUND_BASE_PATH + "hato.mp3"
        
        await play_audio(filepath)


@bot.event
async def on_message(message):
    if message.content.startswith('PONG ') and message.author.id == bot.user.id:
        time_now = message.content.replace('PONG ', '')
        ping_time = tokyo_timezone.localize(
            datetime.datetime.strptime(time_now, '%Y-%m-%d %H:%M:%S.%f'))
        post_time = tokyo_timezone.localize(message.created_at +
                                            datetime.timedelta(hours=9))
        diff_time = post_time - ping_time
        await message.edit(content='PONG({0}ms)'.format((diff_time.seconds * 1000) + int(str(diff_time.microseconds)[:3])))
    # on_messageをつかうと裏で暗黙に動いていたprocess_commandが上書きされてしまうので、明示的にprocess_commandsを呼ぶ
    # https://github.com/Rapptz/discord.py/blob/v1.2.5/discord/ext/commands/bot.py#L900-L901
    await bot.process_commands(message)

# MyBotのインスタンス化及び起動処理。
if __name__ == '__main__':
    loop.start()
    bot.run(TOKEN)  # Botのトークン
    
