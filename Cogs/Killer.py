import os
import discord
from discord.ext import commands
from discord import option
from discord.commands import Option
import random

class Killer(commands.Cog):
    def __init__(self, bot: commands.bot) -> None:
        self.bot = bot

        # キラー一覧
        self.dbd:list = [
            "トラッパー", "レイス", "ヒルビリー", "ナース", "ハグ",
            "ドクター", "ハントレス", "シェイプ", "カニバル", "ナイトメア",
            "ピッグ", "クラウン", "スピリット", "リージョン", "プレイグ",
            "ゴーストフェイス", "デモゴルゴン", "鬼", "デススリンガー", "エクセキューショナー",
            "ブライト", "ツインズ", "トリックスター", "ネメシス", "セノバイト",
            "アーティスト", "貞子", "ドレッジ", "ウェスカー", "ナイト",
            "スカルマーチャント", "シンギュラリティ", "ゼノモーフ"
            ]
        self.ttcsm:list = [
            "レザーフェイス", "コック", "ヒッチハイカー", "ジョニー", "シシー"
        ]

    @commands.Cog.listener()
    async def on_ready(self):
        print(__name__)

    @commands.slash_command(description="DbD若しくはテキチェンのキラーを返します")
    async def killer(self, ctx: discord.ApplicationContext,
                        tgt_game: Option(str,"dbd or ttcsm",name="対象のゲーム")):
        tgt_game_upper:str = tgt_game.upper()
        if tgt_game_upper == "DBD":
            await ctx.respond(f'{random.choice(self.dbd)}')
        elif tgt_game_upper == "TTCSM":
            await ctx.respond(f'{random.choice(self.ttcsm)}')
        else:
            await ctx.respond(f'対応してないゲームの略称だよ～；；')

def setup(bot):
    bot.add_cog(Killer(bot))