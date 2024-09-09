# -*- coding: utf-8 -*-
import os
import logging
from common import set_log, set_common, get_channel_videos, get_video_details
from logging import getLogger, config
from dotenv import load_dotenv
from googleapiclient.discovery import build

# ログ設定を適用
logging.config.dictConfig(set_log())

# メインのロガーを取得
logger = logging.getLogger(__name__)

common_conf = set_common()

load_dotenv('.env')


if __name__ == '__main__':
    API_KEY = os.getenv('YOUTUBE_API_KEY')

    # YouTube APIクライアントを作成
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    # チャンネルIDを指定
    channel_id = 'UCxBR2bnAFAavDHpHtQrTA9Q'
    
    # 取得したい総数
    total_results = 100

    # チャンネルの動画を取得
    all_videos = get_channel_videos(youtube, channel_id, total_results)

    # 結果を処理
    video_details = []
    for item in all_videos:
        video_id = item['id']['videoId']
        video_detail = get_video_details(logger, youtube, video_id)
        video_details.append(video_detail)
