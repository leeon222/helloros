# Ubuntu系统集成测试指南

## 测试环境要求
- Ubuntu 20.04 LTS或Ubuntu 22.04 LTS
- ROS2 Humble（Ubuntu 22.04）或ROS2 Noetic（Ubuntu 20.04）
- Python 3.8+
- 所有必需的Python依赖

## 测试步骤

### 1. 环境准备
```bash
# 安装依赖
chmod +x install_ubuntu.sh
./install_ubuntu.sh

# 使环境变量生效
source ~/.bashrc

# 确保ROS2环境已设置
source /opt/ros/humble/setup.bash  # Ubuntu 22.04
# 或
source /opt/ros/noetic/setup.bash  # Ubuntu 20.04
```

### 2. 单元测试
```bash
# 运行测试脚本
python3 test_tool.py
```

### 3. 功能测试

#### 3.1 数据采集测试
```bash
# 启动ROS2节点（使用模拟器或真实设备）
# 例如：ros2 launch gazebo_ros gazebo.launch.py

# 测试数据采集
python3 run_tool.py --mode collect --topics /scan /odom /imu/data --duration 10
```

#### 3.2 数据预处理测试
```bash
# 测试预处理功能
python3 run_tool.py --mode process --input ./data --sync --frequency 10
```

#### 3.3 数据可视化测试
```bash
# 测试可视化功能
python3 run_tool.py --mode visualize --input ./processed
```

#### 3.4 数据导出测试
```bash
# 测试各种格式导出
python3 run_tool.py --mode export --input ./processed --format csv
python3 run_tool.py --mode export --input ./processed --format json
python3 run_tool.py --mode export --input ./processed --format kitti
python3 run_tool.py --mode export --input ./processed --format tum
```

### 4. 完整流程测试
```bash
# 测试完整流程（采集→预处理→可视化→导出）
python3 run_tool.py --mode all --topics /scan /odom /imu/data --duration 30 --sync --frequency 10 --format csv
```

### 5. Launch文件测试
```bash
# 测试launch文件
ros2 launch launch/ros2_data_tool.launch.py

# 测试带参数的launch
ros2 launch launch/ros2_data_tool.launch.py topics:="/scan /odom /imu/data" duration:=30.0 sync:=true frequency:=10.0
```

## 验证标准

### 1. 成功标准
- 所有测试脚本执行成功，无错误
- 数据采集能够正确保存数据文件
- 预处理后的数据格式正确
- 可视化能够正常显示图表
- 导出的文件格式符合规范
- Launch文件能够正常启动

### 2. 性能要求
- 数据采集延迟 < 100ms
- 预处理速度 > 1000条/秒
- 内存使用 < 2GB（处理1GB数据）

### 3. 兼容性验证
- Ubuntu 20.04 + ROS2 Noetic: 所有功能正常
- Ubuntu 22.04 + ROS2 Humble: 所有功能正常

## 故障排除

### 常见问题
1. **导入错误**
   - 检查Python路径：`echo $PYTHONPATH`
   - 确保项目根目录已添加到PYTHONPATH

2. **ROS2依赖错误**
   - 确保ROS2环境已正确设置：`source /opt/ros/{distro}/setup.bash`
   - 检查rclpy版本：`pip3 show rclpy`

3. **权限问题**
   - 确保有写入权限：`mkdir -p ./data ./processed ./visualizations ./exports`

4. **依赖缺失**
   - 重新运行安装脚本：`./install_ubuntu.sh`
   - 手动安装缺失的包：`pip3 install <package>`

## 测试报告模板

```
# Ubuntu系统集成测试报告

## 测试环境
- Ubuntu版本: [20.04/22.04]
- ROS2版本: [Noetic/Humble]
- Python版本: [3.8+]

## 测试结果

### 单元测试
- [ ] 测试脚本通过

### 功能测试
- [ ] 数据采集功能正常
- [ ] 数据预处理功能正常
- [ ] 数据可视化功能正常
- [ ] 数据导出功能正常

### 完整流程测试
- [ ] 完整流程执行成功

### Launch文件测试
- [ ] Launch文件正常启动
- [ ] 参数传递正确

## 性能测试
- 数据采集延迟: [ms]
- 预处理速度: [条/秒]
- 内存使用: [GB]

## 问题记录
1. [问题描述] - [解决方案]
2. [问题描述] - [解决方案]

## 结论
[通过/失败] - [总结]
```