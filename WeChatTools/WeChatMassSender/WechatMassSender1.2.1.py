import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
import pandas as pd
from wxauto import WeChat
import datetime
import os

# 定义日志文件的保存目录
log_directory = "D:\python_learn\程序（杂乱）\工作软件\WeChatTools\Logs"

# 确保日志目录存在
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# 全局变量，存储日志信息
log_messages = []

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
    """选择文件，并记录日志"""
    file_paths = filedialog.askopenfilenames()
    if file_paths:
        log("选择了文件：{}".format(file_paths))
    return list(file_paths)

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
                    log("成功发送文件 {} 给：{}".format(file_path, receiver))
            if msg:
                wx.SendMsg(msg, receiver)
                log("成功发送消息给：{}".format(receiver))
        except Exception as e:
            log("发送给 {} 失败：{}".format(receiver, str(e)))


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

    # 关闭程序
    root.destroy()

def start_send():
    """开始发送操作，如果消息内容为空，则提示用户并记录日志"""
    password = entry_password.get()
    if password == "411314":
        if not var_mode_message.get() and not var_mode_file.get():
            messagebox.showinfo("提示", "请选择至少一种发送模式")
            log("未选择发送模式")
            return

        msg = entry_message.get().strip() if var_mode_message.get() else ''
        file_paths = select_files() if var_mode_file.get() else []

        if var_mode_file.get() and not file_paths:
            messagebox.showinfo("提示", "未选择文件")
            log("未选择文件")
            return

        if not msg and var_mode_message.get():
            messagebox.showwarning("警告", "消息内容不能为空")
            log("消息内容为空，发送操作已取消")
            return

        if file_paths or var_mode_message.get():
            send_files_and_message(file_paths, msg, receiver_list)
            entry_message.delete(0, tk.END)  # 发送完成后清除消息输入框
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

# 创建滚动文本框显示日志
# 在函数外定义log_text变量
log_text = scrolledtext.ScrolledText(root, width=50, height=10)
log_text.pack(pady=10)
log_text.configure(state='disabled')  # 初始化时禁用文本框状态

# 创建“结束发送”按钮
button_end_send = tk.Button(root, text="结束发送", command=save_logs_and_exit)
button_end_send.pack(side=tk.BOTTOM)

# 在主窗口初始化时调用 start_program 函数
start_program()

# 检查日志文本框是否为空，如果为空，则打印名单
if log_text.get(1.0, tk.END).strip() == '':
    log("接收者列表：")
    for receiver in receiver_list:
        log(f"{receiver}")

# 运行主循环
root.mainloop()