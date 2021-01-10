import datetime
import pytz
from discord.ext import commands
# -----------------------------------------------------------------------------------------


class Logging(commands.Cog):
    def __init__(self, bot: commands.bot):
        print('Logging OK')
        self.bot = bot

    @commands.Cog.listener(name='on_voice_state_update')
    async def Voice_channel(self, member, before, after):
        if member.guild.id == 610568927768084499 and (before.channel != after.channel):  # noqa
            now = datetime.datetime.now(pytz.timezone(
                'Asia/Tokyo')).strftime('%H:%M:%S')
            channel = self.bot.get_channel(797311047262404680)
            if before.channel is None:
                msg = ':regional_indicator_c:' + \
                    now + ' に ' + member.mention + \
                    '（' + member.name + '#' + member.discriminator + '）' + \
                    ' が ' + after.channel.name + ' に接続しました。'
                await channel.send(msg)
            elif after.channel is None:
                msg = ':regional_indicator_d:' + \
                    now + ' に ' + member.mention + \
                    '（' + member.name + '#' + member.discriminator + '）' + \
                    ' が ' + before.channel.name + ' から切断しました。'
                await channel.send(msg)
            elif after.channel != before.channel:
                msg = ':regional_indicator_m:' + \
                    now + ' に ' + member.mention + \
                    '（' + member.name + '#' + member.discriminator + '）' + \
                    ' が ' + before.channel.name + \
                    ' から' + after.channel.name + 'に移動しました。'
                await channel.send(msg)

    # @commands.Cog.listener(name='on_message')
    # async def on_message(self, message: discord.Message):
    #     if message.channel.id == 230589505525121024:
    #         cc = ''
    #         cc += (message.created_at + datetime.timedelta(hours=9)
    #                ).strftime('%Y-%m-%d %H:%M:%S')
    #         cc += ': '
    #         cc += message.author.name
    #         if message.content:
    #             cc += '\n'
    #             cc += message.content

    #         att_urls = []
    #         for att in message.attachments:
    #             att_urls.append(att.url)
    #         if att_urls:
    #             cc += '\n'
    #             cc += '\n'.join(att_urls)

    #         if cc != '':
    #             channel = client.get_channel(693537608646656031)
    #             await channel.send(cc)


def setup(bot):
    bot.add_cog(Logging(bot))
