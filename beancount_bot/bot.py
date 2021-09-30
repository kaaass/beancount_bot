import telebot
from telebot import apihelper
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton, MessageEntity, Message

from beancount_bot import transaction, logger
from beancount_bot.config import get_config, load_config
from beancount_bot.transaction import get_manager

bot = telebot.TeleBot(token=None, parse_mode=None)


@bot.message_handler(commands=['reload'])
def reload_handler(message):
    load_config()
    bot.reply_to(message, "成功重载配置！")


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    # TODO
    bot.reply_to(message, "Howdy, how are you doing?")


@bot.message_handler(func=lambda m: True)
def transaction_query_handler(message: Message):
    manager = get_manager()
    try:
        tx_uuid, tx = manager.create_from_str(message.text)
        # 创建消息按键
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton('撤回交易', callback_data=f'withdraw:{tx_uuid}'))
        # 回复
        bot.reply_to(message, transaction.stringfy(tx), reply_markup=markup)
    except ValueError as e:
        logger.info(f'{message.from_user.id}：无法创建交易', e)
        bot.reply_to(message, e.args[0])
    except Exception as e:
        logger.error(f'{message.from_user.id}：发生未知错误！添加交易失败。', e)
        bot.reply_to(message, '发生未知错误！添加交易失败。')


@bot.callback_query_handler(func=lambda call: call.data[:8] == 'withdraw')
def callback_withdraw(call):
    """
    交易撤回回调
    :param call:
    :return:
    """
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
    if (proxy := get_config('bot.proxy')) is not None:
        apihelper.proxy = {'https': proxy}
    # 启动
    bot.polling()
