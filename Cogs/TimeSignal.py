import discord
from discord.ext import commands
class TimeSignal(commands.Cog):
    def __init__(self,bot: commands.Bot) -> None:
        print('TimeSignal')
        self.bot = bot

    async def vc_connnect(self):
        pass

    async def vc_disconnect(self):
        pass

    @commands.command(name='start')
    async def start_loop(self,ctx: commands.Context):
        try:
            self.loop.start()
            await ctx.send('スタートしました')
        except RuntimeError:
            await ctx.send('エラー')

    @commands.command(name='stop')
    async def stop_loop(self,ctx: commands.Context):
        self.loop.stop()
        await ctx.send('ストップしました')

    async def toggle_auto_select(self):
        pass

    async def toggle_channel(self):
        pass

    async def set_channel(self):
        pass

    async def test_join(self):
        pass

    async def play_audio(self):
        pass

    def loop(self):
        pass

    def cog_unload(self):
        self.loop.cancel()
        return super().cog_unload()
def setup(bot):
    bot.add_cog(TimeSignal(bot))


