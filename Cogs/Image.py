import asyncio
import os
import requests
import cv2
import discord
from discord.ext import commands
import json
import datetime


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
        
        # 回数制限があるAPI用のcountを持つjson
        api_count = 'api_count.json'
        with open(api_count, encoding="utf8") as f:
            api_count_json = json.loads(f.read())
        
        # 制限回数を更新
        dt_now = datetime.datetime.now()
        if api_count_json['alpha']['year'] != dt_now.year or api_count_json['alpha']['month'] != dt_now.month:
             api_count_json['alpha']['count'] = 50
             api_count_json['alpha']['year'] = dt_now.year
             api_count_json['alpha']['month'] = dt_now.month

        # 50回制限確認
        if api_count_json['alpha']['count'] <= 0:
            await ctx.send('月の50回越えてそうだからやめておこう')
            return

        try:
            # アップロードした画像URL、画像名取得
            img_url = ctx.message.attachments[0].url
            file_name = ctx.message.attachments[0].filename
        except:  # noqa
            await ctx.send('画像が足りないよ？')
            return
        
        # urlを元に画像を取得し、tmpフォルダに保存
        tmp_img_name = 'temp/{0}'.format(file_name)
        
        # ディレクトリ作成(存在していれば作成しない)
        os.makedirs('temp/', exist_ok=True)

        r = requests.get(img_url)
        if r.status_code == 200:
            with open(tmp_img_name, 'wb') as f:
                f.write(r.content)

        # 背景透過のAPIURL
        url = "https://api.remove.bg/v1.0/removebg"

        # post実行
        result = requests.post(url,
            data = {'size' : 'auto'},
            headers={'X-API-Key': 'LrTEjBryRmFCUgJWkx76G5Yd'},
            files={'image_file' : open(tmp_img_name, 'rb')})

        # status_codeを代入
        status_code = result.status_code

        # 成功
        if status_code == requests.codes.ok:
            img_name = 'temp/alpha/{0}'.format(file_name)

            # ディレクトリ作成(存在していれば作成しない)
            os.makedirs('temp/alpha/', exist_ok=True)

            with open(img_name, 'wb') as out:
                out.write(result.content)
                
            # 透過後の画像サイズ取得し、確認
            flip_size = os.path.getsize(img_name)
            if flip_size > 8178892:
                await ctx.send('8M超えました。')
                os.remove(img_name)
                os.remove(tmp_img_name)
                return
            
            # ファイルを取得し返す
            with open(img_name, "rb") as fh:
                f = discord.File(fh, filename=file_name)

                # alphaのカウントから1引く
                api_count_json['alpha']['count'] = api_count_json['alpha']['count'] - 1

                with open(api_count, encoding="utf8", mode="w") as jsonf:
                    jsonf.write(json.dumps(api_count_json, ensure_ascii=False))
            
                await ctx.send(content=('でけた(今月残り回数：多分{0}回)'.format(str(api_count_json['alpha']['count']))), file=f)
            
            os.remove(img_name)
            os.remove(tmp_img_name)

        else:
            await ctx.send('APIがエラー吐いた')
        
def setup(bot):
    bot.add_cog(Image(bot))