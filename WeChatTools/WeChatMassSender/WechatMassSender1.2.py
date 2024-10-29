#1.2更新内容：
"""
给不同的人发送不同的信息
分开读取excel不同列
UI界面：
    展示名单，可拖动文件输入
    解决了NaN问题
"""
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pandas as pd
from wxauto import WeChat

def select_files():
    file_paths = filedialog.askopenfilenames()
    return list(file_paths)

def MSGSend(msg, receiver_list):
    wx = WeChat()
    for receiver in receiver_list:
        try:
            wx.SendMsg(msg, receiver)
        except Exception as e:
            messagebox.showerror("发送失败", str(e))

def send_files_and_message(file_paths, msg, receiver_list):
    wx = WeChat()
    for receiver in receiver_list:
        try:
            # 发送文件
            for file_path in file_paths:
                wx.SendFiles([file_path], receiver)
            # 发送文字
            if msg:
                wx.SendMsg(msg, receiver)
            messagebox.showinfo("发送成功", "文件和消息已成功发送给：{}".format(receiver))
        except Exception as e:
            messagebox.showerror("发送失败", str(e))

def start_send():
    password = entry_password.get()
    if password == "411314":
        if not var_mode_message.get() and not var_mode_file.get():
            messagebox.showinfo("提示", "请选择至少一种发送模式")
            return

        msg = entry_message.get() if var_mode_message.get() else ''
        file_paths = select_files() if var_mode_file.get() else []

        if var_mode_file.get() and not file_paths:
            messagebox.showinfo("提示", "未选择文件")
            return

        if file_paths or var_mode_message.get():
            send_files_and_message(file_paths, msg, receiver_list)
            # 发送完成后清除消息输入框
            entry_message.delete(0, tk.END)
        else:
            messagebox.showinfo("结束", "结束发送")
    else:
        messagebox.showerror("错误", "密码错误，发送取消")

def toggle_message_entry():
    if var_mode_message.get():
        entry_message.configure(state='normal')
    else:
        entry_message.configure(state='disabled')

# 读取Excel文件的第一列，去除NaN值
file_path = '名单.xlsx'
df1 = pd.read_excel(file_path, usecols=[0], header=None).dropna()
receiver_list = df1[0].astype(str).tolist()

# 创建主窗口
root = tk.Tk()
root.title("微信自动发送工具")

# 创建密码输入框
label_password = tk.Label(root, text="密码:")
label_password.pack()
entry_password = tk.Entry(root, show="*")
entry_password.pack()

# 创建模式选择变量
var_mode_message = tk.BooleanVar()
var_mode_file = tk.BooleanVar()

# 创建消息输入框
label_message = tk.Label(root, text="消息内容:")
label_message.pack()
entry_message = tk.Entry(root)
entry_message.pack()

# 创建发送模式的复选按钮
check_message = tk.Checkbutton(root, text="发送文本", variable=var_mode_message, command=toggle_message_entry)
check_message.pack()
check_file = tk.Checkbutton(root, text="发送文件", variable=var_mode_file)
check_file.pack()

# 初始化消息输入框的状态
toggle_message_entry()

# 创建发送按钮
button_send = tk.Button(root, text="发送", command=start_send)
button_send.pack()

# 创建滚动文本框显示发送人名单
scrolled_text = scrolledtext.ScrolledText(root, width=50, height=10)
scrolled_text.pack()
scrolled_text.insert(tk.END, '\n'.join(receiver_list))
scrolled_text.configure(state='disabled')

# 运行主循环
root.mainloop()