from typing import Dict

from telebot import TeleBot

from beancount_bot.config import get_config
from beancount_bot.i18n import _
from beancount_bot.session import get_session, SESS_TX_TAGS, set_session
from beancount_bot.util import stringify_tags


class SessionSpecificConfig:
    """与特定 session 相关的配置"""

    def get(self, cmd, bot: TeleBot, message):
        """获取当前配置内容的指令"""
        pass

    def set(self, cmd, bot: TeleBot, message):
        """设置当前配置的指令"""
        pass

    def help(self):
        """
        获取帮助信息
        :return: get 指令参数, get 帮助信息, set 指令参数, set 帮助信息
        """
        return '[param]', 'help', '[param]', 'help'

    def make_help(self, key, is_set=False):
        """
        生成帮助信息
        :param key: 参数
        :param is_set: 是否是 set 指令
        :return: 帮助信息
        """
        prefix, param, info = None, None, None
        if is_set:
            prefix = '/set'
            _, _, param, info = self.help()
        else:
            prefix = '/get'
            param, info, _, _ = self.help()

        if len(param) > 0:
            param = f' {param}'
        return f'{prefix} {key}{param} - {info}'


SESSION_CONFIG: Dict[str, SessionSpecificConfig] = {}


def register_session_config(key: str, conf: SessionSpecificConfig):
    """注册特定 session 的配置"""
    SESSION_CONFIG[key] = conf


##########
# 具体配置 #
##########


class TagsConfig(SessionSpecificConfig):
    """交易标签"""

    def help(self):
        return '', _('获取添加于交易的标签'), \
               _('[标签列表]'), _('设置当前用户的标签。多个标签使用空格隔开，为空则表示清空。')

    def get(self, cmd, bot, message):
        """显示所有标签"""
        global_tags = get_config('transaction.tags', [])
        session_tags = get_session(bot.session_user_id, SESS_TX_TAGS, [])
        bot.reply_to(message,
                     _("全局标签：{global_tags}\n"
                       "当前用户标签：{session_tags}\n"
                       "可以通过 /set tags [标签列表] 设置当前用户的标签。")
                     .format(global_tags=stringify_tags(global_tags, human_readable=True),
                             session_tags=stringify_tags(session_tags, human_readable=True)))

    def set(self, cmd, bot, message):
        """设置标签"""
        tags = list(set(cmd.split()))
        set_session(bot.session_user_id, SESS_TX_TAGS, tags)
        bot.reply_to(message, _("成功设置用户标签！"))


register_session_config('tags', TagsConfig())
