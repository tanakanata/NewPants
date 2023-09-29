import os
import deepl
import discord
from discord.ext import commands
from discord import option
from discord.commands import Option

class Translate(commands.Cog):
    def __init__(self, bot: commands.bot) -> None:
        self.bot = bot
        self.src_langs:dict = {}
        self.src_lang_code_list:list = []
        self.tgt_langs:dict = {}
        self.tgt_lang_code_list:list = []
        self.translator = deepl.Translator(os.environ["DEEPL"])
        self.get_languages()

    @commands.Cog.listener()
    async def on_ready(self):
        print(__name__)

    def get_languages(self):
        for lang in self.translator.get_source_languages():
            self.src_langs[lang.name] = lang.code
            self.src_lang_code_list.append(lang.code)
        
        for lang in self.translator.get_target_languages():
            self.tgt_langs[lang.name] = lang.code
            self.tgt_lang_code_list.append(lang.code)
        
        print(self.tgt_lang_code_list)

    def get_src_language_names(self):
        return [lang for lang in self.src_lang_code_list]

    def get_tgt_language_names(self,ctx):
        return [lang for lang in self.tgt_lang_code_list if lang.startswitch(ctx.value)]
    
    def get_count_and_limit(self):
        usage = self.translator.get_usage()
        count = usage.character.count
        limit = usage.character.limit
        return count, limit
    
    @commands.slash_command(name="lang",description="翻訳可能言語一覧を送信します。")
    async def list_target_languages(self,ctx:discord.ApplicationContext):
        msg = "```翻訳可能言語"
        for k,v in self.tgt_langs.items():
            msg = msg + f'\n{k} : {v}'

        msg = msg + "```"
        await ctx.respond(msg)

    @commands.slash_command(description="翻訳します。")
    async def translate(self, ctx: discord.ApplicationContext,
                        tgt_lang: Option(str,"翻訳先言語コード",name="言語"), 
                        text: Option(str,"翻訳したいテキスト",name="テキスト")):

        discord_text_max_length = 1950

        if tgt_lang.upper() == "EN":
            tgt_lang = "EN-US"

        data = self.get_count_and_limit()
        count, limit = data[0], data[1]
        remain = limit - count

        if count + len(text) > limit:
            await ctx.respond("今月の上限を超えちゃうよ。")
            return

        if tgt_lang.upper() not in self.tgt_lang_code_list:
            await ctx.respond("翻訳先の言語指定がおかしいよ")
            return

        result = self.translator.translate_text(text=text, target_lang=tgt_lang)

        

        if len(result.text) + len(result.detected_source_lang) <= discord_text_max_length:
            rst_joined_text = f'{result.text} \n{tgt_lang.upper()} >> {result.detected_source_lang}\n残り{remain}文字'
            await ctx.respond(rst_joined_text)

        else:
            rst_split_text = result.text.split()
            part_msg_text:str
            part_msg_num = 1

            for split_text in rst_split_text:
                if len(part_msg_text) + len(split_text) >= discord_text_max_length:
                    await ctx.respond(part_msg_text)
                    part_msg_text = ""

                part_msg_text += split_text

            if len(part_msg_text) + len(result.detected_source_lang) >= discord_text_max_length:
                await ctx.respond(part_msg_text)
                part_msg_text =""

            part_msg_text = f'{part_msg_text} \n{tgt_lang.upper()} >> {result.detected_source_lang}\n残り{remain}文字'
            await ctx.respond(part_msg_text)

def setup(bot):
    bot.add_cog(Translate(bot))