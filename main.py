import os.path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from utils import FileParser, Log, url2content
from tqdm import tqdm
import argparse
import warnings

parser = argparse.ArgumentParser()
parser.add_argument('--raw_url', type=str, default='https://ds.163.com/2019/yys/dj-rank/server.html')
parser.add_argument('--server_url', type=str, default='https://s.166.net/config/bbs_yys/server.json')
parser.add_argument('--shishen_url', type=str, default='https://s.166.net/config/bbs_yys/shishen.json')
parser.add_argument('--yuhun_url', type=str, default='https://s.166.net/config/bbs_yys/yuhun.json')
parser.add_argument('--path_of_config', type=str, default='./config/crawler_config.yaml')
parser.add_argument('--path_of_chrome', type=str, default=r'C:\Users\42436\Downloads\chrome-win64\chrome-win64\chrome.exe')
parser.add_argument('--path_of_chrome_driver', type=str, default=r'C:\Users\42436\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe')
parser.add_argument('--uid', type=str, default='199e4c4d27b84b7097fec77a22b2a68a')
# Modify the Following
parser.add_argument('--saved_path', type=str, default=r'C:\Users\42436\Desktop\project\yys_crawler\20241201')
parser.add_argument('--timestamp', type=str, default='1733102546739')
parser.add_argument('--token', type=str, default='ACB2678BDE5139893C97894457D2FAB9')

# Load Configuration
args = parser.parse_known_args()[0]
warnings.filterwarnings('ignore')

if __name__ == '__main__':
    # Load WebDriver
    options = webdriver.ChromeOptions()
    options.add_argument('ignore-certificate-errors')
    options.binary_location = args.path_of_chrome
    options.add_experimental_option('detach', True)
    wd = webdriver.Chrome(service=Service(args.path_of_chrome_driver),
                          chrome_options=options)
    # Load Utils: FileParser and LogManager
    parser = FileParser()
    log = Log(args.saved_path)

    # Update Config Files
    url2content(wd, args.server_url, 99, -64, 'files/server.json')
    # url2content(wd, args.shishen_url, 99, -64, 'files/shishen.json')
    # url2content(wd, args.yuhun_url, 99, -64, 'files/yuhun.json')

    server_list = sorted(parser.server_dict.keys())
    for server_id in server_list[log.start_from:]:
        server_name = parser.server_dict[server_id]['name']
        saved_path = os.path.join(args.saved_path, server_id)
        if not os.path.exists(saved_path):
            os.mkdir(saved_path)
        for page in tqdm(range(1, 11)):
            server_url = f'https://a19-v3-bigdata.gameyw.netease.com/a19-bigdata/ky59/v1/g37_charts/topuids?server={server_id}&page={page}&uid={args.uid}&timestamp={args.timestamp}&token={args.token}'
            role_list = parser.ParseServer(url2content(wd, server_url, 25, -14))
            for rank, role_id in enumerate(role_list):
                user_url = f'https://a19-v3-bigdata.gameyw.netease.com/a19-bigdata/ky59/v1/g37_charts/oneuid?server={server_id}&roleid={role_id}&uid={args.uid}&timestamp={args.timestamp}&token={args.token}'
                url2content(wd, user_url, 25, -14, os.path.join(saved_path, f'{server_id}_{(page - 1) * 10 + rank + 1}.json'))
        number = parser.ParseUser(saved_path, os.path.join(args.saved_path, f'{server_id}_{server_name}.xls'))
        # Write Log
        log.WriteLog(f'{server_id} {server_name} {number}\n')
