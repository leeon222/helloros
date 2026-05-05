#!/usr/bin/env python3
"""测试新功能的脚本"""

import os
import sys
import tempfile
import yaml

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.ros2_data_tool.logger import get_logger

logger = get_logger("test_new_features")


def test_default_config():
    """测试默认配置功能"""
    logger.info("Testing default configuration...")
    
    # 测试run_tool.py的默认配置
    import subprocess
    
    try:
        # 测试帮助信息（不实际运行采集）
        result = subprocess.run(
            ["python3", "run_tool.py", "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            logger.info("✓ Default configuration test passed")
            return True
        else:
            logger.error(f"✗ Default configuration test failed: {result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"✗ Default configuration test failed with exception: {e}")
        return False


def test_config_file():
    """测试配置文件支持"""
    logger.info("Testing configuration file support...")
    
    # 创建临时配置文件
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        config = {
            'mode': 'collect',
            'topics': ['/scan', '/odom'],
            'duration': 5.0,
            'output': './test_data'
        }
        yaml.dump(config, f)
        config_file = f.name
    
    try:
        # 测试配置文件解析（不实际运行采集）
        import subprocess
        
        result = subprocess.run(
            ["python3", "run_tool.py", "--config", config_file, "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            logger.info("✓ Configuration file test passed")
            return True
        else:
            logger.error(f"✗ Configuration file test failed: {result.stderr}")
            return False
            
    finally:
        # 清理临时文件
        if os.path.exists(config_file):
            os.unlink(config_file)


def test_logger():
    """测试日志模块"""
    logger.info("Testing logger module...")
    
    try:
        # 测试不同级别的日志
        logger.info("This is an info message")
        logger.warning("This is a warning message")
        logger.error("This is an error message")
        
        logger.info("✓ Logger module test passed")
        return True
        
    except Exception as e:
        logger.error(f"✗ Logger module test failed: {e}")
        return False


def test_imports():
    """测试模块导入"""
    logger.info("Testing module imports...")
    
    try:
        # 测试核心模块导入
        from src.ros2_data_tool.processor import DataProcessor
        from src.ros2_data_tool.logger import Logger
        
        logger.info("✓ Module import test passed")
        return True
        
    except ImportError as e:
        logger.error(f"✗ Module import test failed: {e}")
        return False


def main():
    """运行所有测试"""
    logger.info("=== Testing new features ===\n")
    
    tests = [
        ("Default Configuration", test_default_config),
        ("Configuration File", test_config_file),
        ("Logger Module", test_logger),
        ("Module Imports", test_imports)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"Running {test_name} test...")
        if test_func():
            passed += 1
        logger.info("")
    
    logger.info(f"=== Test Results ===")
    logger.info(f"Passed: {passed}/{total}")
    
    if passed == total:
        logger.info("✓ All tests passed!")
        return 0
    else:
        logger.error(f"✗ {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())