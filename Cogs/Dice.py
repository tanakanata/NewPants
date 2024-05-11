import random
import discord
from discord import Option
from discord.ext import commands

class Dice(commands.Cog):
    bot: commands.bot.Bot

    def __init__(self, bot:commands.bot.Bot):
        print('Dice OK')
        self.bot = bot

    

    @commands.slash_command(description="指定数のダイスを振ります", guild_ids=[267396486088622080])
    async def dice(self, ctx: discord.ApplicationContext,
                   dice_num: Option(int, name='ダイス数'),
                   side_num: Option(int, name="面数")):
        
        result_list:list = []
        total: int = 0

        for i in range(dice_num):
            result = random.randint(1,side_num)
            result_list.append(result)
            total += result
        print(result_list)
        msg:str = "".join(str(result_list))
        msg = msg + " 合計" + str(total)

        await ctx.respond(msg)

    @commands.slash_command(name="random", guild_ids=[267396486088622080])
    async def random_cmd(self, ctx: discord.ApplicationContext,
                         num: Option(int, name="最大数")):
        msg = ctx.author.nick + "さんの結果は " + str(random.randint(1,num)) + " でした"
        await ctx.respond(msg)


        

def setup(bot):
    bot.add_cog(Dice(bot))