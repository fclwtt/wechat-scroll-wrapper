"""
核心滚动模块 - 自适应间距检测 + 精确滚动
"""
import json
import time
import sys
import os
import pyautogui
from PIL import ImageGrab

# Windows DPI 感知 - 必须在导入 pyautogui 后、使用任何坐标前调用
if sys.platform == 'win32':
    try:
        import ctypes
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass

from utils import get_config_path


class WeChatScroller:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = get_config_path()
        
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.target_x, self.target_y = self.config['target_pos']
        self.scroll_x, self.scroll_y = self.config['scroll_pos']
        self.dy_same = self.config['dy_same']
        self.dy_cross = self.config['dy_cross']
        self.probe_offset = self.config.get('probe_offset', 30)
        self.separator_color = self.config.get('separator_color', [230, 230, 230])
        self.color_tolerance = self.config.get('color_tolerance', 30)
        self.scroll_pause = self.config.get('scroll_pause', 0.3)
        self.scroll_compensation = self.config.get('scroll_compensation', 0)
        
        # 写入诊断日志
        self._log_config_loaded()
        
        # 安全设置：鼠标移到角落取消
        pyautogui.FAILSAFE = True
    
    def _log_config_loaded(self):
        """写入配置加载日志，用于诊断"""
        try:
            log_path = os.path.join(os.path.dirname(get_config_path()), 'scroll_debug.log')
            with open(log_path, 'w', encoding='utf-8') as f:
                f.write(f"Config loaded from: {get_config_path()}\n")
                f.write(f"scroll_compensation: {self.scroll_compensation}\n")
                f.write(f"dy_same: {self.dy_same}\n")
                f.write(f"dy_cross: {self.dy_cross}\n")
                f.write(f"target_pos: {self.target_x}, {self.target_y}\n")
        except Exception:
            pass  # 日志写入失败不影响主功能
    
    def get_pixel_color(self, x, y):
        """获取指定坐标的像素颜色"""
        screenshot = ImageGrab.grab(bbox=(x, y, x + 1, y + 1))
        return screenshot.getpixel((0, 0))[:3]  # RGB
    
    def is_separator_at(self, y_offset):
        """
        检测目标坐标下方 y_offset 处是否是字母分隔符
        字母分隔符背景色偏灰（~230,230,230），联系人行偏白（~255,255,255）
        """
        probe_x = self.target_x
        probe_y = self.target_y + y_offset
        
        color = self.get_pixel_color(probe_x, probe_y)
        r, g, b = color
        
        # 判断是否接近分隔符的灰色背景
        sep_r, sep_g, sep_b = self.separator_color
        is_sep = (
            abs(r - sep_r) <= self.color_tolerance and
            abs(g - sep_g) <= self.color_tolerance and
            abs(b - sep_b) <= self.color_tolerance
        )
        return is_sep
    
    def detect_scroll_amount(self):
        """
        探测下一个联系人的位置，决定滚动量
        
        策略：从目标坐标往下逐步探测
        - 如果在 dy_same 距离内检测到分隔符 → 跨字母 → 滚 dy_cross
        - 否则 → 同字母 → 滚 dy_same
        """
        # 在目标坐标下方探测分隔符
        # 探测区间：[target_y + dy_same - 20, target_y + dy_same + 20]
        probe_center = self.dy_same
        
        for offset in range(probe_center - 20, probe_center + 20, 2):
            if self.is_separator_at(offset):
                # 找到分隔符 → 下一个是跨字母
                return self.dy_cross
        
        # 没找到分隔符 → 同字母间距
        return self.dy_same
    
    def scroll(self, amount=None):
        """
        执行一次滚动
        
        Args:
            amount: 指定滚动量，None 则自动检测
        """
        if amount is None:
            amount = self.detect_scroll_amount()
        
        # 加上补偿值
        actual_amount = amount + self.scroll_compensation
        
        # 移动到滚动区域
        pyautogui.moveTo(self.scroll_x, self.scroll_y)
        time.sleep(0.1)
        
        # 执行滚动（负值=向下）
        pyautogui.scroll(-actual_amount)
        time.sleep(self.scroll_pause)
        
        scroll_type = '跨字母' if amount == self.dy_cross else '同字母'
        print(f"[滚动] amount={amount} + 补偿{self.scroll_compensation} = {actual_amount}, type={scroll_type}")
        return amount
    
    def next_contact(self):
        """滚动到下一个联系人（自动判断间距类型）"""
        return self.scroll()
    
    def update_config(self, **kwargs):
        """动态更新配置（保存到 exe 同目录）"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
            if key in self.config:
                self.config[key] = value
        
        # 持久化到 exe 同目录
        config_path = get_config_path()
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    # 仅在直接运行此脚本时执行（打包后不会触发）
    if not getattr(sys, 'frozen', False):
        scroller = WeChatScroller()
        print("滚动测试模式，按 Ctrl+C 退出")
        print(f"目标坐标: {scroller.target_x}, {scroller.target_y}")
        print(f"dy_same={scroller.dy_same}, dy_cross={scroller.dy_cross}")
        
        try:
            while True:
                input("按 Enter 滚动到下一个联系人...")
                scroller.next_contact()
        except KeyboardInterrupt:
            print("\n退出")
