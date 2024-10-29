"""
1.2.2更新

1.2.2待优化
有个Bug，拖入文件时，由于调用的update_file_list函数包含select_files，会导致弹出一个选择文件界面，直接关掉就行
"""


import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from tkinterdnd2 import DND_FILES, TkinterDnD
import pandas as pd
from wxauto import WeChat
import datetime
import os

# 定义日志文件的保存目录
log_directory = "D:\\python_learn\\WorkSoftWares\\WeChatTools\\WeChatMassSender\\Logs"

# 确保日志目录存在
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# 全局变量，存储日志信息
log_messages = []
# 全局变量，存储选中的文件路径
selected_files = []

def log(message):
    """将日志信息追加到日志文本框和全局变量中"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # 获取当前时间
    log_entry = f"[{timestamp}] {message}"  # 格式化日志信息，包含时间戳
    log_messages.append(log_entry)
    log_text.configure(state='normal')  # 启用文本框状态
    log_text.insert(tk.END, log_entry + "\n")
    log_text.see(tk.END)  # 自动滚动到最新日志
    log_text.configure(state='disabled')  # 禁用文本框状态，防止用户编辑

def select_files():
    """选择文件，并保存路径到全局变量"""
    file_paths = filedialog.askopenfilenames()
    if file_paths:
        selected_files.extend(file_paths)  # 保存选择的文件路径
        log("选择了文件：{}".format(file_paths))

        # 更新显示将被发送的文件的文本框
        entry_files.delete('1.0', tk.END)  # 清空文本框
        for file_path in selected_files:
            entry_files.insert(tk.END, file_path + "\n")  # 显示文件路径

    return selected_files

def on_drop(event):
    """处理拖放的文件"""
    file_paths = root.tk.splitlist(event.data)
    if not selected_files:  # 如果 selected_files 为空，则直接添加
        selected_files.extend(file_paths)
    else:  # 如果 selected_files 不为空，则添加到列表末尾
        selected_files.extend(file_paths)
    update_file_list()  # 更新文本框内容
    log(f"拖放了文件：{file_paths}")

def MSGSend(msg, receiver_list):
    """发送消息，并记录成功或失败的日志"""
    wx = WeChat()
    for receiver in receiver_list:
        try:
            wx.SendMsg(msg, receiver)
            log("成功发送消息给：{}".format(receiver))
        except Exception as e:
            log("发送消息给 {} 失败：{}".format(receiver, str(e)))

def send_files_and_message(file_paths, msg, receiver_list):
    """发送文件和消息，并记录日志"""
    wx = WeChat()
    for receiver in receiver_list:
        try:
            if file_paths:
                for file_path in file_paths:
                    wx.SendFiles([file_path], receiver)
                    log(f"成功发送文件 {file_path} 给：{receiver}")
            if msg:
                wx.SendMsg(msg, receiver)
                log(f"成功发送消息给：{receiver}")
        except Exception as e:
            log(f"发送给 {receiver} 失败：{e}")

# 更新全局变量 selected_files 并显示在 entry_files 文本框中
def update_file_list():
    """更新选中的文件列表并显示"""
    global selected_files
    selected_files = select_files()
    entry_files.delete('1.0', tk.END)  # 清空文本框
    for file_path in selected_files:
        entry_files.insert(tk.END, file_path + "\n")

def save_logs_and_exit():
    """将日志保存到以时间命名的文件，并退出程序"""
    # 获取当前时间作为日志文件名
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_filename = f"log_{timestamp}.txt"
    log_path = os.path.join(log_directory, log_filename)  # 组合日志目录和文件名

    # 将日志信息保存到文件
    with open(log_path, "w") as log_file:
        for line in log_messages:
            log_file.write(line + "\n")
        log_file.write("程序停止运行\n")

    # 关闭程序
    root.destroy()


def start_send():
    global selected_files  # 声明 selected_files 为全局变量
    """开始发送操作，如果消息内容为空，则提示用户并记录日志"""
    password = entry_password.get()
    if password == "411314":
        if not var_mode_message.get() and not var_mode_file.get():
            messagebox.showinfo("提示", "请选择至少一种发送模式")
            log("未选择发送模式")
            return

        msg = entry_message.get('1.0', 'end').strip() if var_mode_message.get() else ''

        # 如果选择了发送文件模式但selected_files为空，则让用户选择文件
        if var_mode_file.get() and not selected_files:
            # 只有当没有文件被拖放时，才显示文件选择对话框
            if not entry_files.get('1.0', 'end').strip():
                selected_files = select_files()
                if not selected_files:
                    messagebox.showinfo("提示", "未选择文件")
                    log("未选择文件")
                    return
            else:
                log("已通过拖放选择了文件")

        # 如果消息模式被选中但消息框为空，则提示用户
        if not msg and var_mode_message.get():
            messagebox.showwarning("警告", "消息内容不能为空")
            log("消息内容为空，发送操作已取消")
            return

        # 发送文件和/或消息
        file_paths_to_send = selected_files if var_mode_file.get() else []
        if file_paths_to_send or msg:
            send_files_and_message(file_paths_to_send, msg, receiver_list)
            entry_message.delete('1.0', 'end')  # 发送完成后清除消息输入框
        else:
            log("发送操作已取消")
    else:
        messagebox.showerror("错误", "密码错误，发送取消")
        log("密码错误，发送取消")

def toggle_message_entry():
    """根据是否选择发送文本切换消息输入框的状态"""
    if var_mode_message.get():
        entry_message.configure(state='normal')
    else:
        entry_message.configure(state='disabled')

def start_program():
    """在程序开始时添加日志开头的分隔线和时间戳"""
    start_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log("程序开始运行")
    log("-" * 50)  # 添加分隔线
    log(f"开始时间：{start_time}")

def clear_files():
    """清空文件列表，更新文本框，并创建日志"""
    global selected_files
    selected_files.clear()  # 清空文件路径列表
    entry_files.delete('1.0', tk.END)  # 清空文本框
    log("清空了所有待发送的文件")

# 读取Excel文件的第一列，去除NaN值
file_path = "D:\\python_learn\\WorkSoftWares\\WeChatTools\\WeChatMassSender\\名单.xlsx"
df1 = pd.read_excel(file_path, usecols=[0], header=None).dropna()
receiver_list = df1[0].astype(str).tolist()

# 创建主窗口
root = TkinterDnD.Tk()
root.title("微信批量私发助手1.2.2")

# 创建密码输入框
label_password = tk.Label(root, text="密码:")
label_password.pack()
entry_password = tk.Entry(root, show="*")
entry_password.pack()

# 创建模式选择变量
var_mode_message = tk.BooleanVar()
var_mode_file = tk.BooleanVar()

# 创建消息输入框的标签
label_message = tk.Label(root, text="消息内容:")
label_message.pack()
# 创建一个更大的消息输入框，使用Text控件
entry_message = tk.Text(root, height=10, width=50)
entry_message.pack()

# 创建用于放置复选框的框架
frame_checkboxes = tk.Frame(root)
frame_checkboxes.pack(side=tk.TOP)
# 创建发送模式的复选按钮
var_mode_message = tk.BooleanVar()
check_message = tk.Checkbutton(frame_checkboxes, text="发送文本", variable=var_mode_message, command=toggle_message_entry)
check_message.pack(side=tk.LEFT)
var_mode_file = tk.BooleanVar()
check_file = tk.Checkbutton(frame_checkboxes, text="发送文件", variable=var_mode_file)
check_file.pack(side=tk.LEFT)

# 初始化消息输入框的状态
toggle_message_entry()

# 创建用于放置按钮的框架
frame_buttons = tk.Frame(root)
frame_buttons.pack(side=tk.TOP)
# 创建“选择文件”按钮
button_select_files = tk.Button(frame_buttons, text="选择文件", command=update_file_list)
button_select_files.pack(side=tk.LEFT)
# 创建“清空文件”按钮
button_clear_files = tk.Button(frame_buttons, text="清空文件", command=clear_files)
button_clear_files.pack(side=tk.LEFT)

# 创建发送按钮
button_send = tk.Button(root, text="发送", command=start_send)
button_send.pack()

# 创建一个文本框用来显示将被发送的文件
label_files = tk.Label(root, text="将被发送的文件（也可以将文件拖动到此）:")
label_files.pack()
entry_files = tk.Text(root, height=5, width=80)
entry_files.pack()
# 注册拖放目标
entry_files.drop_target_register(DND_FILES)
entry_files.dnd_bind('<<Drop>>', on_drop)

# 创建滚动文本框显示日志
# 在函数外定义log_text变量
log_text = scrolledtext.ScrolledText(root, width=80, height=20)
log_text.pack(pady=10)
log_text.configure(state='disabled')  # 初始化时禁用文本框状态

# 创建“结束发送”按钮
button_end_send = tk.Button(root, text="结束发送并退出", command=save_logs_and_exit)
button_end_send.pack(side=tk.BOTTOM)

# 检查日志文本框是否为空，如果为空，则打印名单
if log_text.get(1.0, tk.END).strip() == '':
    log("接收者列表：")
    for receiver in receiver_list:
        log(f"{receiver}")

# 在主窗口初始化时调用 start_program 函数
start_program()

# 运行主循环
root.mainloop()