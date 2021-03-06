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
import re
import requests
import cv2
import numpy as np
from discord.ext import commands, tasks
import discord
from pathlib import Path
from pykakasi import kakasi

# -----------------------------------------------------------------------------------------
TOKEN = config.AT
tz = config.TZ
client = discord.Client()
kakasi = kakasi()
CHANNEL_ID = int(config.VC_id1)
SOUND_BASE_PATH = os.path.dirname(os.path.abspath(__file__)) + '/'
PLAYING = False
IMAGING = False
Flipping = False
intents = discord.Intents.all()
# -----------------------------------------------------------------------------------------

tokyo_timezone = pytz.timezone('Asia/Tokyo')

bot = commands.Bot(command_prefix='!', help_command=None, intents=intents)

bot.remove_command('help')


@bot.event
async def on_ready():
    global channel, now, M_dice, D_dice, N_dice

    channel = bot.get_channel(CHANNEL_ID)
    now = datetime.datetime.now(pytz.timezone(tz)).strftime('%H:%M:%S')
    M_dice = random.randint(1, 7)
    D_dice = random.randint(8, 11)
    N_dice = random.randint(12, 15)

    print('--------------------')
    print('ログインしました')
    print(bot.user.name)
    print(bot.user.id)
    print(discord.__version__)
    print('起動時刻')
    print(config.TZ)
    print(now)
    print('--------------------')
    await bot.change_presence(activity=discord.Game(tz))


@bot.command()
async def help(ctx):
    with open("help.png", "rb") as fh:
        f = discord.File(fh, filename="help.png")

    await ctx.send(file=f)


@bot.command()
async def flip(ctx, mode='n'):
    global Flipping
    try:
        img_url = ctx.message.attachments[0].url
        file_name = ctx.message.attachments[0].filename
    except:
        await ctx.send('画像が足りないよ？')
        return

    if mode == 'h':
        md = 1
    elif mode == 'v':
        md = 0
    elif mode == 'vh' or mode == 'hv':
        md = -1
    else:
        await ctx.send('モードを指定してね \n上下 : v\n左右 : h\n上下左右 : vh or hv')
        return

    while(Flipping):
        await asyncio.sleep(1)

    Flipping = True

    tmp_img_name = 'temp/{0}'.format(file_name)

    r = requests.get(img_url)
    if r.status_code == 200:
        with open(tmp_img_name, 'wb') as f:
            f.write(r.content)

    img_name = 'temp/flip/{0}'.format(file_name)

    tmp_size = os.path.getsize(tmp_img_name)
    if tmp_size > 8388608:
        await ctx.send('は？')
        os.remove(tmp_img_name)
        return

    img = cv2.imread(tmp_img_name)

    flip_img = cv2.flip(img, md)
    try:
        cv2.imwrite(img_name, flip_img)
    except:
        await ctx.send('対応してないファイルだよ？')
        Flipping = False
        return

    flip_size = os.path.getsize(img_name)
    if flip_size > 8178892:
        await ctx.send('8M超えました。')
        os.remove(img_name)
        os.remove(tmp_img_name)
        return

    with open(img_name, "rb") as fh:
        f = discord.File(fh, filename=file_name)

    await ctx.send(content='でけた', file=f)

    Flipping = False

    os.remove(img_name)
    os.remove(tmp_img_name)


def download_img(img_url, file_name):
    r = requests.get(img_url, stream=True)
    if r.status_code == 200:
        with open(file_name, 'wb') as f:
            f.write(r.content)


@bot.command()
async def rgb(ctx, *args):
    global IMAGING
    RGB = []

    while(IMAGING):
        await asyncio.sleep(1)

    IMAGING = True

    if len(args) == 0:
        imgtype = 'png'
        Red = random.randint(0, 255)
        Green = random.randint(0, 255)
        Blue = random.randint(0, 255)

    elif len(args) == 3:
        imgtype = 'png'
        try:
            Red = int(args[0])
            Green = int(args[1])
            Blue = int(args[2])
        except:
            await ctx.send('使い方調べてから出直して')
            IMAGING = False
            return

    elif len(args) == 4:
        imgtype = 'apng'
        try:
            Red = int(args[0])
            Green = int(args[1])
            Blue = int(args[2])
            alpha = int(args[3])
        except:
            await ctx.send('使い方調べてから出直して')
            IMAGING = False
            return

    else:
        await ctx.send('引数の数とあなたの頭がおかしいよ？')
        IMAGING = False
        return

    if not 0 <= Red <= 255:
        await ctx.send('0 ~ 255以外うけつけませ～んw')
        IMAGING = False
        return
    elif not 0 <= Blue <= 255:
        await ctx.send('0 ~ 255以外うけつけませ～んw')
        IMAGING = False
        return
    elif not 0 <= Green <= 255:
        await ctx.send('0 ~ 255以外うけつけませ～んw')
        IMAGING = False
        return

    if imgtype == 'png':
        img = np.zeros((400, 600, 3), np.uint8)
        RGB.append(Blue)
        RGB.append(Green)
        RGB.append(Red)

        H_Blue = '{:02X}'.format(Blue)
        H_Green = '{:02X}'.format(Green)
        H_Red = '{:02X}'.format(Red)

        html = '#{0}{1}{2}'.format(H_Red, H_Green, H_Blue)

        img[:, :, 0:3] = RGB
        cv2.imwrite('temp/JPEG.png', img)

        with open("temp/JPEG.png", "rb") as fh:
            f = discord.File(fh, filename="JPEG.png")

        msg = 'R={0} G={1} B={2} \n{3}'.format(Red, Green, Blue, html)

        await ctx.send(content=msg, file=f)

        os.remove('temp/JPEG.png')

        IMAGING = False

    if imgtype == 'apng':
        img = np.zeros((400, 600, 4), np.uint8)
        RGB.append(Blue)
        RGB.append(Green)
        RGB.append(Red)

        if not 0 <= alpha <= 255:
            await ctx.send('0 ~ 255以外うけつけませ～んw')
            IMAGING = False
            return

        RGB.append(alpha)

        img[:, :, 0:4] = RGB
        cv2.imwrite('temp/GIF.png', img)

        with open("temp/GIF.png", "rb") as fh:
            f = discord.File(fh, filename="GIF.png")
        msg = 'R={0} G={1} B={2} α={3}'.format(Red, Green, Blue, alpha)

        await ctx.send(content=msg, file=f)

        os.remove('temp/GIF.png')

        IMAGING = False


@bot.command()
async def color(ctx, *args):
    global IMAGING
    RGB = []
    print(args)
    while(IMAGING):
        await asyncio.sleep(1)

    IMAGING = True

    if len(args) == 0:
        Red = random.randint(0, 255)
        Green = random.randint(0, 255)
        Blue = random.randint(0, 255)

        H_Blue = '{:02X}'.format(Blue)
        H_Green = '{:02X}'.format(Green)
        H_Red = '{:02X}'.format(Red)

        html = '{0}{1}{2}'.format(H_Red, H_Green, H_Blue)

    elif len(args) == 1:
        print(args[0])
        color = str(args[0])
        print(args)
        html = color.replace('#', '')
        print(html)

        if re.fullmatch(r'([0-9a-fA-F]){6}', html) == None:
            await ctx.send('は？')
            IMAGING = False
            return

        Red = int(html[0:2], 16)
        Green = int(html[2:4], 16)
        Blue = int(html[4:6], 16)

    else:
        await ctx.send('何かがおかしいよ？')
        IMAGING = False
        return

    img = np.zeros((400, 600, 3), np.uint8)
    RGB.append(Blue)
    RGB.append(Green)
    RGB.append(Red)

    img[:, :, 0:3] = RGB
    cv2.imwrite('temp/JPEG.png', img)

    with open("temp/JPEG.png", "rb") as fh:
        f = discord.File(fh, filename="JPEG.png")

    msg = 'R={0} G={1} B={2} \n#{3}'.format(Red, Green, Blue, html)

    await ctx.send(content=msg, file=f)

    os.remove('temp/JPEG.png')

    IMAGING = False


@bot.command()
async def boin(ctx, *arg):
    if len(arg) == 0:
        await ctx.send('文章を入力しろ　ボケ　カス　雑魚　無能　ハゲ　増毛')
        return
    # 漢字・ひらがなをカタカナに変換
    arg = str(arg)
    mojiretsu = arg.translate(str.maketrans({'"': '', "ー": "～", "ｰ": "～"}))
    mojiretsu = mojiretsu.replace("||", "").replace('"', '').replace(
        "('", "").replace("',)", "").replace("')", "").replace("', '", " ")
    kakasi.setMode('J', 'K')
    kakasi.setMode("H", "K")
    conv = kakasi.getConverter()
    katakana = conv.do(mojiretsu)
    text = katakana.translate(str.maketrans({"ﾟ": "", "ﾞ": ""}))
    # 大文字とゥの変換リスト
    large_tone = {
        'ア': 'ア', 'イ': 'イ', 'ウ': 'ウ', 'エ': 'エ', 'オ': 'オ',
        'ァ': 'ア', 'ィ': 'イ', 'ゥ': 'ウ', 'ェ': 'エ', 'ォ': 'オ',
        'ヴ': 'ウ',
        'カ': 'ア', 'キ': 'イ', 'ク': 'ウ', 'ケ': 'エ', 'コ': 'オ',
        'サ': 'ア', 'シ': 'イ', 'ス': 'ウ', 'セ': 'エ', 'ソ': 'オ',
        'タ': 'ア', 'チ': 'イ', 'ツ': 'ウ', 'テ': 'エ', 'ト': 'オ',
        'ッ': 'ウ',
        'ナ': 'ア', 'ニ': 'イ', 'ヌ': 'ウ', 'ネ': 'エ', 'ノ': 'オ',
        'ハ': 'ア', 'ヒ': 'イ', 'フ': 'ウ', 'ヘ': 'エ', 'ホ': 'オ',
        'マ': 'ア', 'ミ': 'イ', 'ム': 'ウ', 'メ': 'エ', 'モ': 'オ',
        'ヤ': 'ア', 'ユ': 'ウ', 'ヨ': 'オ',
        'ャ': 'ア', 'ュ': 'ウ', 'ョ': 'オ',
        'ラ': 'ア', 'リ': 'イ', 'ル': 'ウ', 'レ': 'エ', 'ロ': 'オ',
        'ワ': 'ア', 'ヲ': 'オ', 'ン': 'ン',
        'ヮ': 'ア',
        'ガ': 'ア', 'ギ': 'イ', 'グ': 'ウ', 'ゲ': 'エ', 'ゴ': 'オ',
        'ザ': 'ア', 'ジ': 'イ', 'ズ': 'ウ', 'ゼ': 'エ', 'ゾ': 'オ',
        'ダ': 'ア', 'ヂ': 'イ', 'ヅ': 'ウ', 'デ': 'エ', 'ド': 'オ',
        'バ': 'ア', 'ビ': 'イ', 'ブ': 'ウ', 'ベ': 'エ', 'ボ': 'オ',
        'パ': 'ア', 'ピ': 'イ', 'プ': 'ウ', 'ペ': 'エ', 'ポ': 'オ',
        'ｱ': 'ア', 'ｲ': 'イ', 'ｳ': 'ウ', 'ｴ': 'エ', 'ｵ': 'オ',
        'ｧ': 'ア', 'ｨ': 'イ', 'ｩ': 'ウ', 'ｪ': 'エ', 'ｫ': 'オ',
        'ｳﾞ': 'ウ',
        'ｶ': 'ア', 'ｷ': 'イ', 'ｸ': 'ウ', 'ｹ': 'エ', 'ｺ': 'オ',
        'ｻ': 'ア', 'ｼ': 'イ', 'ｽ': 'ウ', 'ｾ': 'エ', 'ｿ': 'オ',
        'ﾀ': 'ア', 'ﾁ': 'イ', 'ﾂ': 'ウ', 'ﾃ': 'エ', 'ﾄ': 'オ',
        'ｯ': 'ウ',
        'ﾅ': 'ア', 'ﾆ': 'イ', 'ﾇ': 'ウ', 'ﾈ': 'エ', 'ﾉ': 'オ',
        'ﾊ': 'ア', 'ﾋ': 'イ', 'ﾌ': 'ウ', 'ﾍ': 'エ', 'ﾎ': 'オ',
        'ﾏ': 'ア', 'ﾐ': 'イ', 'ﾑ': 'ウ', 'ﾒ': 'エ', 'ﾓ': 'オ',
        'ﾔ': 'ア', 'ﾕ': 'ウ', 'ﾖ': 'オ',
        'ｬ': 'ア', 'ｭ': 'ウ', 'ｮ': 'オ',
        'ﾗ': 'ア', 'ﾘ': 'イ', 'ﾙ': 'ウ', 'ﾚ': 'エ', 'ﾛ': 'オ',
        'ﾜ': 'ア', 'ｦ': 'オ', 'ﾝ': 'ン',
        'ｶﾞ': 'ア', 'ｷﾞ': 'イ', 'ｸﾞ': 'ウ', 'ｹﾞ': 'エ', 'ｺﾞ': 'オ',
        'ｻﾞ': 'ア', 'ｼﾞ': 'イ', 'ｽﾞ': 'ウ', 'ｾﾞ': 'エ', 'ｿﾞ': 'オ',
        'ﾀﾞ': 'ア', 'ﾁﾞ': 'イ', 'ﾂﾞ': 'ウ', 'ﾃﾞ': 'エ', 'ﾄﾞ': 'オ',
        'ﾊﾞ': 'ア', 'ﾋﾞ': 'イ', 'ﾌﾞ': 'ウ', 'ﾍﾞ': 'エ', 'ﾎﾞ': 'オ',
        'ﾊﾟ': 'ア', 'ﾋﾟ': 'イ', 'ﾌﾟ': 'ウ', 'ﾍﾟ': 'エ', 'ﾎﾟ': 'オ'
    }

    # 大文字を母音に変換
    text = list(text)
    for i, v in enumerate(text):
        if v in large_tone:
            text[i] = large_tone[v]
    text = ''.join(text)

    # 残った小文字を母音に変換
    # for k,v in zip('ヮャュョッ','アアウオウ'):
    #     text = text.replace(k,v)
    if text == "":
        await ctx.send('変換したら文字なくなちゃった (*ﾉω・*)ﾃﾍ')
        return

    await ctx.send(text)


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
async def dice(ctx, *args):
    if len(args) == 1:
        try:
            atai = int(args[0])
        except:
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
        await ctx.send('はじめまして。NewPantsBotのダイス担当です。只今の結果は ' + str(kekka) + ' です。')


@bot.command()
async def ping(ctx):
    await ctx.send('PONG {0}'.format(
        tokyo_timezone.localize(
            (ctx.message.created_at + datetime.timedelta(hours=9))
        ).strftime('%Y-%m-%d %H:%M:%S.%f')
    ))


@bot.command()
async def toggle_channel(ctx):
    global CHANNEL_ID, channel
    if CHANNEL_ID == 610568928233521152:
        CHANNEL_ID = 618082304484442123
        channel = bot.get_channel(CHANNEL_ID)
        await ctx.send(channel.name + 'に変更しました。')
    elif CHANNEL_ID == 618082304484442123:
        CHANNEL_ID = 769665765283463208
        channel = bot.get_channel(CHANNEL_ID)
        await ctx.send(channel.name + 'に変更しました。')
    elif CHANNEL_ID == 769665765283463208:
        CHANNEL_ID = 788347573479407616
        channel = bot.get_channel(CHANNEL_ID)
        await ctx.send(channel.name + 'に変更しました。')
    elif CHANNEL_ID == 788347573479407616:
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
async def SV(ctx):
    await discord.VoiceChannel.connect(channel)


@bot.command()
async def test_join(ctx, *args):
    global M_dice, D_dice, N_dice, r_message, interval, Vactor
    now_datetime = datetime.datetime.now(
        pytz.timezone(tz)).strftime('%H:%M:%S')
    today = datetime.datetime.now(pytz.timezone(tz)).strftime('%m%d')
    split_time = now_datetime.split(':')
    actorlist = ['Donglong', 'Chico']
    Vactor = random.choice(actorlist)

    if len(args) == 0:
        jikoku = int(split_time[0])

    elif len(args) == 1:
        try:
            jikoku = int(args[0])
        except:
            await ctx.send('引数間違えないでください！！！！！')
            return
    elif len(args) == 2:
        try:
            jikoku = int(args[0])
        except:
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
        await ctx.send('地球上では1日って24時間なんですよ。そんなことも知らないんですか？？？小学校からやり直したほうがいいですよ？？？？')
        return

    if Vactor == 'Donglong':
        interval = 2

    else:
        interval = 0.5

    jikoku = str(jikoku)
    jikoku = jikoku.zfill(2)
    V1 = Vactor

    if '05' <= jikoku <= '10':
        pre_filepath = SOUND_BASE_PATH + \
            '{0}/pre/{1}.wav'.format(Vactor, M_dice)
        post_filepath = SOUND_BASE_PATH + '{0}/{1}.wav'.format(Vactor, jikoku)
        M_dice = random.randint(1, 7)
        Vactor = random.choice(actorlist)
    elif '11' <= jikoku <= '17':
        pre_filepath = SOUND_BASE_PATH + \
            '{0}/pre/{1}.wav'.format(Vactor, D_dice)
        post_filepath = SOUND_BASE_PATH + '{0}/{1}.wav'.format(Vactor, jikoku)
        D_dice = random.randint(8, 11)
        Vactor = random.choice(actorlist)
    elif '18' <= jikoku <= '24' or '00' <= jikoku <= '04':
        pre_filepath = SOUND_BASE_PATH + \
            '{0}/pre/{1}.wav'.format(Vactor, N_dice)
        post_filepath = SOUND_BASE_PATH + '{0}/{1}.wav'.format(Vactor, jikoku)
        N_dice = random.randint(12, 15)
        Vactor = random.choice(actorlist)

    if today == '1225' and V1 == 'Donglong':
        pre_filepath = SOUND_BASE_PATH + 'Donglong/me.wav'

    while(PLAYING):
        await asyncio.sleep(1)

    r_message = ctx.message

    await play_audio(pre_filepath, post_filepath)


async def play_audio(pre_filepath, post_filepath):
    global PLAYING
    audio1 = discord.FFmpegPCMAudio(pre_filepath)
    audio2 = discord.FFmpegPCMAudio(post_filepath)
    emoji = '\N{BLACK RIGHT-POINTING TRIANGLE}'

    while(PLAYING):
        await asyncio.sleep(1)

    PLAYING = True

    voice = await discord.VoiceChannel.connect(channel)

    asyncio.sleep(0.5)

    voice.play(audio1)

    while voice.is_playing():
        await asyncio.sleep(1)

    audio1.cleanup()
    voice.play(audio2)

    while voice.is_playing():
        await asyncio.sleep(1)

    audio2.cleanup()

    asyncio.sleep(interval)

    await voice.disconnect()

    try:
        r_message
        await r_message.add_reaction(emoji)
    except NameError:
        pass

    PLAYING = False

    return


@bot.command()
async def test(ctx):
    # guild = bot.get_guild(610568927768084499)
    # textch = guild.text_channels
    # vcch = guild.voice_channels
    chuwa = bot.get_channel(CHANNEL_ID)
    await ctx.send(chuwa.members)


@tasks.loop(seconds=1)
async def loop():
    global M_dice, D_dice, N_dice, interval, Vactor
    now_datetime = datetime.datetime.now(
        pytz.timezone(tz)).strftime('%H:%M:%S')
    today = datetime.datetime.now(pytz.timezone(tz)).strftime('%m%d')
    split_time = now_datetime.split(':')
    actorlist = ['Donglong', 'Chico']
    Vactor = random.choice(actorlist)

    if Vactor == 'Donglong':
        interval = 2

    else:
        interval = 0.5

    V1 = Vactor

    if split_time[1] == '00' and split_time[2] == '00':
        if '05' <= split_time[0] <= '10':
            pre_filepath = SOUND_BASE_PATH + \
                '{0}/pre/{1}.wav'.format(Vactor, M_dice)
            post_filepath = SOUND_BASE_PATH + \
                '{0}/{1}.wav'.format(Vactor, split_time[0])
            M_dice = random.randint(1, 7)
            Vactor = random.choice(actorlist)
        elif '11' <= split_time[0] <= '17':
            pre_filepath = SOUND_BASE_PATH + \
                '{0}/pre/{1}.wav'.format(Vactor, D_dice)
            post_filepath = SOUND_BASE_PATH + \
                '{0}/{1}.wav'.format(Vactor, split_time[0])
            D_dice = random.randint(8, 11)
            Vactor = random.choice(actorlist)
        elif '18' <= split_time[0] <= '24' or '00' <= split_time[0] <= '04':
            pre_filepath = SOUND_BASE_PATH + \
                '{0}/pre/{1}.wav'.format(Vactor, N_dice)
            post_filepath = SOUND_BASE_PATH + \
                '{0}/{1}.wav'.format(Vactor, split_time[0])
            N_dice = random.randint(12, 15)
            Vactor = random.choice(actorlist)

        if today == '1225' and V1 == 'Donglong':
            pre_filepath = SOUND_BASE_PATH + 'Donglong/me.wav'

        await play_audio(pre_filepath, post_filepath)


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
