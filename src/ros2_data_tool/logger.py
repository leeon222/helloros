"""日志模块 - 提供分级日志系统"""

import logging
import sys
from typing import Optional


class Logger:
    """日志类 - 提供INFO、WARNING、ERROR级别的日志功能"""
    
    def __init__(self, name: str = "ros2_data_tool", level: int = logging.INFO):
        """初始化日志器"""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        # 清除已有的处理器
        self.logger.handlers.clear()
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        
        # 设置日志格式
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(console_handler)
    
    def info(self, message: str, **kwargs):
        """记录INFO级别的日志"""
        self.logger.info(message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        """记录WARNING级别的日志"""
        self.logger.warning(message, **kwargs)
    
    def error(self, message: str, exc_info: bool = False, **kwargs):
        """记录ERROR级别的日志"""
        self.logger.error(message, exc_info=exc_info, **kwargs)
    
    def critical(self, message: str, exc_info: bool = True, **kwargs):
        """记录CRITICAL级别的日志"""
        self.logger.critical(message, exc_info=exc_info, **kwargs)


# 创建全局日志实例
logger = Logger()


def get_logger(name: Optional[str] = None) -> Logger:
    """获取日志器实例"""
    if name:
        return Logger(name)
    return logger