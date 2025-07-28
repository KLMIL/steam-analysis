# Main 함수

import json

from scripts.fetch_app_list import fetch_app_list
from scripts.fetch_app_details import chunked_request_multithread


def main():
    # 앱 리스트 요청 API 호출
    # fetch_app_list()

    # 테스트용 API 호출
    # test_appids = [570, 730, 440]
    # chunked_request_multithread(
    #     appids=test_appids,
    #     chunk_size=3,  # 여기선 3개밖에 없으니 굳이 청크 나눌 필요 없음
    #     sleep_sec=1,
    #     result_file='data/test_results.jsonl',  # 별도 결과 파일로 저장
    #     progress_file='data/test_progress.txt',  # 별도 진행 파일
    #     max_workers=1  # 쓰레드는 1개로, 안정성 확보
    # )
    
    # # 받아온 앱 리스트 오픈
    with open('data/applist.json', encoding='utf-8') as f:
        apps = json.load(f)
        appids = [app['appid'] for app in apps if 'appid' in app]

    # 앱 디테일 요청 API 호출
    chunked_request_multithread(
         appids=appids,
         chunk_size=10,
         sleep_sec=0.3,
         result_file='data/results.jsonl',
         progress_file='data/progress.txt',
         max_workers=1
    )


if __name__ == "__main__":
	main()
