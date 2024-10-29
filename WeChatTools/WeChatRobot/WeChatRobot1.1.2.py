import time
import datetime
from wxauto import WeChat
from openai import OpenAI
from openai import RateLimitError  # 导入RateLimitError异常
import os
import random
import json


"""1.1.2更新：
收到资助！提升了回复速度和次数
优化错误返回逻辑和提示
优化结束语
优化管理员处理和指令
"""



def chat_with_kimi(user_message, role, retry_count=0 ):
    global conversation_history  # 使用全局变量来存储对话历史
    # 将用户的消息添加到对话历史中
    conversation_history.append({"role": role, "content": user_message})

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
    except Exception as e:
        return handle_error(e)#调用错误处理函数，返回错误类型


def handle_error(e, retry_count=0):
    # 将异常对象转换为字符串。我不会处理错误类型的e，这属于是解决不了错误就把错误绕开
    error_str = str(e)
    # 尝试从错误字符串中提取 'type' 和 'message'
    try:
        # 错误的开始和结束位置
        start = error_str.find("{'error':") + len("{'error':")
        end = error_str.find("}}", start)
        # 提取错误信息子字符串
        error_info = error_str[start:end]
        # 分割消息和类型
        parts = error_info.split("', 'type': '")
        message = parts[0].strip().strip("'")
        error_type = parts[1].strip().strip("'}").strip("}")
    except (ValueError, IndexError):
        # 如果提取失败，使用默认错误信息
        error_type = 'unknown_error'
        message = 'An unknown error occurred.'

    # 根据错误类型返回相应的错误描述
    if error_type == 'content_filter':
        error_message = "喵酱不想回答啦~您的输入或生成内容可能包含不安全或敏感内容喵~"
    elif error_type == 'invalid_request_error':
        if "token length too long" in message:
            error_message = "请求中的 tokens 长度过长，喵酱记不住啦~请求不要超过模型 tokens 的最长限制喵~。"
        elif "exceeded model token limit" in message:
            error_message = "呜呜 请求的 tokens 数和设置的 max_tokens 加和超过了模型规格长度喵~。让喵酱休息一下啦~"
        else:
            error_message = "请求无效，通常是您请求格式错误或者缺少必要参数。"
    elif error_type == 'invalid_authentication_error':
        error_message = "鉴权失败，请检查 API key 是否正确。"
    elif error_type == 'exceeded_current_quota_error':
        error_message = "喵酱饿了，小鱼干账户额度不足，请检查账户余额。"
    elif error_type == 'permission_denied_error':
        error_message = "您没有权限执行此操作。"
    elif error_type == 'resource_not_found_error':
        error_message = "找不到指定的资源或没有授权访问。"
    elif error_type == 'rate_limit_reached_error':
        error_message = "问得太快啦，请求触发了速率限制，请稍后再试喵~"
    elif error_type == 'engine_overloaded_error':
        error_message = "当前并发请求过多喵~节点限流中~别急别急 喵酱一个一个回答~"
    elif error_type == 'server_error':
        error_message = "内部错误，请联系管理员。"
    else:
        error_message = f"发生了一个未知错误: {message},喵酱也不知道该怎么办了"

    # 如果需要重试，可以在这里添加重试逻辑
    # 这里要改啊，error_dict用法不合适
    """if retry_count < 3:
        retry_after = error_dict.get('error', {}).get('retry_after', 1)
        print(f"Waiting {retry_after} seconds before retrying...")
        time.sleep(retry_after)
        return handle_error(error_dict, retry_count + 1)  # 递归调用，增加重试次数"""
    return error_message


def generate_cute_exit_message():
    # 这里可以定义一些可爱的退出语句，随机或按顺序选择
    exit_messages = [
        "呜~主人要离开喵酱了，我会想你的~记得下次再来找喵酱玩哦~",
        "喵~是时候说再见了，喵酱会在这里等你的~下次见喵~",
        "啊呜~主人要忙了吗？喵酱会乖乖的，期待和主人的下次相遇喵~",
        "喵喵~主人要休息了吗？喵酱也要好好休息，下次再见要更加精神哦~",
        "喵~时间过得真快，主人要离开了，喵酱会一直在这里，期待你的再次召唤~"
    ]
    # 随机选择一条退出语句
    return random.choice(exit_messages)


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
    {"role": "system", "content": "回复长度不要超过200字"},
    {"role": "system", "content": "叶哲昊是你的主人和管理员，他的昵称是Self"}

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
                    kimi_reply = chat_with_kimi(user_input , "user")
                    print(f"喵酱说: {kimi_reply}")
                    if f'{kimi_reply}' != "None":#这里是 最早的错误返回是一个None，现在虽然不再是了但是还是留着吧
                        chat.SendMsg(f'【喵酱】{kimi_reply}')
                    else:
                        chat.SendMsg('消息发得太快啦，请一会儿再试喔')
                        time.sleep(10)
                        break
                        # 此处将msg.content传递给大模型，再由大模型返回的消息回复即可实现ai聊天

            elif msg.type == 'self':
                sender = msg.sender  # 这里可以将msg.sender改为msg.sender_remark，获取备注名
                print("所有消息：", f'{sender.rjust(20)}：{msg.content}')
                # ！！！ 回复收到，此处为`chat`而不是`wx` ！！！
                if "退出" in f'{msg.content}':
                    OutBreak = 1
                    print("退出")
                    cute_exit_message = generate_cute_exit_message()
                    chat.SendMsg(cute_exit_message)
                    break
                elif "#" in f'{msg.content}':
                    if "#sys" in f'{msg.content}':
                        print("system请求")
                        user_input = f'{sender.rjust(20)}：{msg.content}'
                        kimi_reply = chat_with_kimi(user_input , "system")
                        print(f"喵酱system: {kimi_reply}")
                        if f'{kimi_reply}' != "None":  # 这里是 最早的错误返回是一个None，现在虽然不再是了但是还是留着吧
                            chat.SendMsg(f'【喵酱system】{kimi_reply}')
                        else:
                            chat.SendMsg('消息发得太快啦，请一会儿再试喔')
                            time.sleep(10)
                            break
                            # 此处将msg.content传递给大模型，再由大模型返回的消息回复即可实现ai聊天


                    else:
                        print("主人对话请求")
                        if "喵酱" in f'{msg.content}':
                            user_input = f'{sender.rjust(20)}：{msg.content}'
                            kimi_reply = chat_with_kimi(user_input , "user")
                            print(f"喵酱对主人说: {kimi_reply}")
                            if f'{kimi_reply}' != "None":  # 这里是 最早的错误返回是一个None，现在虽然不再是了但是还是留着吧
                                chat.SendMsg(f'【喵酱】{kimi_reply}')
                            else:
                                chat.SendMsg('消息发得太快啦，请一会儿再试喔')
                                time.sleep(10)
                                break
                                # 此处将msg.content传递给大模型，再由大模型返回的消息回复即可实现ai聊天




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