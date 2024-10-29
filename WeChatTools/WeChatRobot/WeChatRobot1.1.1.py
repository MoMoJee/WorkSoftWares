import time
import datetime
from wxauto import WeChat
from openai import OpenAI
from openai import RateLimitError  # 导入RateLimitError异常
import os

"""1.1.1更新：
优化错误处理逻辑，减少无效错误处理时间
优化错误返回逻辑和提示
设置结束关键词，提供日志文件
我加了安全申明
"""

def chat_with_kimi(user_message, retry_count=0):
    global conversation_history  # 使用全局变量来存储对话历史
    # 将用户的消息添加到对话历史中
    conversation_history.append({"role": "user", "content": user_message})

    # 调用Kimi API进行聊天
    try:
        completion = client.chat.completions.create(
            model="moonshot-v1-8k",  # 你可以根据需要选择不同的模型规格
            messages=conversation_history,
            temperature=0.3,
        )

        # 将Kimi的回复添加到对话历史中
        conversation_history.append({"role": "assistant", "content": completion.choices[0].message.content})

        # 返回Kimi的回复
        return completion.choices[0].message.content
    except RateLimitError as e:
    # 尝试访问错误信息，如果不存在，则打印完整的异常信息
        error_message = e.args[0] if e.args else str(e)
        print(f"Rate limit reached. Error message: {error_message}")
        if retry_count < 3:  # 如果重试次数小于2
            wait_time = 1  # 等待1秒
            print(f"Waiting {wait_time} seconds before retrying...")
            time.sleep(wait_time)
            return chat_with_kimi(user_message, retry_count + 1)  # 递归调用，增加重试次数
        else:
            print("Max retries reached. Please try again later.")
            return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None


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
OutBreak=0#创建终止关键字
First = 1
while 1:
    if OutBreak:
        break
    msgs = wx.GetListenMessage()
    for chat in msgs:
        if First:
            chat.SendMsg('AI喵酱机器人启动！注意以下所有的【喵酱】发言都源自AI大模型，不代表本人观点，请谨慎识别喵！')
            First = 0
        if OutBreak:
            break
        one_msgs = msgs.get(chat)  # 获取消息内容
        # 回复收到
        for msg in one_msgs:
            if OutBreak:
                break
            if msg.type == 'sys':
                print(f'【系统消息】{msg.content}')
            elif msg.type == 'friend':
                sender = msg.sender  # 这里可以将msg.sender改为msg.sender_remark，获取备注名
                print("所有消息：",f'{sender.rjust(20)}：{msg.content}')
             # ！！！ 回复收到，此处为`chat`而不是`wx` ！！！
                if "喵酱" in f'{msg.content}':
                    user_input = f'{sender.rjust(20)}：{msg.content}'
                    kimi_reply = chat_with_kimi(user_input)
                    print(f"喵酱说: {kimi_reply}")
                    if f'{kimi_reply}' != "None":
                        chat.SendMsg(f'【喵酱】{kimi_reply}')
                    else:
                        chat.SendMsg('消息发得太快啦，请一会儿再试喔')
                        time.sleep(10)
                        break
                        # 此处将msg.content传递给大模型，再由大模型返回的消息回复即可实现ai聊天

            elif msg.type == 'self':
                print(f'{msg.sender.ljust(20)}：{msg.content}')
                if "退出" in f'{msg.content}':
                    print("退出")
                    OutBreak=1
                    chat.SendMsg('根据指示，喵酱先退下咯~我已经记下所有的聊天内容，期待下次再见喵~')
                    break

            elif msg.type == 'time':
                print(f'\n【时间消息】{msg.time}')

            elif msg.type == 'recall':
                print(f'【撤回消息】{msg.content}')
    print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")) # 获取当前时间并打印
    time.sleep(1)

#保存日志
# 指定要保存的文件夹路径
folder_path = 'D:\\python_learn\\WorkSoftWares\\WeChatTools\\WeChatRobot\\Logs'  # 替换为你的文件夹路径

# 确保文件夹存在
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

# 获取当前时间并格式化为字符串
current_time = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
# 构造文件名，包含时间戳
file_name = f'conversation_history_{current_time}.txt'
# 构造完整的文件路径
full_file_path = os.path.join(folder_path, file_name)

# 打开文件，准备写入
with open(full_file_path, 'w', encoding='utf-8') as file:
    # 写入文件头部信息
    file.write("Conversation History:\n")
    file.write("---------------------\n")
    # 遍历conversation_history中的每个字典
    for entry in conversation_history:
        # 将字典转换为字符串
        entry_str = f"{entry['role']}: {entry['content']}\n"
        # 写入文件
        file.write(entry_str)

print(f"日志已保存到 {full_file_path}")