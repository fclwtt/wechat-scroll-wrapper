"""
校准工具 - 一次性测量 dy_same 和 dy_cross
运行后按提示操作，结果自动保存到 config.json
"""
import json
import time
import sys
import os
import pyautogui
from PIL import ImageGrab

# Windows DPI 感知
if sys.platform == 'win32':
    try:
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

from utils import get_config_path, get_base_dir


def get_pixel_color(x, y):
    """获取指定坐标的像素颜色"""
    screenshot = ImageGrab.grab(bbox=(x, y, x + 1, y + 1))
    return screenshot.getpixel((0, 0))[:3]


def measure_scroll_distance():
    """
    测量两次滚动之间的距离
    用户手动滚动鼠标滚轮，脚本记录鼠标位置变化
    """
    print("请将鼠标移到当前联系人头像位置")
    input("准备好后按 Enter...")
    
    pos1 = pyautogui.position()
    print(f"位置1: {pos1}")
    
    print("\n现在请手动滚动鼠标滚轮，让下一个联系人移到相同位置")
    print("（滚动到合适位置后，将鼠标移到新联系人头像位置）")
    input("完成后按 Enter...")
    
    pos2 = pyautogui.position()
    print(f"位置2: {pos2}")
    
    # 计算 Y 轴距离
    distance = abs(pos2.y - pos1.y)
    return distance


def detect_separator_color():
    """检测字母分隔符的背景色"""
    print("\n=== 检测字母分隔符颜色 ===")
    print("请将鼠标移到字母分隔符（如 A、B、C）的背景区域")
    input("准备好后按 Enter...")
    
    pos = pyautogui.position()
    color = get_pixel_color(pos.x, pos.y)
    print(f"分隔符颜色: RGB{color}")
    return color


def calibrate():
    """主校准流程"""
    print("=" * 50)
    print("微信通讯录滚动校准工具")
    print("=" * 50)
    
    config_path = get_config_path()
    
    # 加载现有配置
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except FileNotFoundError:
        config = {}
    
    # Step 1: 设置目标坐标
    print("\n【步骤 1/4】设置目标坐标")
    print("目标坐标 = 联系人头像应该对齐到的屏幕位置")
    print("请将鼠标移到第一个联系人的头像中心位置")
    input("准备好后按 Enter...")
    
    target_pos = pyautogui.position()
    config['target_pos'] = [target_pos.x, target_pos.y]
    print(f"✓ 目标坐标: {target_pos.x}, {target_pos.y}")
    
    # Step 2: 设置滚动区域
    print("\n【步骤 2/4】设置滚动区域")
    print("滚动区域 = 鼠标滚轮操作的位置（联系人列表区域内任意位置）")
    print("请将鼠标移到联系人列表区域内")
    input("准备好后按 Enter...")
    
    scroll_pos = pyautogui.position()
    config['scroll_pos'] = [scroll_pos.x, scroll_pos.y]
    print(f"✓ 滚动位置: {scroll_pos.x}, {scroll_pos.y}")
    
    # Step 3: 测量同字母间距
    print("\n【步骤 3/4】测量同字母间距 (dy_same)")
    print("请找到同一字母下的两个连续联系人（如 H 下的 豪哥2号 和 后来）")
    print("如果没有同字母的联系人，可以跳过（使用默认值 56）")
    
    choice = input("是否现在测量？(y/n，默认 n): ").strip().lower()
    if choice == 'y':
        dy_same = measure_scroll_distance()
        config['dy_same'] = dy_same
        print(f"✓ dy_same = {dy_same} 像素")
    else:
        dy_same = config.get('dy_same', 56)
        print(f"使用默认值: dy_same = {dy_same}")
    
    # Step 4: 测量跨字母间距
    print("\n【步骤 4/4】测量跨字母间距 (dy_cross)")
    print("请找到相邻两个字母组的联系人（如 A 下的联系人 → B 下的联系人）")
    
    choice = input("是否现在测量？(y/n，默认 n): ").strip().lower()
    if choice == 'y':
        dy_cross = measure_scroll_distance()
        config['dy_cross'] = dy_cross
        print(f"✓ dy_cross = {dy_cross} 像素")
    else:
        dy_cross = config.get('dy_cross', 88)
        print(f"使用默认值: dy_cross = {dy_cross}")
    
    # 可选：检测分隔符颜色
    print("\n【可选】检测字母分隔符颜色")
    choice = input("是否检测？(y/n，默认 n): ").strip().lower()
    if choice == 'y':
        sep_color = detect_separator_color()
        config['separator_color'] = list(sep_color)
        print(f"✓ 分隔符颜色: {sep_color}")
    
    # 保存配置到 exe 同目录
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, ensure_ascii=False, indent=4)
    
    print("\n" + "=" * 50)
    print(f"✓ 校准完成！配置已保存到: {config_path}")
    print("=" * 50)
    print(f"\n配置摘要:")
    print(f"  目标坐标: {config['target_pos']}")
    print(f"  滚动位置: {config['scroll_pos']}")
    print(f"  dy_same (同字母): {config.get('dy_same', '未设置')}")
    print(f"  dy_cross (跨字母): {config.get('dy_cross', '未设置')}")
    print(f"  分隔符颜色: {config.get('separator_color', '未设置')}")
    print("\n现在可以运行 WeChatScroller.exe 启动滚动按钮了")


if __name__ == '__main__':
    print("提示：校准前请先打开微信通讯录管理页面")
    print("并将窗口调整到最终使用时的位置和大小\n")
    
    input("按 Enter 开始校准...")
    calibrate()
