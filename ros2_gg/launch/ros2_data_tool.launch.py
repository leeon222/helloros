"""ROS2自动化数据采集与处理工具 - Launch文件"""

import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.conditions import IfCondition


def generate_launch_description():
    """生成launch描述"""
    
    # 获取当前目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    # 声明启动参数
    topics_arg = DeclareLaunchArgument(
        'topics',
        default_value='/scan /odom /imu/data',
        description='要采集的话题列表'
    )
    
    output_dir_arg = DeclareLaunchArgument(
        'output',
        default_value='./data',
        description='数据保存路径'
    )
    
    duration_arg = DeclareLaunchArgument(
        'duration',
        default_value='30.0',
        description='采集时长（秒）'
    )
    
    sync_arg = DeclareLaunchArgument(
        'sync',
        default_value='true',
        description='是否进行时间同步'
    )
    
    frequency_arg = DeclareLaunchArgument(
        'frequency',
        default_value='10.0',
        description='目标频率'
    )
    
    format_arg = DeclareLaunchArgument(
        'format',
        default_value='csv',
        description='导出格式'
    )
    
    # 创建一键运行脚本命令
    run_command = [
        'python',
        os.path.join(project_root, 'run_tool.py'),
        '--mode', 'all',
        '--topics', LaunchConfiguration('topics'),
        '--output', LaunchConfiguration('output'),
        '--duration', LaunchConfiguration('duration'),
        '--sync', LaunchConfiguration('sync'),
        '--frequency', LaunchConfiguration('frequency'),
        '--format', LaunchConfiguration('format'),
    ]
    
    # 创建执行过程
    run_tool = ExecuteProcess(
        cmd=run_command,
        output='screen',
    )
    
    return LaunchDescription([
        topics_arg,
        output_dir_arg,
        duration_arg,
        sync_arg,
        frequency_arg,
        format_arg,
        run_tool,
    ])