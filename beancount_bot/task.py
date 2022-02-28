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
        """
        处理器的构造函数将在载入配置时时执行。如启动时、/reload 时
        构造函数参数通过 **kwargs 形式传入
        """
        self.config = None

    def register(self, fire: callable):
        """
        注册定时任务。将在构造任务对象后立刻执行。如果不注册，将不会定时触发
        :param fire: 待执行函数
        """
        pass

    def trigger(self, bot: TeleBot):
        """
        触发任务。任务可通过两种方式触发：定时执行（register 中注册）、/task 任务名
        :param bot: Bot 对象
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
        task.register(lambda capture_task=task: capture_task.trigger(bot))
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
                try:
                    schedule.run_pending()
                except Exception as e:
                    logger.warn('定时任务出错：%s', e)
                time.sleep(interval)

    global _schedule_thread
    _schedule_thread = ScheduleThread()
    _schedule_thread.setDaemon(True)
    _schedule_thread.start()
    return _schedule_thread
