import json
import time
import pandas as pd
import os
import re

'''
The basic structure of the input json file is as follows:
-- msg
-- result
    -- small_extra
        -- count_all
        -- yys_id
        -- role_name
        -- count_win
    -- extra
        -- bl
            -- battle_time
            -- total_battle_time
            -- battle_list
            -- d_battle_list
            -- d_score
            -- role_id
            -- score
            -- yuhun_list
            -- total_damage
            -- high_damage_show
            -- d_role_name
            -- role_name
            -- server
            -- role_level
            -- battle_result
        -- count_all
        -- count_win
    -- rank
    -- server
    -- score
    -- insert_time
    -- dt
    -- role_id
    -- id
-- ret
'''

class FileParser(object):
    def __init__(self):
        self.shishen_dict = json.loads(open('files/shishen.json', 'rb').read())
        self.yuhun_dict = json.loads(open('files/yuhun.json', 'rb').read())
        self.server_dict = json.loads(open('files/server.json', 'rb').read())
        self.columns = ['server', 'ranking', 'role_name', 'score', 'd_role_name', 'd_score', 'battle_time', 'total_battle_time', 'total_damage',
                        'high_damage_show', 'battle_result', 'M0', 'M1', 'M2', 'M3', 'M4', 'M5', 'YH1', 'YH2', 'YH3', 'YH4', 'YH5', 'D0', 'D1', 'D2', 'D3', 'D4', 'D5']

    def ParseLineup(self, game):
        # Parse 6V6 Data
        self.battle_num_list = [battle['shishen_id'] for battle in game['battle_list'][1:]]
        d_battle_num_list = [battle['shishen_id'] for battle in game['d_battle_list'][1:]]
        battle_name_list = [self.shishen_dict[str(num)]['name'] for num in self.battle_num_list]
        d_battle_name_list = [self.shishen_dict[str(num)]['name'] for num in d_battle_num_list]
        return battle_name_list, d_battle_name_list

    def ParseBattle(self, game):
        # Parse Battle Data: Time & Result
        battle_time_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(game['battle_time']))
        total_battle_time = game['total_battle_time']
        result = game['battle_result']
        total_damage, high_damage_show = game['total_damage'], game['high_damage_show']
        return [battle_time_str, total_battle_time, total_damage, high_damage_show, result]

    def ParseRole(self, game):
        # Parse Role Information Data
        role_name, score = game['role_name'], game['score']
        d_role_name, d_score = game['d_role_name'], game['d_score']
        return [role_name, score, d_role_name, d_score]

    def ParseYuhun(self, game):
        # Parse Yuhun Data
        result = {}
        for shishen_yuhun in game['yuhun_list'][2:]:
            shishen_num, yuhun_dict = shishen_yuhun
            for yuhun_num, position in yuhun_dict.items():
                if len(position) >= 4:
                    result[shishen_num] = yuhun_num
                    break
        yuhun_list = []
        for num in self.battle_num_list[1:]:
            if num in result.keys():
                yuhun_list.append(self.yuhun_dict[result[num]]['name'])
            else:
                yuhun_list.append('散件')
        return yuhun_list

    def ParseUser(self, file_path, saved_path=None):
        if file_path.endswith('.json'):
            file_list = [file_path]
        else:
            file_list = [os.path.join(file_path, file_name) for file_name in os.listdir(file_path)]
        server_result = []
        for file_name in file_list:
            file_dict = json.loads(open(file_name, 'rb').read())
            small_extra = file_dict['result']['small_extra']
            game_list = file_dict['result']['extra']['bl']
            server, rank = file_dict['result']['server'], file_dict['result']['rank']
            assert small_extra['count_all'] == len(game_list)

            for game in game_list:
                try:
                    battle_list, d_battle_list = self.ParseLineup(game)
                    if len(battle_list) == 0:
                        continue
                    battle_information = self.ParseBattle(game)
                    role_information = self.ParseRole(game)
                    yuhun_list = self.ParseYuhun(game)
                    game_result = [self.server_dict[server]['name'], rank] + role_information + battle_information + battle_list + yuhun_list + d_battle_list
                    server_result.append(game_result)
                except KeyError as KE:
                    print('Key Not Found in Shishen Dictionary: ', KE)
                except TypeError as TE:
                    print('Type Error Occurs: ', TE)

        if saved_path is not None and len(server_result):
            server_df = pd.DataFrame(server_result, columns=self.columns)
            server_df.to_excel(saved_path)

        return len(server_result)

    def ParseServer(self, file_dict):
        return [result['role_id'] for result in file_dict['result']]


class Log(object):
    def __init__(self, file_path):
        if not os.path.exists(file_path):
            os.mkdir(file_path)
        self.log_path = os.path.join(file_path, 'log.txt')
        with open(self.log_path, 'a+') as f:
            f.seek(0)
            self.start_from = len(f.readlines())

    def WriteLog(self, log_info):
        print(log_info)
        with open(self.log_path, 'a') as f:
            f.write(log_info)


def url2content(wd, url, start_position=0, end_position=-1, save_address=None):
    wd.get(url)
    content = wd.page_source
    try:
        content = eval(content[start_position: end_position])
    except:
        content = re.compile(' null,').sub(' None,', content)
        # content = eval(content[25: -14])
        content = eval(content[start_position: end_position])
    if save_address is not None:
        with open(save_address, 'w') as f:
            json.dump(content, f)
    return content