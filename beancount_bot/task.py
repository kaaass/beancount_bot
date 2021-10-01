import threading
import time
from typing import Dict

import schedule
from telebot import TeleBot

from beancount_bot.config import get_config, get_global, GLOBAL_TASK
from beancount_bot.util import logger, load_class

_schedule_thread: threading.Thread = None


class ScheduleTask:
    """
    定时任务
    """

    def __init__(self):
        self.config = None

    def register(self, fire: callable):
        """
        注册定时任务
        :param fire: 待执行函数
        :return:
        """
        pass

    def trigger(self, bot: TeleBot):
        """
        触发任务
        :param bot: Bot 对象
        :return:
        """
        pass


def load_task() -> Dict[str, ScheduleTask]:
    """
    加载定时任务
    :return:
    """
    from beancount_bot.bot import bot
    ret = {}
    schedule.clear()
    for conf in get_config('schedule', []):
        name = conf['name']
        clazz = load_class(conf['class'])
        args = conf['args']

        logger.info('注册定时任务：%s', name)
        task: ScheduleTask = clazz(**args)
        task.register(lambda: task.trigger(bot))
        task.config = conf

        ret[name] = task
    return ret


def get_task() -> Dict[str, ScheduleTask]:
    """
    获得任务
    :return:
    """
    return get_global(GLOBAL_TASK, load_task)


def start_schedule_thread(interval=5) -> threading.Thread:
    """
    运行定时任务
    :param interval:
    :return:
    """

    class ScheduleThread(threading.Thread):
        @classmethod
        def run(cls):
            while True:
                schedule.run_pending()
                time.sleep(interval)

    global _schedule_thread
    _schedule_thread = ScheduleThread()
    _schedule_thread.setDaemon(True)
    _schedule_thread.start()
    return _schedule_thread
