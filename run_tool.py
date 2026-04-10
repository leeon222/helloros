#!/usr/bin/env python33
"""ROS2自动化数据采集与处理工具 - 一键运行脚本"""

import os
import sys
import argparse
import subprocess
import time
import yaml

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# 导入日志模块
from src.ros2_data_tool.logger import get_logger

logger = get_logger("run_tool")


def load_config(config_file):
    """加载YAML配置文件"""
    if not os.path.exists(config_file):
        logger.warning(f"Configuration file {config_file} not found")
        return {}
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        return config or {}
    except yaml.YAMLError as e:
        logger.error(f"Failed to load configuration file: {e}")
        return {}


def run_command(command, cwd=None):
    """运行命令并返回结果"""
    logger.info(f"Running command: {command}")
    try:
        result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            logger.error(f"Command failed with exit code {result.returncode}: {result.stderr}")
            return False
        if result.stdout:
            logger.info(f"Command output: {result.stdout}")
        return True
    except Exception as e:
        logger.error(f"Exception occurred while running command: {e}", exc_info=True)
        return False


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='ROS2自动化数据采集与处理工具')
    
    # 配置文件参数
    parser.add_argument('--config', type=str,
                        help='配置文件路径')
    
    parser.add_argument('--mode', type=str, default='all',
                        choices=['collect', 'process', 'visualize', 'export', 'all'],
                        help='运行模式')
    
    # 数据采集参数
    parser.add_argument('--topics', type=str, nargs='+', default=['/scan', '/odom', '/imu/data'],
                        help='要采集的话题列表')
    parser.add_argument('--duration', type=float, default=30.0,
                        help='采集时长（秒）')
    
    # 通用参数
    parser.add_argument('--output', type=str, default='./data',
                        help='数据保存路径')
    
    # 预处理参数
    parser.add_argument('--sync', action='store_true',
                        help='是否进行时间同步')
    parser.add_argument('--frequency', type=float,
                        help='目标频率')
    
    # 导出参数
    parser.add_argument('--format', type=str, choices=['csv', 'json', 'kitti', 'tum'], default='csv',
                        help='导出格式')
    
    args = parser.parse_args()
    
    # 加载配置文件（如果指定）
    config = {}
    if args.config:
        config = load_config(args.config)
        logger.info(f"Loaded configuration from: {args.config}")
    
    # 应用配置文件设置（命令行参数优先）
    if 'mode' in config and args.mode == parser.get_default('mode'):
        args.mode = config['mode']
    
    if 'topics' in config and args.topics == parser.get_default('topics'):
        args.topics = config['topics']
    
    if 'duration' in config and args.duration == parser.get_default('duration'):
        args.duration = config['duration']
    
    if 'output' in config and args.output == parser.get_default('output'):
        args.output = config['output']
    
    if 'sync' in config:
        args.sync = config['sync']
    
    if 'frequency' in config and args.frequency is None:
        args.frequency = config['frequency']
    
    if 'format' in config and args.format == parser.get_default('format'):
        args.format = config['format']
    
    # 获取脚本目录
    script_dir = os.path.join(os.path.dirname(__file__), 'scripts')
    
    if args.mode == 'collect':
        cmd = f"python3 {os.path.join(script_dir, 'collector.py')}"
        cmd += f" --topics {' '.join(args.topics)}"
        cmd += f" --output {args.output}"
        if args.duration:
            cmd += f" --duration {args.duration}"
        
        run_command(cmd)
    
    elif args.mode == 'process':
        cmd = f"python3 {os.path.join(script_dir, 'processor.py')}"
        cmd += f" --input {args.output}"
        cmd += f" --output {os.path.join(os.path.dirname(args.output), 'processed')}"
        if args.sync:
            cmd += " --sync"
        if args.frequency:
            cmd += f" --frequency {args.frequency}"
        
        run_command(cmd)
    
    elif args.mode == 'visualize':
        processed_dir = os.path.join(os.path.dirname(args.output), 'processed')
        cmd = f"python3 {os.path.join(script_dir, 'visualizer.py')}"
        cmd += f" --input {processed_dir}"
        cmd += f" --output {os.path.join(os.path.dirname(args.output), 'visualizations')}"
        
        run_command(cmd)
    
    elif args.mode == 'export':
        processed_dir = os.path.join(os.path.dirname(args.output), 'processed')
        cmd = f"python3 {os.path.join(script_dir, 'exporter.py')}"
        cmd += f" --input {processed_dir}"
        cmd += f" --output {os.path.join(os.path.dirname(args.output), 'exports')}"
        cmd += f" --format {args.format}"
        
        run_command(cmd)
    
    elif args.mode == 'all':
        # 数据采集
        logger.info("\n=== Step 1: Data Collection ===")
        cmd = f"python3 {os.path.join(script_dir, 'collector.py')}"
        cmd += f" --topics {' '.join(args.topics)}"
        cmd += f" --output {args.output}"
        if args.duration:
            cmd += f" --duration {args.duration}"
        
        if not run_command(cmd):
            logger.error("Data collection failed")
            return
        
        # 数据预处理
        logger.info("\n=== Step 2: Data Processing ===")
        processed_dir = os.path.join(os.path.dirname(args.output), 'processed')
        cmd = f"python3 {os.path.join(script_dir, 'processor.py')}"
        cmd += f" --input {args.output}"
        cmd += f" --output {processed_dir}"
        if args.sync:
            cmd += " --sync"
        if args.frequency:
            cmd += f" --frequency {args.frequency}"
        
        if not run_command(cmd):
            logger.error("Data processing failed")
            return
        
        # 数据可视化
        logger.info("\n=== Step 3: Data Visualization ===")
        visualizations_dir = os.path.join(os.path.dirname(args.output), 'visualizations')
        cmd = f"python3 {os.path.join(script_dir, 'visualizer.py')}"
        cmd += f" --input {processed_dir}"
        cmd += f" --output {visualizations_dir}"
        
        if not run_command(cmd):
            logger.error("Data visualization failed")
            return
        
        # 数据导出
        logger.info("\n=== Step 4: Data Export ===")
        exports_dir = os.path.join(os.path.dirname(args.output), 'exports')
        export_format = args.format if args.format else 'csv'
        cmd = f"python3 {os.path.join(script_dir, 'exporter.py')}"
        cmd += f" --input {processed_dir}"
        cmd += f" --output {exports_dir}"
        cmd += f" --format {export_format}"
        
        if run_command(cmd):
            logger.info("\n=== All steps completed successfully! ===")
        else:
            logger.error("Data export failed")


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        logger.warning("Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        logger.critical(f"Unexpected error occurred: {e}", exc_info=True)
        sys.exit(1)