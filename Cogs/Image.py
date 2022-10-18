import asyncio
import os
import requests
import cv2
import discord
from discord.ext import commands
import io
from urlextract import URLExtract

import config


class Image(commands.Cog):
    bot: commands.bot.Bot

    def __init__(self, bot: commands.bot.Bot):
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
        MAX_FREE_CALLS = 50
        # 残り回数確認APIURL
        api_url = "https://api.remove.bg/v1.0/account"

        # apikeyの数だけループ
        loop_count = 0
        for alpha in config.alpha:
            loop_count += 1
            result = requests.get(api_url,
                                  headers={'X-API-Key': alpha})
            if result.json()['data']['attributes']['api']['free_calls'] > 0:
                alpha_api_key = alpha
                break

        # 残回数取得
        leftover = result.json()['data']['attributes']['api']['free_calls']

        # 回数制限確認
        if leftover <= 0:
            await ctx.send('月の' + str(len(config.alpha) * MAX_FREE_CALLS) + '回越えてそうだからやめておこう')
            return

        try:
            # アップロードした画像URL、画像名取得
            img_attachment = await self.get_last_image(ctx)
            filename = img_attachment.filename
        except:  # noqa
            await ctx.send('画像が足りないよ？')
            return

        # 背景透過のAPIURL
        api_url = "https://api.remove.bg/v1.0/removebg"

        # post実行
        result = requests.post(api_url,
                               data={'size': 'auto'},
                               headers={'X-API-Key': alpha_api_key},
                               files={'image_file': io.BytesIO(await img_attachment.read())})

        # status_codeを代入
        status_code = result.status_code

        # 成功
        if status_code == requests.codes.ok:
            # 透過後の画像サイズ取得し、確認
            if len(result.content) > 8178892:
                await ctx.send('8M超えました。')
                return

            f = discord.File(io.BytesIO(result.content), filename=filename)

            # 残回数を計算
            leftover = MAX_FREE_CALLS * (len(config.alpha) - loop_count) + leftover

            await ctx.send(content=('でけた(今月残り回数：{0}回)'.format(leftover - 1)), file=f)

        elif status_code == 400:
            error_code = result.json()['errors'][0]['code']
            if error_code == 'unknown_foreground':
                await ctx.send('背景が認識できませんでした')

            else:
                await ctx.send('APIがエラー吐いた')

        else:
            await ctx.send('APIがエラー吐いた')

    async def get_last_image(self, ctx: commands.Context) -> discord.Attachment:
        last_attachment = None
        last_url = None
        extractor = URLExtract()
        async for m in ctx.message.channel.history(limit=25):
            if m.attachments:
                last_attachment = m.attachments[0]
                if self.is_image(last_attachment.url):
                    return last_attachment
            if m.content:
                all_urls = extractor.find_urls(m.content)
                if all_urls:
                    last_url = all_urls[0]
                    if self.is_image(last_url):
                        return AttachmentLike(last_url)

        raise RuntimeError('Image not found')

    def is_image(self, url: str):
        try:
            response = requests.head(url)
            mime = response.headers.get('Content-type', '').lower()
            if "image" in mime:
                return True
            else:
                return False
        except:
            return False


def setup(bot):
    bot.add_cog(Image(bot))


# DiscordのAttachmentっぽいクラス
# urlからfilenameっぽいものを作る
# url, filename, async read() がほしい
# https://discordpy.readthedocs.io/en/stable/api.html#attachment
class AttachmentLike:
    def __init__(self, url: str) -> None:
        self.url = url
        filename = url.rstrip("/").split("/")[-1]
        self.filename = f"#{filename}.png"

    async def read(self) -> bytes:
        return requests.get(self.url).content
