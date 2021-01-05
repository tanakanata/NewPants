import asyncio
import random
import os
import cv2
import re
import discord
from discord.ext import commands
import numpy as np


class ColorImaging(commands.Cog):
    def __init__(self, bot: commands.bot):
        print('ColorImaging OK')
        self.bot = bot
        self.imaging = False

    @commands.command()
    async def rgb(self, ctx, *args):
        RGB = []

        while(self.imaging):
            await asyncio.sleep(1)

        self.imaging = True

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
            except ValueError:
                await ctx.send('使い方調べてから出直して')
                self.imaging = False
                return

        elif len(args) == 4:
            imgtype = 'apng'
            try:
                Red = int(args[0])
                Green = int(args[1])
                Blue = int(args[2])
                alpha = int(args[3])
            except ValueError:
                await ctx.send('使い方調べてから出直して')
                self.imaging = False
                return

        else:
            await ctx.send('引数の数とあなたの頭がおかしいよ？')
            self.imaging = False
            return

        if not 0 <= Red <= 255:
            await ctx.send('0 ~ 255以外うけつけませ～んw')
            self.imaging = False
            return
        elif not 0 <= Blue <= 255:
            await ctx.send('0 ~ 255以外うけつけませ～んw')
            self.imaging = False
            return
        elif not 0 <= Green <= 255:
            await ctx.send('0 ~ 255以外うけつけませ～んw')
            self.imaging = False
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

            self.imaging = False

        if imgtype == 'apng':
            img = np.zeros((400, 600, 4), np.uint8)
            RGB.append(Blue)
            RGB.append(Green)
            RGB.append(Red)

            if not 0 <= alpha <= 255:
                await ctx.send('0 ~ 255以外うけつけませ～んw')
                self.imaging = False
                return

            RGB.append(alpha)

            img[:, :, 0:4] = RGB
            cv2.imwrite('temp/GIF.png', img)

            with open("temp/GIF.png", "rb") as fh:
                f = discord.File(fh, filename="GIF.png")
            msg = 'R={0} G={1} B={2} α={3}'.format(Red, Green, Blue, alpha)

            await ctx.send(content=msg, file=f)

            os.remove('temp/GIF.png')

            self.imaging = False

    @commands.command()
    async def color(self, ctx, *args):
        RGB = []
        while(self.imaging):
            await asyncio.sleep(1)

        self.imaging = True

        if len(args) == 0:
            Red = random.randint(0, 255)
            Green = random.randint(0, 255)
            Blue = random.randint(0, 255)

            H_Blue = '{:02X}'.format(Blue)
            H_Green = '{:02X}'.format(Green)
            H_Red = '{:02X}'.format(Red)

            html = '{0}{1}{2}'.format(H_Red, H_Green, H_Blue)

        elif len(args) == 1:
            color = str(args[0])
            html = color.replace('#', '')

            if re.fullmatch(r'([0-9a-fA-F]){6}', html) == '':
                await ctx.send('は？')
                self.imaging = False
                return

            Red = int(html[0:2], 16)
            Green = int(html[2:4], 16)
            Blue = int(html[4:6], 16)

        else:
            await ctx.send('何かがおかしいよ？')
            self.imaging = False
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

        self.imaging = False


def setup(bot):
    bot.add_cog(ColorImaging(bot))
