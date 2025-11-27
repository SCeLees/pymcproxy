import logging
import os
from datetime import datetime

# 创建logs目录（如果不存在）
if not os.path.exists('logs'):
    os.makedirs('logs')

# 配置日志格式
log_format = '[%(asctime)s] %(levelname)s: %(message)s'
date_format = '%Y-%m-%d %H:%M:%S'

# 设置日志文件名，使用日期作为后缀
log_filename = f"logs/minecraft_proxy_{datetime.now().strftime('%Y%m%d')}.log"

# 创建logger
logger = logging.getLogger('MinecraftProxy')
logger.setLevel(logging.DEBUG)

# 创建文件处理器
file_handler = logging.FileHandler(log_filename, encoding='utf-8')
file_handler.setLevel(logging.DEBUG)

# 创建控制台处理器
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# 创建格式化器并添加到处理器
formatter = logging.Formatter(log_format, datefmt=date_format)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# 将处理器添加到logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

def get_logger():
    """获取配置好的logger实例"""
    return logger