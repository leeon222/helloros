"""数据采集模块

支持同时采集多个ROS2话题，保存原始数据。
"""

import argparse
import os
import json
import pickle
import time
from datetime import datetime
from typing import List, Dict, Any


class DataCollector:
    """数据采集器"""
    
    def __init__(self, topics: List[str], output_dir: str, duration: float = None):
        self._topics = topics
        self._output_dir = output_dir
        self._duration = duration
        self._data = {topic: [] for topic in topics}
        self._start_time = None
        self._end_time = None
        self._node = None
        self._subscribers = []
        
        # 创建输出目录
        os.makedirs(output_dir, exist_ok=True)
    
    def _create_node(self):
        """创建ROS2节点"""
        # 延迟导入rclpy
        import rclpy
        from rclpy.node import Node
        rclpy.init()
        self._node = Node('data_collector')
    
    def _create_subscriber(self, topic: str):
        """创建话题订阅器"""
        max_retries = 3
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                message_type = self._get_message_type_for_topic(topic)
                if not message_type:
                    print(f"Warning: Cannot determine message type for topic {topic}")
                    return
                
                callback = self._create_callback(topic)
                subscriber = self._node.create_subscription(
                    message_type, topic, callback, 10)
                self._subscribers.append(subscriber)
                return
                
            except Exception as e:
                retry_count += 1
                print(f"Warning: Failed to create subscriber for topic {topic} (attempt {retry_count}/{max_retries}): {e}")
                if retry_count < max_retries:
                    import time
                    time.sleep(1)  # 等待1秒后重试
        
        print(f"Error: Failed to create subscriber for topic {topic} after {max_retries} attempts")
    
    def _get_message_type_for_topic(self, topic: str) -> Any:
        """根据话题名推断消息类型"""
        topic_lower = topic.lower()
        
        # 延迟导入消息类型
        from sensor_msgs.msg import LaserScan, Image, Imu
        from nav_msgs.msg import Odometry
        from geometry_msgs.msg import TransformStamped, Twist
        
        if 'scan' in topic_lower:
            return LaserScan
        elif 'image' in topic_lower or 'camera' in topic_lower:
            return Image
        elif 'imu' in topic_lower:
            return Imu
        elif 'odom' in topic_lower:
            return Odometry
        elif 'tf' in topic_lower:
            return TransformStamped
        elif 'cmd_vel' in topic_lower or 'twist' in topic_lower:
            return Twist
        
        return None
    
    def _create_callback(self, topic: str):
        """创建回调函数"""
        def callback(msg):
            timestamp = self._get_timestamp(msg)
            data = {
                'timestamp': timestamp,
                'message': self._serialize_message(msg),
            }
            self._data[topic].append(data)
        
        return callback
    
    def _get_timestamp(self, msg) -> float:
        """获取消息时间戳"""
        if hasattr(msg, 'header') and hasattr(msg.header, 'stamp'):
            return msg.header.stamp.sec + msg.header.stamp.nanosec * 1e-9
        return time.time()
    
    def _serialize_message(self, msg) -> Dict[str, Any]:
        """序列化消息"""
        serialized = {}
        
        for attr_name in dir(msg):
            if not attr_name.startswith('_'):
                attr_value = getattr(msg, attr_name)
                serialized[attr_name] = self._serialize_value(attr_value)
        
        return serialized
    
    def _serialize_value(self, value) -> Any:
        """序列化值"""
        if isinstance(value, (int, float, str, bool, type(None))):
            return value
        elif isinstance(value, list):
            return [self._serialize_value(item) for item in value]
        elif isinstance(value, tuple):
            return tuple(self._serialize_value(item) for item in value)
        elif hasattr(value, '__dict__'):
            return {k: self._serialize_value(v) for k, v in value.__dict__.items()
                   if not k.startswith('_')}
        else:
            try:
                return str(value)
            except:
                return repr(value)
    
    def start(self):
        """开始采集"""
        self._start_time = time.time()
        self._create_node()
        
        for topic in self._topics:
            self._create_subscriber(topic)
            print(f"Subscribed to topic: {topic}")
        
        print(f"Data collection started. Duration: {self._duration} seconds" 
              if self._duration else "Data collection started. Press Ctrl+C to stop.")
        
        # 延迟导入rclpy
        import rclpy
        if self._duration:
            rclpy.spin_once(self._node, timeout_sec=self._duration)
        else:
            rclpy.spin(self._node)
    
    def stop(self):
        """停止采集"""
        self._end_time = time.time()
        print(f"Data collection stopped. Collected {len(self._data)} topics")
        
        self._node.destroy_node()
        # 延迟导入rclpy
        import rclpy
        rclpy.shutdown()
    
    def save_data(self):
        """保存采集的数据 - 带事务处理"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        try:
            # 保存元数据
            metadata = {
                'start_time': self._start_time,
                'end_time': self._end_time,
                'duration': self._end_time - self._start_time if self._end_time else None,
                'topics': self._topics,
                'data_count': {topic: len(data) for topic, data in self._data.items()},
            }
            
            metadata_path = os.path.join(self._output_dir, f'metadata_{timestamp}.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            # 保存每个话题的数据
            saved_topics = []
            for topic, data in self._data.items():
                if data:  # 只保存非空数据
                    topic_name = topic.replace('/', '_').strip('_')
                    data_path = os.path.join(self._output_dir, f'{topic_name}_{timestamp}.pkl')
                    
                    try:
                        with open(data_path, 'wb') as f:
                            pickle.dump(data, f)
                        saved_topics.append(topic)
                        print(f"Saved {len(data)} messages for topic {topic} to {data_path}")
                    except Exception as e:
                        print(f"Error saving data for topic {topic}: {e}")
            
            if saved_topics:
                print(f"\nSuccessfully saved data for {len(saved_topics)} topics")
            else:
                print("\nNo data was saved (all topics had no messages)")
                
        except Exception as e:
            print(f"Error during data saving: {e}")
            # 尝试保存部分数据
            self._save_partial_data(timestamp)
    
    def _save_partial_data(self, timestamp):
        """保存部分数据（在主保存失败时调用）"""
        print("\nAttempting to save partial data...")
        
        partial_metadata = {
            'start_time': self._start_time,
            'end_time': self._end_time,
            'partial_save': True,
            'saved_topics': [],
        }
        
        saved_count = 0
        for topic, data in self._data.items():
            if data:
                try:
                    topic_name = topic.replace('/', '_').strip('_')
                    data_path = os.path.join(self._output_dir, f'{topic_name}_{timestamp}_partial.pkl')
                    
                    with open(data_path, 'wb') as f:
                        pickle.dump(data, f)
                    saved_count += 1
                    partial_metadata['saved_topics'].append(topic)
                    print(f"Partially saved {len(data)} messages for topic {topic}")
                    
                except Exception as e:
                    print(f"Failed to save partial data for topic {topic}: {e}")
        
        if saved_count > 0:
            metadata_path = os.path.join(self._output_dir, f'metadata_{timestamp}_partial.json')
            try:
                with open(metadata_path, 'w') as f:
                    json.dump(partial_metadata, f, indent=2)
                print(f"\nSuccessfully saved partial data for {saved_count} topics")
            except Exception as e:
                print(f"Failed to save partial metadata: {e}")
        else:
            print("\nFailed to save any partial data")


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='ROS2数据采集工具')
    
    parser.add_argument('--topics', type=str, nargs='+', required=True,
                        help='要采集的话题列表')
    parser.add_argument('--output', type=str, default='./data',
                        help='数据保存路径')
    parser.add_argument('--duration', type=float,
                        help='采集时长（秒），不指定则一直采集直到Ctrl+C')
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    collector = DataCollector(
        topics=args.topics,
        output_dir=args.output,
        duration=args.duration,
    )
    
    try:
        collector.start()
    except KeyboardInterrupt:
        print("\nReceived keyboard interrupt. Stopping collection...")
    finally:
        collector.stop()
        collector.save_data()


if __name__ == '__main__':
    main()