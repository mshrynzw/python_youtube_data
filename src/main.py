# -*- coding: utf-8 -*-
import os
from common import set_log, set_common
from logging import getLogger, config
from dotenv import load_dotenv


log_conf = set_log()
config.dictConfig(log_conf)
logger = getLogger(__name__)

common_conf = set_common()

load_dotenv('.env')


if __name__ == '__main__':
    logger.info(common_conf['AAA'])
    API_KEY = os.getenv('YOUTUBE_API_KEY')
    logger.info(API_KEY)