# -*- coding: utf-8 -*-

import logging.config
import yaml

logging_config_file = './conf/logging_config.yaml'

# 设置日志
with open(logging_config_file, 'r') as f:
    config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)
logger = logging.getLogger(__name__)
