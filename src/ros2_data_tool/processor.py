"""数据预处理模块

实现自动清洗、时间同步、降采样、单位标准化等功能。
"""

import os
import json
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from datetime import datetime
from tqdm import tqdm


class DataProcessor:
    """数据处理器"""
    
    def __init__(self, input_dir: str, output_dir: str):
        self._input_dir = input_dir
        self._output_dir = output_dir
        self._data = {}
        self._metadata = {}
        
        os.makedirs(output_dir, exist_ok=True)
    
    def load_data(self):
        """加载采集的数据"""
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
    
    def process(self):
        """处理所有数据"""
        processed_data = {}
        
        for topic, data in tqdm(self._data.items(), desc="Processing topics"):
            processed_data[topic] = self._process_topic(data, topic)
        
        self._data = processed_data
        return processed_data
    
    def _process_topic(self, data: List[Dict], topic: str) -> List[Dict]:
        """处理单个话题的数据"""
        if not data:
            return []
        
        # 转换为DataFrame便于处理
        df = self._convert_to_dataframe(data)
        
        # 应用预处理步骤
        df = self._clean_data(df)
        df = self._remove_duplicates(df)
        df = self._filter_empty_messages(df)
        df = self._normalize_units(df, topic)
        
        # 转换回原始格式
        return self._convert_from_dataframe(df)
    
    def _convert_to_dataframe(self, data: List[Dict]) -> pd.DataFrame:
        """将数据转换为DataFrame"""
        # 提取时间戳和消息内容
        timestamps = [item['timestamp'] for item in data]
        messages = [item['message'] for item in data]
        
        # 创建扁平化的字典列表
        flat_messages = []
        for msg in messages:
            flat_msg = self._flatten_dict(msg)
            flat_msg['timestamp'] = timestamps[len(flat_messages)]
            flat_messages.append(flat_msg)
        
        return pd.DataFrame(flat_messages)
    
    def _flatten_dict(self, d: Dict, parent_key: str = '', sep: str = '_') -> Dict:
        """扁平化字典 - 优化版本"""
        items = {}
        
        def _flatten(current_dict, current_key):
            for k, v in current_dict.items():
                new_key = f"{current_key}{sep}{k}" if current_key else k
                if isinstance(v, dict) and v:
                    _flatten(v, new_key)
                elif isinstance(v, list):
                    for i, item in enumerate(v):
                        item_key = f"{new_key}_{i}"
                        if isinstance(item, (dict, list)):
                            _flatten({item_key: item}, '')
                        else:
                            items[item_key] = item
                else:
                    items[new_key] = v
        
        _flatten(d, parent_key)
        return items
    
    def _convert_from_dataframe(self, df: pd.DataFrame) -> List[Dict]:
        """将DataFrame转换回原始格式 - 优化版本"""
        result = []
        
        # 预先转换为字典列表，减少循环中的操作
        records = df.to_dict('records')
        
        for record in records:
            timestamp = record.pop('timestamp', None)
            message = self._unflatten_dict(record)
            result.append({
                'timestamp': timestamp,
                'message': message
            })
        
        return result
    
    def _unflatten_dict(self, d: Dict, sep: str = '_') -> Dict:
        """反扁平化字典"""
        result = {}
        for k, v in d.items():
            parts = k.split(sep)
            current = result
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            current[parts[-1]] = v
        return result
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """清洗数据：剔除NaN、无穷大、异常跳变"""
        # 删除包含NaN或无穷大的行
        df_clean = df.replace([np.inf, -np.inf], np.nan).dropna()
        
        # 检测并删除异常跳变
        for col in df_clean.select_dtypes(include=[np.number]).columns:
            if col != 'timestamp':
                df_clean = self._remove_outliers(df_clean, col)
        
        return df_clean
    
    def _remove_outliers(self, df: pd.DataFrame, column: str) -> pd.DataFrame:
        """使用IQR方法删除异常值"""
        Q1 = df[column].quantile(0.25)
        Q3 = df[column].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        
        return df[(df[column] >= lower_bound) & (df[column] <= upper_bound)]
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """删除重复数据"""
        # 基于时间戳删除重复
        df = df.drop_duplicates(subset=['timestamp'])
        return df.sort_values('timestamp').reset_index(drop=True)
    
    def _filter_empty_messages(self, df: pd.DataFrame) -> pd.DataFrame:
        """过滤空消息"""
        # 检查除时间戳外是否有数据
        non_timestamp_cols = [col for col in df.columns if col != 'timestamp']
        if non_timestamp_cols:
            df = df.dropna(subset=non_timestamp_cols, how='all')
        return df
    
    def _normalize_units(self, df: pd.DataFrame, topic: str) -> pd.DataFrame:
        """单位统一标准化"""
        # 根据话题类型进行单位转换
        topic_lower = topic.lower()
        
        if 'scan' in topic_lower:
            # LaserScan: 角度转弧度，距离保持米
            if 'angle_min' in df.columns:
                df['angle_min'] = np.radians(df['angle_min'])
            if 'angle_max' in df.columns:
                df['angle_max'] = np.radians(df['angle_max'])
            if 'angle_increment' in df.columns:
                df['angle_increment'] = np.radians(df['angle_increment'])
        
        elif 'imu' in topic_lower:
            # IMU: 确保角速度单位为rad/s，加速度单位为m/s²
            # 假设数据已经是标准单位，这里只做验证
            pass
        
        elif 'odom' in topic_lower:
            # Odometry: 确保位置单位为米，角度单位为弧度
            pass
        
        return df
    
    def synchronize_data(self, target_frequency: float = None) -> Dict[str, List[Dict]]:
        """时间同步：多传感器数据时间戳对齐"""
        if len(self._data) <= 1:
            return self._data
        
        # 获取所有数据的时间范围
        all_timestamps = []
        for data in self._data.values():
            all_timestamps.extend([item['timestamp'] for item in data])
        
        start_time = min(all_timestamps)
        end_time = max(all_timestamps)
        
        # 如果指定了目标频率，生成同步时间点
        if target_frequency:
            time_step = 1.0 / target_frequency
            sync_timestamps = np.arange(start_time, end_time, time_step)
        else:
            # 使用所有数据的合并时间戳
            sync_timestamps = sorted(list(set(all_timestamps)))
        
        # 对每个话题进行时间同步
        synchronized_data = {}
        for topic, data in tqdm(self._data.items(), desc="Synchronizing data"):
            synchronized_data[topic] = self._interpolate_data(data, sync_timestamps)
        
        self._data = synchronized_data
        return synchronized_data
    
    def _interpolate_data(self, data: List[Dict], sync_timestamps: np.ndarray) -> List[Dict]:
        """对数据进行插值处理"""
        if not data:
            return []
        
        # 转换为DataFrame
        df = self._convert_to_dataframe(data)
        df = df.sort_values('timestamp').reset_index(drop=True)
        
        # 创建同步时间的DataFrame
        sync_df = pd.DataFrame({'timestamp': sync_timestamps})
        
        # 对数值型列进行插值
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        sync_df = pd.merge_asof(sync_df, df[numeric_cols], on='timestamp', direction='nearest')
        
        # 转换回原始格式
        return self._convert_from_dataframe(sync_df)
    
    def downsample(self, frequency: float) -> Dict[str, List[Dict]]:
        """数据降采样"""
        downsampled_data = {}
        
        for topic, data in tqdm(self._data.items(), desc="Downsampling data"):
            if not data:
                downsampled_data[topic] = []
                continue
            
            # 计算采样间隔
            sample_interval = 1.0 / frequency
            
            # 按时间间隔采样
            downsampled = []
            last_timestamp = None
            
            for item in sorted(data, key=lambda x: x['timestamp']):
                current_timestamp = item['timestamp']
                if last_timestamp is None or current_timestamp - last_timestamp >= sample_interval:
                    downsampled.append(item)
                    last_timestamp = current_timestamp
            
            downsampled_data[topic] = downsampled
        
        self._data = downsampled_data
        return downsampled_data
    
    def save_processed_data(self):
        """保存处理后的数据"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 更新元数据
        self._metadata['processing_time'] = datetime.now().isoformat()
        self._metadata['processed_data_count'] = {
            topic: len(data) for topic, data in self._data.items()
        }
        
        # 保存元数据
        metadata_path = os.path.join(self._output_dir, f'metadata_processed_{timestamp}.json')
        with open(metadata_path, 'w') as f:
            json.dump(self._metadata, f, indent=2)
        
        # 保存处理后的数据
        for topic, data in self._data.items():
            data_path = os.path.join(self._output_dir, f'{topic}_processed_{timestamp}.pkl')
            
            with open(data_path, 'wb') as f:
                pickle.dump(data, f)
            
            print(f"Saved {len(data)} processed messages for topic {topic} to {data_path}")


def parse_args():
    """解析命令行参数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='数据预处理工具')
    
    parser.add_argument('--input', type=str, required=True,
                        help='输入数据目录')
    parser.add_argument('--output', type=str, default='./processed',
                        help='输出数据目录')
    parser.add_argument('--sync', action='store_true',
                        help='是否进行时间同步')
    parser.add_argument('--frequency', type=float,
                        help='目标频率（用于同步和降采样）')
    parser.add_argument('--downsample', action='store_true',
                        help='是否进行降采样')
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    processor = DataProcessor(
        input_dir=args.input,
        output_dir=args.output,
    )
    
    try:
        processor.load_data()
        processor.process()
        
        if args.sync:
            processor.synchronize_data(args.frequency)
        
        if args.downsample and args.frequency:
            processor.downsample(args.frequency)
        
        processor.save_processed_data()
        
    except Exception as e:
        print(f"Error during processing: {e}")
        raise


if __name__ == '__main__':
    main()