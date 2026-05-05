"""数据可视化模块

实现激光点云、轨迹、性能统计等可视化功能。
"""

import os
import json
import pickle
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from typing import Dict, List, Any
from datetime import datetime


class DataVisualizer:
    """数据可视化器"""
    
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
    
    def visualize_all(self):
        """可视化所有数据"""
        for topic, data in self._data.items():
            topic_lower = topic.lower()
            
            if 'scan' in topic_lower:
                self._visualize_laserscan(data, topic)
            elif 'odom' in topic_lower:
                self._visualize_odometry(data, topic)
            elif 'imu' in topic_lower:
                self._visualize_imu(data, topic)
            elif 'twist' in topic_lower:
                self._visualize_twist(data, topic)
        
        # 生成性能统计
        self._generate_performance_report()
    
    def _visualize_laserscan(self, data: List[Dict], topic: str):
        """可视化激光雷达数据"""
        if not data:
            return
        
        # 获取最新的激光扫描数据
        latest_scan = data[-1]['message']
        
        # 提取激光数据
        ranges = np.array(latest_scan.get('ranges', []))
        angle_min = latest_scan.get('angle_min', 0.0)
        angle_max = latest_scan.get('angle_max', 2 * np.pi)
        angle_increment = latest_scan.get('angle_increment', np.pi / 180)
        
        # 过滤无效数据
        valid_indices = np.where((ranges > 0) & (ranges < 100))[0]
        if len(valid_indices) == 0:
            return
        
        ranges = ranges[valid_indices]
        angles = angle_min + angle_increment * valid_indices
        
        # 转换为笛卡尔坐标
        x = ranges * np.cos(angles)
        y = ranges * np.sin(angles)
        
        # 创建图形
        fig, ax = plt.subplots(figsize=(10, 10))
        ax.scatter(x, y, s=1, c='blue', alpha=0.5)
        
        # 设置坐标轴
        ax.set_aspect('equal')
        max_range = max(np.max(np.abs(x)), np.max(np.abs(y))) * 1.1
        ax.set_xlim(-max_range, max_range)
        ax.set_ylim(-max_range, max_range)
        
        # 添加原点和坐标轴
        ax.plot([0], [0], 'ro', markersize=5)
        ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
        ax.axvline(0, color='gray', linestyle='--', alpha=0.5)
        
        # 添加标题和标签
        ax.set_title(f'LaserScan Visualization - {topic}')
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        
        # 保存图像
        output_path = os.path.join(
            self._output_dir, 
            f'laserscan_{topic}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        )
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved LaserScan visualization to {output_path}")
    
    def _visualize_odometry(self, data: List[Dict], topic: str):
        """可视化里程计数据"""
        if not data:
            return
        
        # 提取位置数据
        timestamps = []
        x_positions = []
        y_positions = []
        velocities = []
        
        for item in data:
            msg = item['message']
            timestamp = item['timestamp']
            
            if 'pose' in msg and 'pose' in msg['pose']:
                pose = msg['pose']['pose']
                if 'position' in pose:
                    x_positions.append(pose['position'].get('x', 0))
                    y_positions.append(pose['position'].get('y', 0))
                    timestamps.append(timestamp)
            
            if 'twist' in msg and 'twist' in msg['twist']:
                twist = msg['twist']['twist']
                if 'linear' in twist:
                    linear = twist['linear']
                    velocity = np.sqrt(linear.get('x', 0)**2 + linear.get('y', 0)**2)
                    velocities.append(velocity)
        
        # 绘制轨迹
        if x_positions and y_positions:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))
            
            # 轨迹图
            ax1.plot(x_positions, y_positions, 'b-', linewidth=2)
            ax1.plot(x_positions[0], y_positions[0], 'go', markersize=8, label='Start')
            ax1.plot(x_positions[-1], y_positions[-1], 'ro', markersize=8, label='End')
            ax1.set_aspect('equal')
            ax1.set_title(f'Robot Trajectory - {topic}')
            ax1.set_xlabel('X (m)')
            ax1.set_ylabel('Y (m)')
            ax1.legend()
            ax1.grid(True)
            
            # 速度图
            if velocities and timestamps:
                ax2.plot(timestamps, velocities, 'r-', linewidth=2)
                ax2.set_title('Linear Velocity')
                ax2.set_xlabel('Time (s)')
                ax2.set_ylabel('Velocity (m/s)')
                ax2.grid(True)
            
            # 保存图像
            output_path = os.path.join(
                self._output_dir, 
                f'odometry_{topic}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
            )
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"Saved Odometry visualization to {output_path}")
    
    def _visualize_imu(self, data: List[Dict], topic: str):
        """可视化IMU数据"""
        if not data:
            return
        
        # 提取IMU数据
        timestamps = []
        angular_vel_x = []
        angular_vel_y = []
        angular_vel_z = []
        linear_acc_x = []
        linear_acc_y = []
        linear_acc_z = []
        
        for item in data:
            msg = item['message']
            timestamp = item['timestamp']
            
            if 'angular_velocity' in msg:
                angular = msg['angular_velocity']
                angular_vel_x.append(angular.get('x', 0))
                angular_vel_y.append(angular.get('y', 0))
                angular_vel_z.append(angular.get('z', 0))
            
            if 'linear_acceleration' in msg:
                linear = msg['linear_acceleration']
                linear_acc_x.append(linear.get('x', 0))
                linear_acc_y.append(linear.get('y', 0))
                linear_acc_z.append(linear.get('z', 0))
            
            timestamps.append(timestamp)
        
        # 创建图形
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
        
        # 角速度图
        ax1.plot(timestamps, angular_vel_x, 'r-', label='X')
        ax1.plot(timestamps, angular_vel_y, 'g-', label='Y')
        ax1.plot(timestamps, angular_vel_z, 'b-', label='Z')
        ax1.set_title('Angular Velocity')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Velocity (rad/s)')
        ax1.legend()
        ax1.grid(True)
        
        # 线加速度图
        ax2.plot(timestamps, linear_acc_x, 'r-', label='X')
        ax2.plot(timestamps, linear_acc_y, 'g-', label='Y')
        ax2.plot(timestamps, linear_acc_z, 'b-', label='Z')
        ax2.set_title('Linear Acceleration')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Acceleration (m/s²)')
        ax2.legend()
        ax2.grid(True)
        
        # 角速度直方图
        if angular_vel_z:
            ax3.hist(angular_vel_z, bins=50, alpha=0.7, color='blue')
            ax3.set_title('Angular Velocity Z Distribution')
            ax3.set_xlabel('Angular Velocity (rad/s)')
            ax3.set_ylabel('Frequency')
            ax3.grid(True)
        
        # 线加速度直方图
        if linear_acc_z:
            ax4.hist(linear_acc_z, bins=50, alpha=0.7, color='red')
            ax4.set_title('Linear Acceleration Z Distribution')
            ax4.set_xlabel('Acceleration (m/s²)')
            ax4.set_ylabel('Frequency')
            ax4.grid(True)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图像
        output_path = os.path.join(
            self._output_dir, 
            f'imu_{topic}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        )
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved IMU visualization to {output_path}")
    
    def _visualize_twist(self, data: List[Dict], topic: str):
        """可视化Twist数据"""
        if not data:
            return
        
        # 提取Twist数据
        timestamps = []
        linear_x = []
        angular_z = []
        
        for item in data:
            msg = item['message']
            timestamp = item['timestamp']
            
            if 'linear' in msg:
                linear_x.append(msg['linear'].get('x', 0))
            if 'angular' in msg:
                angular_z.append(msg['angular'].get('z', 0))
            
            timestamps.append(timestamp)
        
        # 创建图形
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # 线速度图
        ax1.plot(timestamps, linear_x, 'b-', linewidth=2)
        ax1.set_title(f'Linear Velocity - {topic}')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('Velocity (m/s)')
        ax1.grid(True)
        
        # 角速度图
        ax2.plot(timestamps, angular_z, 'r-', linewidth=2)
        ax2.set_title('Angular Velocity')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Velocity (rad/s)')
        ax2.grid(True)
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图像
        output_path = os.path.join(
            self._output_dir, 
            f'twist_{topic}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        )
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Saved Twist visualization to {output_path}")
    
    def _generate_performance_report(self):
        """生成性能统计报告"""
        stats = {}
        
        for topic, data in self._data.items():
            if not data:
                continue
            
            # 计算话题频率
            timestamps = [item['timestamp'] for item in data]
            if len(timestamps) > 1:
                time_diffs = np.diff(timestamps)
                frequency = 1.0 / np.mean(time_diffs) if np.mean(time_diffs) > 0 else 0
                stats[topic] = {
                    'message_count': len(data),
                    'frequency': frequency,
                    'time_range': (min(timestamps), max(timestamps)),
                    'duration': max(timestamps) - min(timestamps)
                }
        
        # 创建性能报告
        fig, ax = plt.subplots(figsize=(12, 8))
        
        topics = list(stats.keys())
        frequencies = [stats[t]['frequency'] for t in topics]
        message_counts = [stats[t]['message_count'] for t in topics]
        
        # 创建柱状图
        x = np.arange(len(topics))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, frequencies, width, label='Frequency (Hz)')
        bars2 = ax.bar(x + width/2, message_counts, width, label='Message Count')
        
        # 设置标签和标题
        ax.set_xlabel('Topics')
        ax.set_ylabel('Value')
        ax.set_title('Topic Performance Statistics')
        ax.set_xticks(x)
        ax.set_xticklabels(topics, rotation=45, ha='right')
        ax.legend()
        
        # 在柱状图上添加数值标签
        for bar in bars1:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.2f}', ha='center', va='bottom')
        
        for bar in bars2:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{int(height)}', ha='center', va='bottom')
        
        # 调整布局
        plt.tight_layout()
        
        # 保存图像
        output_path = os.path.join(
            self._output_dir, 
            f'performance_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.png'
        )
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        # 保存统计数据
        stats_path = os.path.join(
            self._output_dir, 
            f'performance_stats_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
        )
        with open(stats_path, 'w') as f:
            json.dump(stats, f, indent=2)
        
        print(f"Saved performance report to {output_path}")
        print(f"Saved performance statistics to {stats_path}")


def parse_args():
    """解析命令行参数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='数据可视化工具')
    
    parser.add_argument('--input', type=str, required=True,
                        help='输入数据目录')
    parser.add_argument('--output', type=str, default='./visualizations',
                        help='输出图像目录')
    
    return parser.parse_args()


def main():
    """主函数"""
    args = parse_args()
    
    visualizer = DataVisualizer(
        input_dir=args.input,
        output_dir=args.output,
    )
    
    try:
        visualizer.load_data()
        visualizer.visualize_all()
        
    except Exception as e:
        print(f"Error during visualization: {e}")
        raise


if __name__ == '__main__':
    main()