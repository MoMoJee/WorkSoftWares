from wxauto import WeChat
import pandas as pd








# 指定Excel文件路径
file_path = '名单.xlsx'

# 读取Excel文件的第一列
df1 = pd.read_excel(file_path, usecols=[0], header=None)

# 将第一列的数据转换为列表
receiver_list = df1[0].tolist()

# 打印名单列表
print(receiver_list)

if input("请检查名单，输入密码回车发送")=="411314":

# 发送消息
    for receiver in receiver_list:
        wx = WeChat()
        wx.SendMsg('注意！审核人写张天华老师', receiver)
else:
    print("密码错误，发送取消")


#【群发消息】:你还未填写”光电二班麻风腮疫苗接种统计”，注意是所有人都要填写，没特殊情况的填写“是”，并在备注里填写“无”。请翻阅群置顶消息并抓紧填写
#你还没填写“光电二班国庆留校、离校登记”，看一看班级置顶消息，快快完成
#【群发消息】还未提交国家助学金申请的，尽快完成“智慧学工”网上申请。如果企业微信打不开、不方便也可以在智慧学工portal.muc.edu.cn操作，其实就是上回提交申请的那个地方。收到请回复，未提交的请同时说明