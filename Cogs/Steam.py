import requests
import json
import re
import config
from discord.ext import commands
import xml.etree.ElementTree as ET


class Steam(commands.Cog):
    def __init__(self, bot: commands.bot):
        print(__name__)
        self.bot = bot
        self.apikey = config.steam

    def get_games(self, userid):
        game_list = []
        play_time = []
        playtime_list = []
        count = 0

        # URLにAPI_keyとUserIDを入れてURLを作成
        URL = f'http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={self.apikey}&steamid={userid}&format=json&include_appinfo=true'  # noqa

        result = requests.get(URL)

        # status_codeを代入
        status_code = result.status_code

        if not 200 <= status_code <= 299:
            return status_code
        # リクエストの結果をjsonに格納
        json_date = json.loads(result.text)
        # プロフィールが非公開かどうかを判定
        response = json_date["response"]
        if len(response) == 0:
            status_code = 403
            print('403')
            return status_code
        # ゲームを所持しているかを判定
        game_count = response["game_count"]
        if game_count == 0:
            status_code = 404
            print('404')
            return status_code

        json_date = response["games"]
        # ゲーム一覧からゲーム名とプレイ時間を取得
        for game in json_date:
            game_list.append(game["name"])
            time = divmod(game["playtime_forever"], 60)
            txt = f'{time[0]}時間{time[1]}分'
            play_time.append(txt)

        # 取得したゲーム名とプレイ時間をペアにしてリストに格納
        for f1 in range(len(game_list)):
            text = f'{game_list[count]} : {play_time[count]}'
            playtime_list.append(text)
            count += 1

        return status_code, game_count, game_list, playtime_list

    @commands.command()
    async def get_game(self, ctx, username):
        if re.match(r'^[0-9]+$', username):
            steamID = username

        elif re.match(r'^[0-9a-zA-Z_]+$', username):
            URL = f'https://steamcommunity.com/id/{username}/?xml=1'
            # URLを使用しXMLを取得
            response = requests.get(URL)

            # XMLからsteamIDを取得
            root = ET.fromstring(response.text)
            for u_id in root.iter('steamID64'):
                steamID = u_id.text
        else:
            await ctx.send('usernameがおかしいよ')
            return

        r = self.get_games(steamID)

        if type(r) == int:
            status_code = r
        else:
            status_code = r[0]
            game_count = r[1]
            playtime_list = r[3]

        if 200 <= status_code <= 299:
            resultJoined = '\n'.join(playtime_list)
            discordTextMaxLength = 1950
            if len(resultJoined) <= discordTextMaxLength:
                # 2000以下
                await ctx.send(f'```Total : {game_count}\n{resultJoined}```')
            else:
                partMessageBody = f'Total : {game_count}\n'
                partMessageNum = 1

                for line in playtime_list:
                    if len(partMessageBody) + len(line) >= discordTextMaxLength:  # noqa
                        await ctx.send(f'```{partMessageBody}```')
                        partMessageBody = ""
                        partMessageNum += 1
                    partMessageBody += line + '\n'

                await ctx.send(f'```{partMessageBody}```')

        elif status_code == 403:
            await ctx.send('プロフィールが非公開みたい')

        elif status_code == 404:
            await ctx.send('ゲームを所持してないよ')

        else:
            await ctx.send(f'何かがおかしいよ? ErrorCode {status_code}')


def setup(bot):
    bot.add_cog(Steam(bot))
