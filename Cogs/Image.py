import asyncio
import os
import requests
import cv2
import discord
from discord.ext import commands
import json
import datetime
import io
import config


class Image(commands.Cog):
    def __init__(self, bot: commands.bot):
        print('Image OK')
        self.bot = bot
        self.cv2 = cv2
        self.flipping = None

    @commands.command()
    async def flip(self, ctx, mode='n'):
        try:
            img_url = ctx.message.attachments[0].url
            file_name = ctx.message.attachments[0].filename
        except:  # noqa
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

        while(self.flipping):
            await asyncio.sleep(1)

        self.flipping = True

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
        except:  # noqa
            await ctx.send('対応してないファイルだよ？')
            self.flipping = False
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

        self.flipping = False

        os.remove(img_name)
        os.remove(tmp_img_name)

    @commands.command()
    async def alpha(self, ctx, mode='n'):
        
        # 残り回数確認APIURL
        api_url = "https://api.remove.bg/v1.0/account"

        # api実行
        result = requests.get(api_url,
            headers={'X-API-Key': config.alpha})
        
        # 残回数取得
        leftover = result.json()['data']['attributes']['api']['free_calls']

        # 50回制限確認
        if leftover <= 0:
            await ctx.send('月の50回越えてそうだからやめておこう')
            return

        try:
            # アップロードした画像URL、画像名取得
            img_url = ctx.message.attachments[0].url
            file_name = ctx.message.attachments[0].filename
        except:  # noqa
            await ctx.send('画像が足りないよ？')
            return

        # 背景透過のAPIURL
        api_url = "https://api.remove.bg/v1.0/removebg"

        # post実行
        result = requests.post(api_url,
            data = {'size' : 'auto'},
            headers={'X-API-Key': config.alpha},
            files={'image_file' : io.BytesIO(await ctx.message.attachments[0].read())})

        # status_codeを代入
        status_code = result.status_code

        # 成功
        if status_code == requests.codes.ok:
            # 透過後の画像サイズ取得し、確認
            if len(result.content) > 8178892:
                await ctx.send('8M超えました。')
                return
            
            f = discord.File(io.BytesIO(result.content), filename=file_name)
        
            await ctx.send(content=('でけた(今月残り回数：{0}回)'.format(leftover - 1)), file=f)

        else:
            await ctx.send('APIがエラー吐いた')
        
def setup(bot):
    bot.add_cog(Image(bot))