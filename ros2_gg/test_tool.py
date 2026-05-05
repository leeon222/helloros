#!/usr/bin/env python3
"""ROS2自动化数据采集与处理工具 - 测试脚本"""

import os
import sys
import json
import pickle
import tempfile
import shutil
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 只导入不需要ROS的模块
from src.ros2_data_tool.processor import DataProcessor
from src.ros2_data_tool.visualizer import DataVisualizer
from src.ros2_data_tool.exporter import DataExporter


def test_processor():
    """测试数据预处理模块"""
    print("=== Testing DataProcessor ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建输入和输出目录
        input_dir = os.path.join(temp_dir, 'input')
        output_dir = os.path.join(temp_dir, 'output')
        os.makedirs(input_dir)
        
        # 创建模拟数据
        mock_data = [
            {
                'timestamp': 1600000000.0,
                'message': {
                    'pose': {
                        'pose': {
                            'position': {'x': 0.0, 'y': 0.0, 'z': 0.0},
                            'orientation': {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0}
                        }
                    }
                }
            },
            {
                'timestamp': 1600000001.0,
                'message': {
                    'pose': {
                        'pose': {
                            'position': {'x': 1.0, 'y': 1.0, 'z': 0.0},
                            'orientation': {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0}
                        }
                    }
                }
            }
        ]
        
        # 保存模拟数据
        topic_name = 'odom'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        data_path = os.path.join(input_dir, f'{topic_name}_{timestamp}.pkl')
        
        with open(data_path, 'wb') as f:
            pickle.dump(mock_data, f)
        
        # 创建处理器并运行
        processor = DataProcessor(input_dir=input_dir, output_dir=output_dir)
        processor.load_data()
        processor.process()
        processor.save_processed_data()
        
        print(f"Processed data saved to: {output_dir}")
        print("Processor test: PASSED")


def test_exporter():
    """测试数据导出模块"""
    print("\n=== Testing DataExporter ===")
    
    with tempfile.TemporaryDirectory() as temp_dir:
        # 创建输入和输出目录
        input_dir = os.path.join(temp_dir, 'input')
        output_dir = os.path.join(temp_dir, 'output')
        os.makedirs(input_dir)
        
        # 创建模拟数据
        mock_data = [
            {
                'timestamp': 1600000000.0,
                'message': {
                    'pose': {
                        'pose': {
                            'position': {'x': 0.0, 'y': 0.0, 'z': 0.0},
                            'orientation': {'x': 0.0, 'y': 0.0, 'z': 0.0, 'w': 1.0}
                        }
                    }
                }
            }
        ]
        
        # 保存模拟数据
        topic_name = 'odom'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        data_path = os.path.join(input_dir, f'{topic_name}_{timestamp}.pkl')
        
        with open(data_path, 'wb') as f:
            pickle.dump(mock_data, f)
        
        # 测试CSV导出
        exporter = DataExporter(input_dir=input_dir, output_dir=output_dir)
        exporter.load_data()
        exporter.export('csv')
        
        # 测试JSON导出
        exporter.export('json')
        
        print(f"Exported data saved to: {output_dir}")
        print("Exporter test: PASSED")


def main():
    """运行所有测试"""
    print("Running ROS2 Data Tool tests...\n")
    
    try:
        test_processor()
        test_exporter()
        
        print("\n=== All tests passed! ===")
        return 0
        
    except Exception as e:
        print(f"\n=== Test failed: {e} ===")
        return 1


if __name__ == '__main__':
    sys.exit(main())