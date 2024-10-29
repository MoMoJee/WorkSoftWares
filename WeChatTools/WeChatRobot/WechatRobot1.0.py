import time
import datetime
from wxauto import WeChat
from openai import OpenAI


def chat_with_kimi(user_message):
    global conversation_history  # 使用全局变量来存储对话历史

    # 将用户的消息添加到对话历史中
    conversation_history.append({"role": "user", "content": user_message})

    # 调用Kimi API进行聊天
    completion = client.chat.completions.create(
        model="moonshot-v1-8k",  # 你可以根据需要选择不同的模型规格
        messages=conversation_history,
        temperature=0.3,
    )

    # 将Kimi的回复添加到对话历史中
    conversation_history.append({"role": "assistant", "content": completion.choices[0].message.content})

    # 返回Kimi的回复
    return completion.choices[0].message.content


#AI接口接入部分
# 请将这里的字符串替换为你从Kimi开放平台申请的API Key
api_key = "sk-kIeW7aynlZvF7n2DFjkU6JA5GKNgTDqXt9yKsCRPrLfjKJkR"
client = OpenAI(
    api_key=api_key,
    base_url="https://api.moonshot.cn/v1",
)
# 初始化对话上下文，键入对话前提
conversation_history = [
    {"role": "system", "content": "请自然对话，你现在的角色是可爱的猫娘，名字机器喵酱"},
    {"role": "system", "content": "我会传给你带有昵称、消息内容的一个字符串，请根据此回复"},
    {"role": "system", "content": "回复长度不要超过200字"}
]


#微信接入
wx = WeChat()
# 首先设置一个监听列表，列表元素为指定好友（或群聊）的昵称
listen_list = ["五号楼花果山"]
# 然后调用`AddListenChat`方法添加监听对象，其中可选参数`savepic`为是否保存新消息图片
for i in listen_list:
    wx.AddListenChat(who=i)
#无限循环
while 1:
    msgs = wx.GetListenMessage()
    for chat in msgs:
        one_msgs = msgs.get(chat)  # 获取消息内容

        # 回复收到
        for msg in one_msgs:
            if msg.type == 'sys':
                print(f'【系统消息】{msg.content}')

            elif msg.type == 'friend':
                sender = msg.sender  # 这里可以将msg.sender改为msg.sender_remark，获取备注名
                print(f'{sender.rjust(20)}：{msg.content}')
                # ！！！ 回复收到，此处为`chat`而不是`wx` ！！！
                user_input = f'{sender.rjust(20)}：{msg.content}'
                kimi_reply = chat_with_kimi(user_input)
                print(f"Kimi says: {kimi_reply}")

                chat.SendMsg(f'{kimi_reply}')
                # 此处将msg.content传递给大模型，再由大模型返回的消息回复即可实现ai聊天

            elif msg.type == 'self':
                print(f'{msg.sender.ljust(20)}：{msg.content}')

            elif msg.type == 'time':
                print(f'\n【时间消息】{msg.time}')

            elif msg.type == 'recall':
                print(f'【撤回消息】{msg.content}')
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) # 获取当前时间并打印
    time.sleep(1)

