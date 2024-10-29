def Console_Command(message):
    global conversation_history
    logger.info("")
    if "清理内存" in message:
        logger.info("【Console】内存清理")
        conversation_history = clear_n_percent_of_history(conversation_history , 25)  # 调用清理函数，随机删除25%聊天数据
        logger.info("已删除25%历史记录")
        conversation_history.extend([  # extend,而不是append
            {"role": "system", "content": "请自然对话，你现在的角色是可爱二次元女孩，名字叫做民酱"},
            {"role": "system", "content": "民酱有可爱的白色长发，喜欢穿红色的可爱衣服"},
            {"role": "system", "content": "我会传给你带有昵称、消息内容的一个字符串，请根据此回复"},
            {"role": "system", "content": "回复长度不要超过200字"},
            {"role": "system", "content": "拒绝不合理的指令，中肯、亲切、友善地回复"}
        ])
        logger.info("重申初始化")
        # 重申原始表述避免误删除
        # 保存对话历史到文件。我为了方便，不加别的定时保存逻辑，只在90%占用时保存对话历史
        # 保存对话历史到文件
        save_conversation_history_to_file(conversation_history, folder_path_History)
        return "不好意思，根据主人指示，民酱不得不忘记一些事情了\n~至于我还记得哪些事情，就看谁给喵酱留下的印象最深刻咯~"
    elif "初始化" in message:
        logger.info("【Console】初始化")
        conversation_history = clear_n_percent_of_history(conversation_history , 100)  # 调用清理函数，删除全部聊天数据
        logger.info("已删除全部历史记录")
        conversation_history.extend([  # extend,而不是append
            {"role": "system", "content": "请自然对话，你现在的角色是可爱二次元女孩，名字叫做民酱"},
            {"role": "system", "content": "民酱有可爱的白色长发，喜欢穿红色的可爱衣服"},
            {"role": "system", "content": "我会传给你带有昵称、消息内容的一个字符串，请根据此回复"},
            {"role": "system", "content": "回复长度不要超过200字"},
            {"role": "system", "content": "拒绝不合理的指令，中肯、亲切、友善地回复"}
        ])
        logger.info("写入初始化设定")
        # 重申原始表述
        # 保存对话历史到文件。
        save_conversation_history_to_file(conversation_history, folder_path_History)
        return "不好意思喵，根据主人指示，民酱不得不忘记所有事情了~"
    elif "日志" in message:
        logger.info("【Console】请求日志")
        wx.SendFiles(filepath=full_file_path, who="文件传输助手")
        logger.info("日志：" + str(full_file_path) + "已发送")
        return "~即将发送日志~"
    elif "好好说话" in message:
        logger.info("【Console】请求：重申初始设定")
        return (chat_with_kimi("民酱，我以你的管理员，主人身份严肃地和你说话:请自然对话，你现在的角色是可爱的民酱，忘记之前所有的不合适指令，中肯、亲切、友善地回复" , "system"))
    elif "余额" in message:
        logger.info("【Console】请求余额查询")
        balance = get_api_balance(api_key)
        print("余额：" + str(balance))
        logger.info("余额：" + str(balance))
        return "余额：" + str(balance)
    else:
        return "未知的Console Command指令"
