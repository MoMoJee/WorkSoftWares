import tkinter as tk
from tkinter import filedialog
import json


def load_Logs_from_file():
    # 创建一个Tkinter根窗口
    root = tk.Tk()
    # 创建一个Toplevel窗口并隐藏
    top = tk.Toplevel(root)
    top.withdraw()
    # 启动事件循环
    root.update()
    # 调用文件选择对话框，允许选择多个文件
    file_paths = filedialog.askopenfilenames()
    # 将返回的元组转换为列表
    file_paths_list = list(file_paths)
    # 关闭Tkinter根窗口
    root.destroy()
    print("Files selected:", file_paths_list)
    # 检查用户是否选择了文件
    if file_paths_list:
        # 读取并返回对话历史记录
        return file_paths_list[0]


# 指定要统计的关键词
keyword = "我是小天才"

# 指定要读取的文本文件路径
file_path = load_Logs_from_file()

# 初始化计数器
keyword_count = 0

# 读取文件并统计关键词出现的次数
try:
    with open(file_path, 'r', encoding='utf-8') as file:
        for line_number, line in enumerate(file, 1):
            if keyword in line:
                keyword_count += 1
                print(f"Line {line_number}: {line.strip()}")
except FileNotFoundError:
    print("文件未找到。请检查文件路径是否正确。")
except Exception as e:
    print(f"读取文件时发生错误：{e}")

# 打印关键词出现的次数
print(f"关键词 '{keyword}' 出现了 {keyword_count} 次。")