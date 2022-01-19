# 
import dingtalkchatbot.chatbot as cb
def dingding(text, msg,webhook,secretKey):
    ding = cb.DingtalkChatbot(webhook, secret=secretKey)
    ding.send_text(msg='{}\r\n{}'.format(text, msg), is_at_all=False)
## 飞书
def feishu(text,msg,webhook):
    ding = cb.DingtalkChatbot(webhook)
    ding.send_text(msg='{}\r\n{}'.format(text, msg), is_at_all=False)

# 添加Telegram Bot推送支持
def tgbot(text, msg,token,group_id):
    import telegram
    try:
        bot = telegram.Bot(token='{}'.format(token))# Your Telegram Bot Token
        bot.send_message(chat_id=group_id, text='{}\r\n{}'.format(text, msg))
    except Exception as e:
        pass