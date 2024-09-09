# -*- coding: utf-8 -*-
from common import set_log, set_common
from logging import getLogger, config


log_conf = set_log()
config.dictConfig(log_conf)
logger = getLogger(__name__)

common_conf = set_common()

if __name__ == '__main__':
    logger.info(common_conf['AAA'])
