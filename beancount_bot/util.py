import sys

import telebot

from beancount_bot.i18n import _

logger = telebot.logger


def load_class(classname: str) -> type:
    """
    通过类名加载类
    :param classname:
    :return:
    """
    class_path = classname.split('.')
    module, classname = '.'.join(class_path[:-1]), class_path[-1]
    __import__(module)
    return getattr(sys.modules[module], classname)


def stringify_errors(errors: list) -> str:
    """
    格式化 Beancount 解析结果的错误信息
    """
    return '\n'.join(map(lambda err:
                         _('行 {lineno}：{message}')
                         .format(lineno=err.source["lineno"], message=err.message), errors))


def stringify_tags(tags, human_readable=False):
    """
    格式化 Beancount 标签列表
    """
    if human_readable:
        if len(tags) == 0:
            return _('无')
        return ', '.join(f'#{t}' for t in tags)
    return ' '.join(f'#{t}' for t in tags)


def indent(text: str, prefix: str = '  ') -> str:
    """
    文本增加缩进
    """
    return '\n'.join(prefix + line for line in text.split('\n'))
