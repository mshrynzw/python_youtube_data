# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from googleapiclient.errors import HttpError


def set_common():
    with open('./conf/common.json', 'r') as f:
        common_conf = json.load(f)

    return common_conf


def set_log():
    if not os.path.isdir('./log/'):
        os.mkdir('./log/')

    with open('./conf/log.json', 'r') as f:
        log_conf = json.load(f)
    log_conf["handlers"]["fileHandler"]["filename"] = './log/{}.log'.format(datetime.utcnow().strftime("%Y%m%d%H%M%S"))

    return log_conf


def get_channel_videos(channel_id, logger, youtube):
    all_videos = []
    next_page_token = None

    try:
        while True:
            search_response = youtube.search().list(
                channelId=channel_id,
                type='video',
                part='id,snippet',
                order='date',
                maxResults=50,
                pageToken=next_page_token
            ).execute()

            all_videos.extend(search_response['items'])

            next_page_token = search_response.get('nextPageToken')

            if not next_page_token:
                break

            logger.info(f"{len(all_videos)}件の動画情報を取得しました。")

    except HttpError as e:
        if e.resp.status in [403, 429]:
            logger.warning("YouTube APIのリクエスト上限に達しました。処理を終了します。")
        else:
            logger.error(f"YouTube APIリクエスト中にエラーが発生しました: {e}")
    except Exception as e:
        logger.error(f"予期せぬエラーが発生しました: {e}")

    logger.info(f"合計{len(all_videos)}件の動画情報を取得しました。")
    return all_videos


def get_video_details(logger, youtube, video_id):
    try:
        video_response = youtube.videos().list(
            part='snippet,statistics',
            id=video_id
        ).execute()

        video_info = video_response['items'][0]
        title = video_info['snippet']['title']
        published_at = datetime.strptime(video_info['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
        view_count = int(video_info['statistics'].get('viewCount', 0))
        comment_count = int(video_info['statistics'].get('commentCount', 0))
        like_count = int(video_info['statistics'].get('likeCount', 0))

        logger.info(f'id: {video_id}')
        logger.info(f'title: {title}')
        logger.info(f'published: {published_at.strftime("%Y-%m-%d %H:%M:%S")}')
        logger.info(f'views: {view_count}')
        logger.info(f'comments: {comment_count}')
        logger.info(f'likes: {like_count}')
        logger.info('---')

        return {
            'id': video_id,
            'title': title,
            'published_at': published_at,
            'view_count': view_count,
            'comment_count': comment_count,
            'like_count': like_count
        }

    except HttpError as e:
        if e.resp.status in [403, 429]:
            logger.warning(f"YouTube APIのリクエスト上限に達しました。video_id: {video_id} の処理をスキップします。")
        else:
            logger.error(f"YouTube APIリクエスト中にエラーが発生しました: {e}")
        return None
    except Exception as e:
        logger.error(f"予期せぬエラーが発生しました: {e}")
        return None


# Firebase初期化（アプリケーションの開始時に一度だけ実行）
def initialize_firebase():
    cred = credentials.Certificate("./conf/service_account_key/data-9e315-firebase-adminsdk-z5m2g-d14bae6ebc.json")
    firebase_admin.initialize_app(cred)


# Firestoreにデータを登録または更新する関数
def update_firestore_video(channel_id, logger, video_details):
    db = firestore.client()
    channel_ref = db.collection('channels').document(channel_id)

    # バッチ処理を使用して複数の更新を効率的に行う
    batch = db.batch()

    for video in video_details:
        video_ref = channel_ref.collection('videos').document(video['id'])

        # DatetimeオブジェクトをFirestoreのTimestampに変換
        video_data = {
            'title': video['title'],
            'published_at': video['published_at'],
            'view_count': video['view_count'],
            'comment_count': video['comment_count'],
            'like_count': video['like_count']
        }

        batch.set(video_ref, video_data, merge=True)

    # バッチ処理を実行
    try:
        batch.commit()
        logger.info(f"{len(video_details)}件のビデオ情報をFirestoreに登録/更新しました。")
    except Exception as e:
        logger.error(f"Firestoreの更新中にエラーが発生しました: {e}")