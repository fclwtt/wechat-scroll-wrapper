"""
悬浮按钮 - 点击一次 = 滚动一次
你的点击工具在发完消息后，点击这个按钮即可触发滚动
"""
import tkinter as tk
import json
import os
import threading
from scroller import WeChatScroller


class ScrollButton:
    def __init__(self):
        # 加载配置
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = json.load(f)
        
        self.scroller = WeChatScroller(config_path)
        self.scroll_count = 0
        
        # 创建悬浮窗口
        self.root = tk.Tk()
        self.root.title("滚动控制")
        self.root.attributes('-topmost', True)  # 始终置顶
        self.root.attributes('-alpha', 0.9)     # 轻微透明
        self.root.resizable(False, False)
        
        # 窗口大小和位置
        btn_w = self.config.get('button_width', 120)
        btn_h = self.config.get('button_height', 50)
        btn_x = self.config.get('button_x', 100)
        btn_y = self.config.get('button_y', 100)
        
        self.root.geometry(f"{btn_w}x{btn_h}+{btn_x}+{btn_y}")
        
        # 按钮样式
        self.button = tk.Button(
            self.root,
            text="下一步\n(点击滚动)",
            font=("Microsoft YaHei", 11, "bold"),
            bg="#4CAF50",
            fg="white",
            activebackground="#45a049",
            activeforeground="white",
            relief=tk.FLAT,
            cursor="hand2",
            command=self.on_click
        )
        self.button.pack(fill=tk.BOTH, expand=True)
        
        # 状态栏
        self.status_var = tk.StringVar(value="就绪 | 已滚动: 0")
        status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            font=("Microsoft YaHei", 8),
            fg="#666",
            bg="#f0f0f0"
        )
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
        # 绑定快捷键
        self.root.bind('<space>', lambda e: self.on_click())
        self.root.bind('<Escape>', lambda e: self.root.destroy())
        
        # 窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        
        print("=" * 40)
        print("滚动按钮已启动")
        print(f"按钮位置: ({btn_x}, {btn_y})")
        print(f"按钮大小: {btn_w} x {btn_h}")
        print(f"目标坐标: {self.scroller.target_x}, {self.scroller.target_y}")
        print(f"dy_same={self.scroller.dy_same}, dy_cross={self.scroller.dy_cross}")
        print("=" * 40)
        print("提示：让你的点击工具点击这个按钮即可触发滚动")
        print("按 Space 也可手动触发 | Esc 退出")
    
    def on_click(self):
        """按钮被点击（由点击工具或手动触发）"""
        self.scroll_count += 1
        
        # 视觉反馈：按钮变黄
        self.button.config(bg="#FFC107", text=f"滚动中... #{self.scroll_count}")
        self.root.update()
        
        try:
            # 执行滚动
            amount = self.scroller.next_contact()
            
            # 更新状态
            self.status_var.set(f"已滚动: {self.scroll_count} | 上次: {amount}px")
            
        except Exception as e:
            self.status_var.set(f"错误: {str(e)[:20]}")
            print(f"[错误] {e}")
        
        # 恢复按钮
        self.button.config(bg="#4CAF50", text=f"下一步\n(点击滚动)")
        self.root.update()
    
    def on_close(self):
        """关闭窗口"""
        print(f"\n共滚动 {self.scroll_count} 次")
        self.root.destroy()
    
    def run(self):
        """启动主循环"""
        self.root.mainloop()


if __name__ == '__main__':
    app = ScrollButton()
    app.run()
