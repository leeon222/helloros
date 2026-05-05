"""数据导出模块

支持多种格式导出，包括KITTI、TUM等SLAM常用格式。
"""

import os
import json
import pickle
import csv
import numpy as np
import pandas as pd
from typing import Dict, List, Any
from datetime import datetime


class DataExporter:
    """数据导出器"""
    
    def __init__(self, input_dir: str, output_dir: str):
        self._input_dir = input_dir
        self._output_dir = output_dir
        self._data = {}
        self._metadata = {}
        
        os.makedirs(output_dir, exist_ok=True)
    
    def load_data(self):
        """加载处理后的数据"""
        # 查找所有数据文件
        data_files = []
        metadata_file = None
        
        for file in os.listdir(self._input_dir):
            if file.endswith('.pkl'):
                data_files.append(file)
            elif file.endswith('.json') and 'metadata' in file:
                metadata_file = file
        
        if not data_files:
            raise ValueError(f"No data files found in {self._input_dir}")
        
        # 加载元数据
        if metadata_file:
            with open(os.path.join(self._input_dir, metadata_file), 'r') as f:
                self._metadata = json.load(f)
        
        # 加载数据文件
        for file in data_files:
            file_path = os.path.join(self._input_dir, file)
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            
            # 从文件名提取话题名
            topic_name = file.split('_')[0]
            self._data[topic_name] = data
        
        print(f"Loaded data for {len(self._data)} topics")
    
    def export(self, export_format: str):
        """导出数据"""
        export_format = export_format.lower()
        
        if export_format == 'csv':
            self._export_csv()
        elif export_format == 'json':
            self._export_json()
        elif export_format == 'kitti':
            self._export_kitti()
        elif export_format == 'tum':
            self._export_tum()
        else:
            raise ValueError(f"Unsupported export format: {export_format}")
    
    def _export_csv(self):
        """导出为CSV格式"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for topic, data in self._data.items():
            if not data:
                continue
            
            # 转换为DataFrame
            df = self._convert_to_dataframe(data)
            
            # 保存CSV文件
            csv_path = os.path.join(
                self._output_dir, 
                f'{topic}_export_{timestamp}.csv'
            )
            df.to_csv(csv_path, index=False)
            
            print(f"Exported {topic} to CSV: {csv_path}")
    
    def _export_json(self):
        """导出为JSON格式"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        for topic, data in self._data.items():
            if not data:
                continue
            
            # 保存JSON文件
            json_path = os.path.join(
                self._output_dir, 
                f'{topic}_export_{timestamp}.json'
            )
            
            # 转换数据格式以便JSON序列化
            export_data = []
            for item in data:
                export_item = {
                    'timestamp': item['timestamp'],
                    'message': self._sanitize_json(item['message'])
                }
                export_data.append(export_item)
            
            with open(json_path, 'w') as f:
                json.dump(export_data, f, indent=2)
            
            print(f"Exported {topic} to JSON: {json_path}")
    
    def _export_kitti(self):
        """导出为KITTI数据集格式"""
        # 创建KITTI格式目录结构
        kitti_dir = os.path.join(self._output_dir, 'kitti_format')
        poses_dir = os.path.join(kitti_dir, 'poses')
        os.makedirs(poses_dir, exist_ok=True)
        
        # 查找里程计数据
        odom_topic = None
        for topic in self._data.keys():
            if 'odom' in topic.lower():
                odom_topic = topic
                break
        
        if not odom_topic:
            print("No odometry data found for KITTI export")
            return
        
        data = self._data[odom_topic]
        
        # 创建poses文件
        poses_path = os.path.join(poses_dir, '00.txt')
        
        with open(poses_path, 'w') as f:
            for item in data:
                msg = item['message']
                
                if 'pose' in msg and 'pose' in msg['pose']:
                    pose = msg['pose']['pose']
                    
                    # 提取位姿数据
                    position = pose.get('position', {})
                    orientation = pose.get('orientation', {})
                    
                    # 创建4x4变换矩阵
                    transform_matrix = self._create_transform_matrix(
                        position.get('x', 0),
                        position.get('y', 0),
                        position.get('z', 0),
                        orientation.get('x', 0),
                        orientation.get('y', 0),
                        orientation.get('z', 0),
                        orientation.get('w', 1)
                    )
                    
                    # 写入一行数据（前3行，12个元素）
                    row_data = transform_matrix[:3].flatten()
                    f.write(' '.join([f'{x:.9f}' for x in row_data]) + '\n')
        
        print(f"Exported KITTI format to: {kitti_dir}")
    
    def _export_tum(self):
        """导出为TUM数据集格式"""
        # 创建TUM格式目录
        tum_dir = os.path.join(self._output_dir, 'tum_format')
        os.makedirs(tum_dir, exist_ok=True)
        
        # 查找里程计数据
        odom_topic = None
        for topic in self._data.keys():
            if 'odom' in topic.lower():
                odom_topic = topic
                break
        
        if not odom_topic:
            print("No odometry data found for TUM export")
            return
        
        data = self._data[odom_topic]
        
        # 创建TUM格式文件
        tum_path = os.path.join(tum_dir, 'groundtruth.txt')
        
        with open(tum_path, 'w') as f:
            for item in data:
                msg = item['message']
                timestamp = item['timestamp']
                
                if 'pose' in msg and 'pose' in msg['pose']:
                    pose = msg['pose']['pose']
                    
                    # 提取位姿数据
                    position = pose.get('position', {})
                    orientation = pose.get('orientation', {})
                    
                    # TUM格式：timestamp tx ty tz qx qy qz qw
                    line = f"{timestamp:.6f} "
                    line += f"{position.get('x', 0):.9f} "
                    line += f"{position.get('y', 0):.9f} "
                    line += f"{position.get('z', 0):.9f} "
                    line += f"{orientation.get('x', 0):.9f} "
                    line += f"{orientation.get('y', 0):.9f} "
                    line += f"{orientation.get('z', 0):.9f} "
                    line += f"{orientation.get('w', 1):.9f}\n"
                    
                    f.write(line)
        
        print(f"Exported TUM format to: {tum_dir}")
    
    def _convert_to_dataframe(self, data: List[Dict]) -> pd.DataFrame:
        """将数据转换为DataFrame"""
        # 提取时间戳和消息内容
        timestamps = [item['timestamp'] for item in data]
        messages = [item['message'] for item in data]
        
        # 创建扁平化的字典列表
        flat_messages = []
        for msg in messages:
            flat_msg = self._flatten_dict(msg)
            flat_messages.append(flat_msg)
        
        # 创建DataFrame并添加时间戳列
        df = pd.DataFrame(flat_messages)
        df['timestamp'] = timestamps
        
        return df
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """扁平化字典"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict) and v:
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                for i, item in enumerate(v):
                    if isinstance(item, (dict, list)):
                        items.extend(self._flatten_dict({f"{k}_{i}": item}, parent_key, sep=sep).items())
                    else:
                        items.append((f"{new_key}_{i}", item))
            else:
                items.append((new_key, v))
        return dict(items)
    
    def _sanitize_json(self, data: Any) -> Any:
        """清理数据以便JSON序列化"""
        if isinstance(data, (int, float, str, bool, type(None))):
            return data
        elif isinstance(data, list):
            return [self._sanitize_json(item) for item in data]
        elif isinstance(data, dict):
            return {k: self._sanitize_json(v) for k, v in data.items()}
        else:
            try:
                return str(data)
            except:
                return repr(data)
    
    def _create_transform_matrix(self, x, y, z, qx, qy, qz, qw):
        """创建4x4变换矩阵"""
        # 计算旋转矩阵
        R = np.array([
            [1 - 2*qy**2 - 2*qz**2, 2*qx*qy - 2*qz*qw, 2*qx*qz + 2*qy*qw],
            [2*qx*qy + 2*qz*qw, 1 - 2*qx**2 - 2*qz**2, 2*qy*qz - 2*qx*qw],
            [2*qx*qz - 2*qy*qw, 2*qy*qz + 2*qx*qw, 1 - 2*qx**2 - 2*qy**2]
        ])
        
        # 创建变换矩阵
        transform = np.eye(4)
        transform[:3, :3] = R
        transform[:3, 3] = [x, y, z]
        
        return transform


def parse_args():
    """解析命令行参数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='数据导出工具')
    
    parser.add_argument('--input', type=str, required=True,
                        help='输入数据目录')
    parser.add_argument('--output', type=str, default='./exports',
                        help='输出数据目录')
    parser.add_argument('--format', type=str, required=True,
                        choices=['csv', 'json', 'kitti', 'tum'],
                        help='导出格式')
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    exporter = DataExporter(
        input_dir=args.input,
        output_dir=args.output,
    )
    
    try:
        exporter.load_data()
        exporter.export(args.format)
        
    except Exception as e:
        print(f"Error during export: {e}")
        raise


if __name__ == '__main__':
    main()