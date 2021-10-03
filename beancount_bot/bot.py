import telebot
from telebot import apihelper
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, MessageEntity, Message, CallbackQuery

from beancount_bot import transaction
from beancount_bot.config import get_config, load_config
from beancount_bot.session import get_session, SESS_AUTH, get_session_for, set_session
from beancount_bot.task import load_task, get_task
from beancount_bot.transaction import get_manager
from beancount_bot.util import logger

apihelper.ENABLE_MIDDLEWARE = True

bot = telebot.TeleBot(token=None, parse_mode=None)


@bot.middleware_handler(update_types=['message'])
def session_middleware(bot_instance, message):
    """
    会话中间件
    :param bot_instance:
    :param message:
    :return:
    """
    bot_instance.session = get_session_for(message.from_user.id)


#######
# 鉴权 #
#######

def check_auth() -> bool:
    """
    检查是否登录
    :return:
    """
    return SESS_AUTH in bot.session and bot.session[SESS_AUTH]


@bot.message_handler(commands=['start'])
def start_handler(message: Message):
    """
    首次聊天时鉴权
    :param message:
    :return:
    """
    auth = get_session(message.from_user.id, SESS_AUTH, False)
    if auth:
        bot.reply_to(message, "已经鉴权过了！")
        return
    # 要求鉴权
    bot.reply_to(message, "欢迎使用记账机器人！请输入鉴权令牌：")


def auth_token_handler(message: Message):
    """
    登陆令牌回调
    :param message:
    :return:
    """
    if check_auth():
        return
    # 未鉴权则视为鉴权令牌
    auth_token = get_config('bot.auth_token')
    if auth_token == message.text:
        set_session(message.from_user.id, SESS_AUTH, True)
        bot.reply_to(message, "鉴权成功！")
    else:
        bot.reply_to(message, "鉴权令牌错误！")


#######
# 指令 #
#######


@bot.message_handler(commands=['reload'])
def reload_handler(message):
    """
    重载配置指令
    :param message:
    :return:
    """
    if not check_auth():
        bot.reply_to(message, "请先进行鉴权！")
        return
    load_config()
    load_task()
    bot.reply_to(message, "成功重载配置！")


@bot.message_handler(commands=['help'])
def help_handler(message):
    """
    帮助指令
    :param message:
    :return:
    """
    # 创建消息按键
    markup = InlineKeyboardMarkup()
    dispatchers = get_manager().dispatchers
    for ind, d in zip(range(len(dispatchers)), dispatchers):
        markup.add(InlineKeyboardButton(f'帮助：{d.get_name()}', callback_data=f'help:{ind}'))
    # 帮助信息
    command_usage = [
        '/start - 鉴权',
        '/help - 使用帮助',
        '/reload - 重新加载配置文件',
        '/task - 查看、运行任务',
    ]
    bot.reply_to(message, "记账 Bot\n\n可用指令列表：\n"
                 + '\n'.join(command_usage)
                 + "\n\n交易语句帮助请选择对应模块。", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data[:4] == 'help')
def callback_help(call: CallbackQuery):
    try:
        d_id = int(call.data[5:])
        dispatchers = get_manager().dispatchers
        d = dispatchers[d_id]
        bot.reply_to(call.message, f'帮助：{d.get_name()}\n\n' + d.get_usage())
    except Exception as e:
        logger.error(f'{call.id}：发生未知错误！', e)
        bot.answer_callback_query(call.id, '发生未知错误！')


@bot.message_handler(commands=['task'])
def task_handler(message):
    """
    任务指令
    :param message:
    :return:
    """
    if not check_auth():
        bot.reply_to(message, "请先进行鉴权！")
        return

    cmd = message.text
    tasks = get_task()
    if cmd == '/task':
        # 显示所有任务
        all_tasks = ', '.join(tasks.keys())
        bot.reply_to(message,
                     f'当前注册任务：{all_tasks}\n'
                     '可以通过 /task [任务名] 主动触发')
    else:
        # 运行任务
        dest = cmd[6:]
        if dest not in tasks:
            bot.reply_to(message, '任务不存在！')
            return
        task = tasks[dest]
        task.trigger(bot)


#######
# 交易 #
#######


@bot.message_handler(func=lambda m: True)
def transaction_query_handler(message: Message):
    """
    交易语句处理
    :param message:
    :return:
    """
    if not check_auth():
        auth_token_handler(message)
        return
    # 已鉴权则处理交易
    manager = get_manager()
    try:
        tx_uuid, tx = manager.create_from_str(message.text)
        # 创建消息按键
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('撤回交易', callback_data=f'withdraw:{tx_uuid}'))
        # 回复
        bot.reply_to(message, transaction.stringfy(tx), reply_markup=markup)
    except ValueError as e:
        logger.info(f'{message.from_user.id}：无法添加交易', e)
        bot.reply_to(message, e.args[0])
    except Exception as e:
        logger.error(f'{message.from_user.id}：发生未知错误！添加交易失败。', e)
        bot.reply_to(message, '发生未知错误！添加交易失败。')


@bot.callback_query_handler(func=lambda call: call.data[:8] == 'withdraw')
def callback_withdraw(call: CallbackQuery):
    """
    交易撤回回调
    :param call:
    :return:
    """
    auth = get_session(call.from_user.id, SESS_AUTH, False)
    if not auth:
        bot.answer_callback_query(call.id, '请先进行鉴权！')
        return
    tx_uuid = call.data[9:]
    manager = get_manager()
    try:
        manager.remove(tx_uuid)
        # 修改原消息回复
        message = '交易已撤回'
        code_format = MessageEntity('code', 0, len(message))
        bot.edit_message_text(message,
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              entities=[code_format])
    except ValueError as e:
        logger.info(f'{call.id}：无法创建交易', e)
        bot.answer_callback_query(call.id, e.args[0])
    except Exception as e:
        logger.error(f'{call.id}：发生未知错误！撤回交易失败。', e)
        bot.answer_callback_query(call.id, '发生未知错误！撤回交易失败。')


def serving():
    """
    启动 Bot
    :return:
    """

    # 设置 Token
    token = get_config('bot.token')
    bot.token = token
    # 设置代理
    proxy = get_config('bot.proxy')
    if proxy is not None:
        apihelper.proxy = {'https': proxy}
    # 启动
    bot.infinity_polling()
