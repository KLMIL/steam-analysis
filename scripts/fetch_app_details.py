# App ID를 이용해 details 정보를 받아오는 함수

import requests     # HTTP 요청
import json         # json으로 저장
import time         # 대기
import os           # 파일 저장 / 경로 체크
from concurrent.futures import ThreadPoolExecutor, as_completed # 멀티스레드


STEAM_APP_DETAILS_URL = "https://store.steampowered.com/api/appdetails"


# Steam API에 직접 detail을 요청하는 기능
def get_app_details(appid):
    url = f"{STEAM_APP_DETAILS_URL}?appids={appid}&cc=kr&l=korean"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json",
        "Accept-Language": "en-US,en;q=0.9"
    }
    try:
        resp = requests.get(url, timeout=10, headers=headers)
        resp.raise_for_status()
        data = resp.json()
        appinfo = data.get(str(appid), {})
        if not appinfo.get('success', False):
            return None
        details = appinfo.get('data', {})
        details["appid"] = appid    # 검색 편의성을 위해 appid 추가
        return details
    except Exception as e:
        print(f"{{appid}} Error: {e}")
        return None

# 결과값을 jsonl에 저장
def save_results_jsonl(filename, results):
    with open(filename, 'a', encoding='utf-8') as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + '\n')

# 실패한 app id 저장
def save_failed_appids_jsonl(filename, failed_appids):
    with open(filename, 'a', encoding='utf-8') as f:
        for appid in failed_appids:
            f.write(json.dumps({'appid': appid}) + '\n')

# 요청 진행상황 저장
def save_progress(progress_file, idx):
    with open(progress_file, 'w') as f:
        f.write(str(idx))


# 요청 진행상황 불러오기
def load_progress(progress_file):
    try:
        with open(progress_file) as f:
            return int(f.read().strip())
    except:
        return 0
    
# 청크 단위로 get_app_details 호출
def chunked_request_multithread(
    appids, 
    chunk_size=1000, 
    sleep_sec=0.4, 
    result_file='data/results.jsonl', 
    progress_file='data/progress.txt',
    max_workers=4,
    failed_file='data/failed_appids.jsonl'
):
    start_idx = load_progress(progress_file)
    total = len(appids)
    print(f"전쳬: {total}개, {start_idx}번부터 시작, {max_workers}스레드")

    for chunk_start in range(start_idx, total, chunk_size):
        chunk_end = min(chunk_start + chunk_size, total)
        chunk = appids[chunk_start:chunk_end]
        results = []
        failed = []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_appid = {executor.submit(get_app_details, appid): appid for appid in chunk}
            for i, future in enumerate(as_completed(future_to_appid)):
                appid = future_to_appid[future]
                result = future.result()
                if result: 
                    results.append(result)
                else:
                    failed.append(appid) # 실패시 appid 기록
                time.sleep(sleep_sec) # 각 스레드마다 쉼

                if (i + 1) % 100 == 0:
                    print(f"{chunk_start+i+1}/{total} 요청 완료")

        # 청크 끝날 때마다 저장
        save_results_jsonl(result_file, results)
        save_failed_appids_jsonl(failed_file, failed)
        save_progress(progress_file, chunk_end)

        print(f"{chunk_end}/{total}까지 저장 완료 (성공 {len(results)} / 실패 {len(failed)})")

    print("!!!모든 요청 완료!!!")
