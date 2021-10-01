import sys

import telebot

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
