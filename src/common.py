# -*- coding: utf-8 -*-
import json
import os
from datetime import datetime


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


def get_channel_videos(youtube, channel_id, total_results=100):
    all_videos = []
    next_page_token = None

    while len(all_videos) < total_results:
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

    return all_videos[:total_results]


def get_video_details(logger, youtube, video_id):
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
