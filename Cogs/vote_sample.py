import asyncio
import discord
from discord.ext import commands, tasks


class Vote(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.guild_id = None
        self.channel_id = None
        self.message_id = None
        self.choices = 0
        self.vote = False
        self.emojilist = ['\U00000031\U000020E3', '\U00000032\U000020E3', '\U00000033\U000020E3', '\U00000034\U000020E3',
                          '\U00000035\U000020E3', '\U00000036\U000020E3', '\U00000037\U000020E3', '\U00000038\U000020E3', '\U00000039\U000020E3', '\U0001F51F']

    @commands.command(aliases=['vo'])
    async def vote(self, ctx, *args):
        i = 0
        text = 'Question\n'
        if self.vote == True:
            await ctx.send('他の投票が進行中でし')
            return
        if len(args) < 3:
            await ctx.send('引数たらんぞ')
            return
        elif len(args) > 11:
            await ctx.send('選択肢は10個までやぞ')
            return
        try:
            term = int(args[0])
        except:
            await ctx.send('ｼﾞｶﾝﾊﾊﾝｶｸｽｳｼﾞﾃﾞﾆｭｳﾘｮｸ')
            return

        self.Choices = len(args) - 1
        for q in args[1:]:
            text += f'{self.emojilist[i]} : {q}\n'
            i = i + 1

        self.vote = True
        await ctx.send(text)

    @commands.command(aliases=['re'])
    async def result(self, ctx):
        if self.message_id == None:
            await ctx.send('投票中じゃないよ')
            return
        text = aggregate()
        await message.channel.send(text)

    async def aggregate(self):
        channel = self.bot.get_channel(self.channel_id)
        message = await channel.fetch_message(self.message_id)
        message_content = message.content
        reactions = message.reactions
        R_count = []
        index = []

        if message_content.startswith('終了'):
            text = '開票済みよ'
            return text

        message_content = f'終了 : {message_content}'
        await message.edit(content=message_content)

        url = 'https://canary.discord.com/channels/{0}/{1}/{2}'.format(
            self.guild_id, self.channel_id, self.message_id)
        text = 'Result\n'
        for reaction in reactions:
            r = f'{reaction.emoji} : {reaction.count}'
            R_count.append(r)
            i = reaction.count
            index.append(i)

        maxIndex = [i for i, x in enumerate(index) if x == max(index)]
        for res in maxIndex:
            text += f"{R_count[res]}\n"
        text += F"{url}\n"
        return text

    @commands.Cog.listener(name='on_message')
    async def add_reaction(self, message):
        if message.content.startswith('Question') and message.author.id == self.bot.user.id:
            for i in range(self.Choices):
                await message.add_reaction(self.emojilist[i])
            self.guild_id = message.guild.id
            self.channel_id = message.channel.id
            self.message_id = message.id


def setup(bot):
    bot.add_cog(Vote(bot))
