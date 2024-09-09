# -*- coding: utf-8 -*-
import os
import logging
from common import set_log, set_common, get_channel_videos, get_video_details, initialize_firebase, \
    update_firestore_video
from logging import config
from dotenv import load_dotenv
from googleapiclient.discovery import build

# ログ設定を適用
logging.config.dictConfig(set_log())
logger = logging.getLogger(__name__)
common_conf = set_common()

load_dotenv('.env')

if __name__ == '__main__':
    API_KEY = os.getenv('YOUTUBE_API_KEY')

    # YouTube APIクライアントを作成
    youtube = build('youtube', 'v3', developerKey=API_KEY)

    # チャンネルIDを指定
    channel_id = 'UCxBR2bnAFAavDHpHtQrTA9Q'

    # Firebase初期化
    initialize_firebase()

    # チャンネルの全動画を取得
    all_videos = get_channel_videos(channel_id, logger, youtube)

    # 取得した動画IDのリストを作成
    video_ids = [item['id']['videoId'] for item in all_videos]

    # 結果を処理
    video_details = []
    for item in all_videos:
        video_id = item['id']['videoId']
        video_detail = get_video_details(logger, youtube, video_id)

        if video_detail:
            video_details.append(video_detail)

            # 100件ごとにFirestoreに登録/更新
            if len(video_details) % 100 == 0:
                update_firestore_video(channel_id, logger, video_details[-100:])
                logger.info(f"{len(video_details)}件の動画情報を処理しました。")
        else:
            logger.warning(f"video_id: {video_id} の詳細情報を取得できませんでした。")

        # APIリクエスト上限に達した場合、処理を終了
        if video_detail is None and len(video_details) > 0:
            logger.warning("YouTube APIのリクエスト上限に達したため、処理を終了します。")
            break

    # 残りの動画情報をFirestoreに登録/更新
    if len(video_details) % 100 != 0:
        update_firestore_video(channel_id, logger, video_details[-(len(video_details) % 100):])

    logger.info(f"全{len(video_details)}件の動画情報の処理が完了しました。")
