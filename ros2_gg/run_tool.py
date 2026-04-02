#!/usr/bin/env python3
"""ROS2自动化数据采集与处理工具 - 一键运行脚本"""

import os
import sys
import argparse
import subprocess
import time


def run_command(command, cwd=None):
    """运行命令并返回结果"""
    print(f"Running: {command}")
    result = subprocess.run(command, shell=True, cwd=cwd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error: {result.stderr}")
        return False
    print(f"Output: {result.stdout}")
    return True


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='ROS2自动化数据采集与处理工具')
    
    parser.add_argument('--mode', type=str, required=True,
                        choices=['collect', 'process', 'visualize', 'export', 'all'],
                        help='运行模式')
    
    # 数据采集参数
    parser.add_argument('--topics', type=str, nargs='+',
                        help='要采集的话题列表')
    parser.add_argument('--duration', type=float,
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
    parser.add_argument('--format', type=str, choices=['csv', 'json', 'kitti', 'tum'],
                        help='导出格式')
    
    args = parser.parse_args()
    
    # 获取脚本目录
    script_dir = os.path.join(os.path.dirname(__file__), 'scripts')
    
    if args.mode == 'collect':
        if not args.topics:
            print("Error: --topics is required for collect mode")
            return
        
        cmd = f"python {os.path.join(script_dir, 'collector.py')}"
        cmd += f" --topics {' '.join(args.topics)}"
        cmd += f" --output {args.output}"
        if args.duration:
            cmd += f" --duration {args.duration}"
        
        run_command(cmd)
    
    elif args.mode == 'process':
        cmd = f"python {os.path.join(script_dir, 'processor.py')}"
        cmd += f" --input {args.output}"
        cmd += f" --output {os.path.join(os.path.dirname(args.output), 'processed')}"
        if args.sync:
            cmd += " --sync"
        if args.frequency:
            cmd += f" --frequency {args.frequency}"
        
        run_command(cmd)
    
    elif args.mode == 'visualize':
        processed_dir = os.path.join(os.path.dirname(args.output), 'processed')
        cmd = f"python {os.path.join(script_dir, 'visualizer.py')}"
        cmd += f" --input {processed_dir}"
        cmd += f" --output {os.path.join(os.path.dirname(args.output), 'visualizations')}"
        
        run_command(cmd)
    
    elif args.mode == 'export':
        if not args.format:
            print("Error: --format is required for export mode")
            return
        
        processed_dir = os.path.join(os.path.dirname(args.output), 'processed')
        cmd = f"python {os.path.join(script_dir, 'exporter.py')}"
        cmd += f" --input {processed_dir}"
        cmd += f" --output {os.path.join(os.path.dirname(args.output), 'exports')}"
        cmd += f" --format {args.format}"
        
        run_command(cmd)
    
    elif args.mode == 'all':
        if not args.topics:
            print("Error: --topics is required for all mode")
            return
        
        # 数据采集
        print("\n=== Step 1: Data Collection ===")
        cmd = f"python {os.path.join(script_dir, 'collector.py')}"
        cmd += f" --topics {' '.join(args.topics)}"
        cmd += f" --output {args.output}"
        if args.duration:
            cmd += f" --duration {args.duration}"
        
        if not run_command(cmd):
            return
        
        # 数据预处理
        print("\n=== Step 2: Data Processing ===")
        processed_dir = os.path.join(os.path.dirname(args.output), 'processed')
        cmd = f"python {os.path.join(script_dir, 'processor.py')}"
        cmd += f" --input {args.output}"
        cmd += f" --output {processed_dir}"
        if args.sync:
            cmd += " --sync"
        if args.frequency:
            cmd += f" --frequency {args.frequency}"
        
        if not run_command(cmd):
            return
        
        # 数据可视化
        print("\n=== Step 3: Data Visualization ===")
        visualizations_dir = os.path.join(os.path.dirname(args.output), 'visualizations')
        cmd = f"python {os.path.join(script_dir, 'visualizer.py')}"
        cmd += f" --input {processed_dir}"
        cmd += f" --output {visualizations_dir}"
        
        if not run_command(cmd):
            return
        
        # 数据导出
        print("\n=== Step 4: Data Export ===")
        exports_dir = os.path.join(os.path.dirname(args.output), 'exports')
        export_format = args.format if args.format else 'csv'
        cmd = f"python {os.path.join(script_dir, 'exporter.py')}"
        cmd += f" --input {processed_dir}"
        cmd += f" --output {exports_dir}"
        cmd += f" --format {export_format}"
        
        run_command(cmd)
        
        print("\n=== All steps completed successfully! ===")


if __name__ == '__main__':
    main()