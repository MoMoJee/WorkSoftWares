#1.1新增：
#文件选择发送功能
#优化错误提示

import tkinter as tk
from tkinter import filedialog
import pandas as pd
from wxauto import WeChat

def select_files():
    print("1 - Starting file selection")
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
    return file_paths_list

def MSGSend(msg, receiver_list):
    wx = WeChat()
    for receiver in receiver_list:
        try:
            wx.SendMsg(msg, receiver)
        except TypeError:
            continue

def FileSend(FilePathList, receiver_list):
    wx = WeChat()
    for receiver in receiver_list:
        try:
            try:
                wx.SendFiles(FilePathList, receiver)
            except TimeoutError:
                print("发送超时，请重试")
                continue
        except TypeError:
            continue

# 指定Excel文件路径
file_path = '名单.xlsx'
# 读取Excel文件的第一列
df1 = pd.read_excel(file_path, usecols=[0], header=None)
# 将第一列的数据转换为列表
receiver_list = df1[0].tolist()
# 打印名单列表
print("Receiver list:", receiver_list)

if input("请检查名单，输入密码回车发送") == "411314":
    while True:
        try:
            Mode = int(input("请输入发送模式，发送文本按1，发送文件按2，结束发送按任意数字键"))
        except ValueError:
            print("模式错误，重新输入")
            continue
        if Mode == 1:
            msg = input("文本发送模式，请输入要发送的文本")
            MSGSend(msg, receiver_list)
        elif Mode == 2:
            print("请选择要发送的文件")
            # 调用函数选择文件路径
            FilePathList = select_files()
            FileSend(FilePathList, receiver_list)
        else:
            print("结束发送")
            break
else:
    print("密码错误，发送取消")



#【群发消息】:你还未填写”光电二班麻风腮疫苗接种统计”，注意是所有人都要填写，没特殊情况的填写“是”，并在备注里填写“无”。请翻阅群置顶消息并抓紧填写
#你还没填写“光电二班国庆留校、离校登记”，看一看班级置顶消息，快快完成
#【群发消息】还未提交国家助学金申请的，尽快完成“智慧学工”网上申请。如果企业微信打不开、不方便也可以在智慧学工portal.muc.edu.cn操作，其实就是上回提交申请的那个地方。收到请回复，未提交的请同时说明