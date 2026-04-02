"""ROS1/ROS2兼容性层

提供统一的接口访问ROS功能，处理不同版本的消息类型和API差异。
"""

import sys
import importlib
from typing import Any, Dict, Optional, Type


class ROSVersion:
    """ROS版本检测和兼容性处理"""
    
    ROS1 = 'ros1'
    ROS2 = 'ros2'
    UNKNOWN = 'unknown'
    
    @classmethod
    def detect(cls) -> str:
        """检测当前ROS版本"""
        try:
            import rclpy
            return cls.ROS2
        except ImportError:
            try:
                import rospy
                return cls.ROS1
            except ImportError:
                return cls.UNKNOWN


class ROSCompat:
    """ROS兼容性管理器"""
    
    def __init__(self):
        self._ros_version = ROSVersion.detect()
        self._imports = {}
        self._message_types = {}
        self._init_ros()
    
    def _init_ros(self):
        """初始化ROS环境"""
        if self._ros_version == ROSVersion.ROS2:
            self._init_ros2()
        elif self._ros_version == ROSVersion.ROS1:
            self._init_ros1()
    
    def _init_ros2(self):
        """初始化ROS2导入"""
        self._imports['rclpy'] = importlib.import_module('rclpy')
        self._imports['Node'] = getattr(self._imports['rclpy'], 'Node')
        self._imports['init'] = getattr(self._imports['rclpy'], 'init')
        self._imports['spin'] = getattr(self._imports['rclpy'], 'spin')
        self._imports['shutdown'] = getattr(self._imports['rclpy'], 'shutdown')
        
        # 消息类型
        self._message_types['LaserScan'] = self._import_message_type(
            'sensor_msgs.msg', 'LaserScan')
        self._message_types['Image'] = self._import_message_type(
            'sensor_msgs.msg', 'Image')
        self._message_types['Imu'] = self._import_message_type(
            'sensor_msgs.msg', 'Imu')
        self._message_types['Odometry'] = self._import_message_type(
            'nav_msgs.msg', 'Odometry')
        self._message_types['TransformStamped'] = self._import_message_type(
            'geometry_msgs.msg', 'TransformStamped')
        self._message_types['Twist'] = self._import_message_type(
            'geometry_msgs.msg', 'Twist')
    
    def _init_ros1(self):
        """初始化ROS1导入"""
        self._imports['rospy'] = importlib.import_module('rospy')
        self._imports['init_node'] = getattr(self._imports['rospy'], 'init_node')
        self._imports['spin'] = getattr(self._imports['rospy'], 'spin')
        self._imports['Subscriber'] = getattr(self._imports['rospy'], 'Subscriber')
        
        # 消息类型
        self._message_types['LaserScan'] = self._import_message_type(
            'sensor_msgs.msg', 'LaserScan')
        self._message_types['Image'] = self._import_message_type(
            'sensor_msgs.msg', 'Image')
        self._message_types['Imu'] = self._import_message_type(
            'sensor_msgs.msg', 'Imu')
        self._message_types['Odometry'] = self._import_message_type(
            'nav_msgs.msg', 'Odometry')
        self._message_types['TransformStamped'] = self._import_message_type(
            'geometry_msgs.msg', 'TransformStamped')
        self._message_types['Twist'] = self._import_message_type(
            'geometry_msgs.msg', 'Twist')
    
    def _import_message_type(self, package: str, message_type: str) -> Optional[Type]:
        """导入ROS消息类型"""
        try:
            module = importlib.import_module(package)
            return getattr(module, message_type)
        except (ImportError, AttributeError):
            return None
    
    def get_ros_version(self) -> str:
        """获取当前ROS版本"""
        return self._ros_version
    
    def get_import(self, name: str) -> Optional[Any]:
        """获取导入的模块或函数"""
        return self._imports.get(name)
    
    def get_message_type(self, message_name: str) -> Optional[Type]:
        """获取消息类型"""
        return self._message_types.get(message_name)
    
    def is_ros2(self) -> bool:
        """检查是否为ROS2环境"""
        return self._ros_version == ROSVersion.ROS2
    
    def is_ros1(self) -> bool:
        """检查是否为ROS1环境"""
        return self._ros_version == ROSVersion.ROS1


# 全局兼容性实例
ros_compat = ROSCompat()


def get_ros_version() -> str:
    """获取当前ROS版本"""
    return ros_compat.get_ros_version()


def is_ros2() -> bool:
    """检查是否为ROS2环境"""
    return ros_compat.is_ros2()


def is_ros1() -> bool:
    """检查是否为ROS1环境"""
    return ros_compat.is_ros1()


def get_message_type(message_name: str) -> Optional[Type]:
    """获取消息类型"""
    return ros_compat.get_message_type(message_name)


def get_import(name: str) -> Optional[Any]:
    """获取导入的模块或函数"""
    return ros_compat.get_import(name)