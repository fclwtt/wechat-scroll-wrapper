"""
工具函数 - PyInstaller 兼容的路径处理
"""
import sys
import os


def get_base_dir():
    """
    获取程序所在目录（兼容 PyInstaller 打包）
    
    - 开发模式: 返回脚本所在目录
    - PyInstaller --onefile: 返回 exe 所在目录（不是临时解压目录）
    """
    if getattr(sys, 'frozen', False):
        # PyInstaller 打包后，sys.executable 是 exe 路径
        return os.path.dirname(sys.executable)
    else:
        # 开发模式，返回脚本所在目录
        return os.path.dirname(os.path.abspath(__file__))


def get_config_path():
    """获取 config.json 的完整路径（exe 同目录）"""
    return os.path.join(get_base_dir(), 'config.json')
