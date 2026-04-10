# ROS2 自动化数据采集与智能处理工具

## 项目定位

ROS2一站式自动化数据采集与智能处理工具链，面向机器人调试、数据集制作、故障复盘、系统性能监控。

- **自动化数据采集**：支持同时采集多个ROS2话题
- **智能预处理**：自动清洗、时间同步、降采样、单位标准化
- **可视化分析**：激光点云、轨迹、性能统计
- **标准化导出**：支持多种格式导出（CSV、JSON、PNG、ROS Bag）

## 功能特性

### 数据采集
- 支持同时采集多个ROS2话题：LaserScan、Image、Imu、Odometry、TF、Twist
- 命令行参数简洁易用，支持指定话题、保存路径、采集时长
- 自动检测话题类型并匹配相应的消息格式

### 数据预处理（核心差异化功能）
- 自动清洗：剔除NaN、无穷大、异常跳变数据
- 时间同步：多传感器数据时间戳对齐，支持插值处理
- 数据降采样、去重、空消息过滤
- 单位统一标准化：角度转弧度、距离单位统一等

### 数据导出
- 通用格式：CSV、JSON、PNG
- SLAM常用数据集格式：KITTI、TUM
- 支持自定义导出格式扩展

### 可视化与分析
- 激光雷达2D点云绘制，支持动态显示
- 里程计/IMU位置、速度、角速度曲线绘制
- 机器人运动轨迹绘制，包含起点和终点标记
- 话题频率、延迟、丢包率统计
- 自动生成性能分析报告

## 安装说明

### 系统要求
- Ubuntu 20.04 LTS及以上版本
- Python 3.8+
- ROS2 Humble（Ubuntu 22.04）或ROS2 Noetic（Ubuntu 20.04）

### 安装步骤

#### Ubuntu系统自动安装（推荐）
```bash
# 克隆项目
git clone https://github.com/ros2_gg/ros2_gg.git
cd ros2_gg

# 运行自动安装脚本
chmod +x install_ubuntu.sh
./install_ubuntu.sh

# 使环境变量生效
source ~/.bashrc
```

#### 手动安装步骤

1. 克隆项目
```bash
git clone https://github.com/ros2_gg/ros2_gg.git
cd ros2_gg
```

2. 安装Python依赖
```bash
pip3 install -r requirements.txt
```

3. 设置Python路径（可选，便于直接运行）
```bash
export PYTHONPATH=$PYTHONPATH:$PWD
echo "export PYTHONPATH=\"\$PYTHONPATH:$PWD\"" >> ~/.bashrc
source ~/.bashrc
```

4. ROS2工作区构建（可选，用于launch文件）
```bash
colcon build
source install/setup.bash
```

## 使用示例

### 1. 数据采集
```bash
# 基本用法：采集指定话题数据
python3 scripts/collector.py --topics /scan /odom /imu/data --output ./data/

# 指定采集时长（10秒）
python3 scripts/collector.py --topics /scan /odom /imu/data --output ./data/ --duration 10

# 采集单个话题
python3 scripts/collector.py --topics /scan --output ./data/
```

### 2. 数据预处理
```bash
# 基本预处理
python3 scripts/processor.py --input ./data/ --output ./processed/

# 启用时间同步和降采样（10Hz）
python3 scripts/processor.py --input ./data/ --output ./processed/ --sync --frequency 10.0

# 仅启用降采样（5Hz）
python3 scripts/processor.py --input ./data/ --output ./processed/ --downsample --frequency 5.0
```

### 3. 数据可视化
```bash
# 可视化处理后的数据
python3 scripts/visualizer.py --input ./processed/ --output ./visualizations/
```

### 4. 数据导出
```bash
# 导出为CSV格式
python3 scripts/exporter.py --input ./processed/ --output ./exports/ --format csv

# 导出为JSON格式
python3 scripts/exporter.py --input ./processed/ --output ./exports/ --format json

# 导出为KITTI格式（用于SLAM）
python3 scripts/exporter.py --input ./processed/ --output ./exports/ --format kitti

# 导出为TUM格式（用于SLAM）
python3 scripts/exporter.py --input ./processed/ --output ./exports/ --format tum
```

### 5. 一键运行（推荐）

#### 使用默认配置
```bash
# 使用默认配置启动（无需任何参数）
python3 run_tool.py
```

#### 使用配置文件
```bash
# 使用配置文件启动
python3 run_tool.py --config config_example.yaml

# 配置文件覆盖示例（命令行参数优先）
python3 run_tool.py --config config_example.yaml --mode collect --duration 60
```

#### 命令行参数方式
```bash
# 仅采集数据
python3 run_tool.py --mode collect --topics /scan /odom /imu/data --duration 30

# 完整流程：采集→预处理→可视化→导出（CSV格式）
python3 run_tool.py --mode all --topics /scan /odom /imu/data --duration 30 --sync --frequency 10 --format csv

# 仅预处理和导出
python3 run_tool.py --mode process --output ./data/ --sync --frequency 10
python3 run_tool.py --mode export --output ./data/ --format kitti
```

### 6. ROS2 Launch启动
```bash
# 使用默认参数启动
ros2 launch launch/ros2_data_tool.launch.py

# 指定参数启动
ros2 launch launch/ros2_data_tool.launch.py topics:="/scan /odom /imu/data" duration:=30.0 sync:=true frequency:=10.0
```

## 项目结构

```
ros2_gg/
├── src/                        # 源代码目录
│   └── ros2_data_tool/         # 主包目录
│       ├── __init__.py         # 包初始化文件
│       ├── collector.py        # 数据采集模块
│       ├── processor.py        # 数据预处理模块
│       ├── visualizer.py       # 数据可视化模块
│       ├── exporter.py         # 数据导出模块
│       └── logger.py           # 日志模块
├── scripts/                    # 运行脚本目录
│   ├── collector.py            # 采集脚本入口
│   ├── processor.py            # 预处理脚本入口
│   ├── visualizer.py           # 可视化脚本入口
│   └── exporter.py             # 导出脚本入口
├── launch/                     # ROS2 launch文件目录
│   └── ros2_data_tool.launch.py # 主launch文件
├── config/                     # 配置文件目录
├── config_example.yaml         # 配置文件示例
├── data/                       # 默认数据存储目录
├── run_tool.py                 # 一键运行脚本
├── requirements.txt            # Python依赖文件
└── README.md                   # 项目文档
```

## 核心模块说明



### collector.py
数据采集模块，支持同时订阅多个ROS话题，自动识别话题类型，保存原始数据到文件。包含命令行参数解析功能。

### processor.py
数据预处理模块，实现自动清洗（剔除无效数据）、时间同步（多传感器数据对齐）、降采样（降低数据频率）等功能。使用pandas进行数据处理。

### visualizer.py
数据可视化模块，使用matplotlib实现激光雷达点云可视化、机器人轨迹绘制、IMU数据曲线等功能。支持自动生成性能统计报告。

### exporter.py
数据导出模块，支持将处理后的数据导出为多种格式，包括CSV、JSON、KITTI、TUM等。特别支持SLAM常用的数据集格式。

### logger.py
日志模块，提供分级日志系统（INFO、WARNING、ERROR），支持详细的错误信息和解决建议，提高程序的可靠性和可调试性。

## 配置文件

### YAML配置文件
程序支持使用YAML格式的配置文件，提供更灵活的配置方式。配置文件示例：`config_example.yaml`。

**配置文件使用方法：**
```bash
python3 run_tool.py --config config_example.yaml
```

**配置文件优先级：**
- 命令行参数优先于配置文件
- 配置文件优先于默认配置

**支持的配置项：**
- `mode`: 运行模式（collect, process, visualize, export, all）
- `topics`: 要采集的话题列表
- `duration`: 采集时长（秒）
- `output`: 数据保存路径
- `sync`: 是否进行时间同步（true/false）
- `frequency`: 目标频率（用于同步和降采样）
- `format`: 导出格式（csv, json, kitti, tum）

### 配置文件示例
```yaml
# 运行模式
mode: all

# 数据采集参数
topics:
  - /scan
  - /odom
  - /imu/data
duration: 30.0

# 通用参数
output: ./data

# 预处理参数
sync: true
frequency: 10.0

# 导出参数
format: csv
```

## 技术栈

- **Python 3.8+**：核心编程语言
- **ROS2**：机器人操作系统
- **NumPy/Pandas**：数据处理库
- **Matplotlib**：数据可视化库
- **OpenCV**：图像处理库
- **PyYAML**：配置文件解析
- **tqdm**：进度条显示

## 许可证

[MIT License](LICENSE)

## 贡献

欢迎提交Issue和Pull Request！贡献流程：

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 创建Pull Request

## 故障排除

### 常见问题

1. **导入错误**：确保Python路径设置正确
   ```bash
   export PYTHONPATH=$PYTHONPATH:$PWD
   ```

2. **ROS依赖错误**：确保ROS环境已正确安装和配置
   ```bash
   source /opt/ros/humble/setup.bash
   ```

3. **权限问题**：确保有写入权限
   ```bash
   mkdir -p ./data ./processed ./visualizations ./exports
   ```

## 联系方式

- 项目主页：<repository-url>
- 问题反馈：<issues-url>
- 邮箱：<contact-email>