# Steam의 전체 AppID 리스트 가져옴

import requests
import json
import os

STEAM_APP_LIST_URL = "https://api.steampowered.com/ISteamApps/GetAppList/v2/"
DATA_DIR = "data"
APP_LIST_FILENAME = "applist.json"
APP_LIST_PATH = os.path.join(DATA_DIR, APP_LIST_FILENAME)

def fetch_app_list():
    # Steam API에서 AppID 목록 받아서 data 폴더에 저장
    resp = requests.get(STEAM_APP_LIST_URL)
    resp.raise_for_status()
    apps = resp.json()['applist']['apps']

    # 저장 디렉토리
    os.makedirs(DATA_DIR, exist_ok=True)

    # 파일 저장
    with open(APP_LIST_PATH, "w", encoding="utf-8") as f:
        json.dump(apps, f, ensure_ascii=False, indent=2)
    print(f"앱 리스트 {len(apps)}개 저장 완료 ({APP_LIST_PATH})")
