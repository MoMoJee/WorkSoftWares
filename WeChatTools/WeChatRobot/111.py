import threading
import queue
import time
import datetime
from wxauto import WeChat
from openai import OpenAI
from openai import RateLimitError  # 导入RateLimitError异常
import os



# 创建一个线程安全的队列
message_queue = queue.Queue()

# 全局变量来存储对话历史和控制循环的变量
conversation_history = [
    {"role": "system", "content": "请自然对话，你现在的角色是可爱的猫娘，名字机器喵酱"},
    {"role": "system", "content": "我会传给你带有昵称、消息内容的一个字符串，请根据此回复"},
    {"role": "system", "content": "回复长度不要超过200字"},
    {"role": "system", "content": "林蒙力是你的同事"}
]
OutBreak = 0
First = 1

#微信接入
wx = WeChat()
# 首先设置一个监听列表，列表元素为指定好友（或群聊）的昵称
listen_list = ["文件传输助手"]
# 然后调用`AddListenChat`方法添加监听对象，其中可选参数`savepic`为是否保存新消息图片
for i in listen_list:
    wx.AddListenChat(who=i)
#无限循环

# 定义 chat_with_kimi 函数
def chat_with_kimi(user_message, retry_count=0):
    global conversation_history
    try:
        completion = client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=conversation_history,
            temperature=0.3,
        )
        conversation_history.append({"role": "assistant", "content": completion.choices[0].message.content})
        return completion.choices[0].message.content
    except RateLimitError as e:
        error_message = e.args[0] if e.args else str(e)
        print(f"Rate limit reached. Error message: {error_message}")
        if retry_count < 3:
            wait_time = 1  # 可以根据API的具体建议调整等待时间
            print(f"Waiting {wait_time} seconds before retrying...")
            time.sleep(wait_time)
            return chat_with_kimi(user_message, retry_count + 1)
        else:
            print("Max retries reached. Please try again later.")
            return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

# 定义处理消息的消费者线程函数
def process_messages(wx, chat):
    while True:
        try:
            # 获取队列中的消息，设置超时时间避免线程阻塞
            msg_data = message_queue.get(timeout=3)
            if msg_data is None:
                break  # 如果收到结束信号，则退出循环

            sender, msg, chat = msg_data

            # 打印消息
            print("所有消息：", f'{sender.rjust(20)}：{msg}')

            # 检查是否包含“喵酱”关键字
            if "喵酱" in msg:
                user_input = f'{sender.rjust(20)}：{msg}'
                kimi_reply = chat_with_kimi(user_input)
                print(f"喵酱说: {kimi_reply}")
                if kimi_reply:
                    chat.SendMsg(f'【喵酱】{kimi_reply}')
                    time.sleep(2)
                else:
                    chat.SendMsg('消息发得太快啦，请一会儿再试喔')
                    time.sleep(20)
            elif "退出" in msg:
                print("退出")
                message_queue.put(None)  # 发送结束信号给其他线程
                chat.SendMsg('根据指示，喵酱先退下咯~我已经记下所有的聊天内容，期待下次再见喵~')
                break
            else:
                print(f'{msg.sender.ljust(20)}：{msg.content}')

        except queue.Empty:
            print("No messages to process.")
            break
        finally:
            message_queue.task_done()


# 定义生产者线程函数
def listen_for_messages(wx, chat):
    global First
    while not OutBreak:
        msgs = wx.GetListenMessage()
        for chat in msgs:
            if First:
                chat.SendMsg('AI喵酱机器人启动！注意以下所有的【喵酱】发言都源自AI大模型，不代表本人观点，请谨慎识别喵！')
                First = 0
            if OutBreak:
                break
            one_msgs = msgs.get(chat)  # 获取消息内容
            for msg in one_msgs:
                if OutBreak:
                    break
                # 将消息发送者、消息内容和聊天对象放入队列
                message_queue.put((msg.sender, msg.content, chat))

        print(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))  # 获取当前时间并打印
        time.sleep(1)


# 创建并启动消费者线程
consumer_thread = threading.Thread(target=process_messages, args=(wx, chat))
consumer_thread.start()

# 创建并启动生产者线程
producer_thread = threading.Thread(target=listen_for_messages, args=(wx, chat))
producer_thread.start()

# 等待队列中的所有消息被处理
message_queue.join()

# 等待消费者线程结束
consumer_thread.join()

# 发送结束信号给生产者线程
message_queue.put(None)