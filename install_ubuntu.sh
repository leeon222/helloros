#!/bin/bash
# ROS2自动化数据采集工具 - Ubuntu安装脚本
# 支持Ubuntu 20.04 LTS及以上版本

set -e

echo "=========================================="
echo "ROS2自动化数据采集工具 - Ubuntu安装脚本"
echo "支持Ubuntu 20.04 LTS及以上版本"
echo "=========================================="

# 检查Ubuntu版本
UBUNTU_VERSION=$(lsb_release -rs)
echo "当前Ubuntu版本: $UBUNTU_VERSION"

# 根据Ubuntu版本确定ROS2版本
if [[ "$UBUNTU_VERSION" == "20.04" ]]; then
    ROS_DISTRO="noetic"
    echo "检测到Ubuntu 20.04，将安装ROS2 Noetic"
elif [[ "$UBUNTU_VERSION" == "22.04" ]]; then
    ROS_DISTRO="humble"
    echo "检测到Ubuntu 22.04，将安装ROS2 Humble"
else
    echo "警告: 当前Ubuntu版本 $UBUNTU_VERSION 未在测试范围内"
    echo "建议使用Ubuntu 20.04 LTS或Ubuntu 22.04 LTS"
    read -p "是否继续安装? (y/n): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# 更新系统
echo -e "\n[1/5] 更新系统包..."
sudo apt update && sudo apt upgrade -y

# 安装基础依赖
echo -e "\n[2/5] 安装基础依赖..."
sudo apt install -y \
    python3-pip \
    python3-dev \
    python3-venv \
    git \
    curl \
    wget \
    build-essential \
    cmake \
    libssl-dev \
    libboost-all-dev \
    libyaml-cpp-dev

# 安装Python依赖
echo -e "\n[3/5] 安装Python依赖..."
if [ -f "requirements.txt" ]; then
    echo "从requirements.txt安装依赖..."
    pip3 install --upgrade pip
    pip3 install -r requirements.txt
else
    echo "未找到requirements.txt，安装基本依赖..."
    pip3 install --upgrade pip
    pip3 install \
        rclpy>=3.0.0 \
        numpy>=1.20.0 \
        pandas>=1.3.0 \
        matplotlib>=3.4.0 \
        opencv-python>=4.5.0 \
        pyyaml>=6.0 \
        tqdm>=4.60.0 \
        Pillow>=8.0.0 \
        python-dateutil>=2.8.0 \
        psutil>=5.9.0 \
        typing-extensions>=4.0.0
fi

# 设置Python路径
echo -e "\n[4/5] 设置环境变量..."
echo "export PYTHONPATH=\"\$PYTHONPATH:$(pwd)\"" >> ~/.bashrc

# 创建必要的目录
echo -e "\n[5/5] 创建必要的目录..."
mkdir -p data processed visualizations exports

echo -e "\n=========================================="
echo "安装完成！"
echo "=========================================="
echo "请执行以下命令使环境变量生效："
echo "source ~/.bashrc"
echo
echo "使用示例："
echo "python run_tool.py --mode all --topics /scan /odom /imu/data"
echo
echo "如果需要使用ROS2 launch文件，请确保已安装ROS2并设置环境："
echo "source /opt/ros/$ROS_DISTRO/setup.bash"
echo "ros2 launch launch/ros2_data_tool.launch.py"