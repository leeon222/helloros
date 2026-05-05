#!/usr/bin/env python3
"""数据导出脚本"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ros2_data_tool.exporter import main

if __name__ == '__main__':
    main()