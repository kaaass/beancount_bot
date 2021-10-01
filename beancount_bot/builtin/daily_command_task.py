import os
from typing import List

import schedule
from telebot import TeleBot

from beancount_bot.session import all_user
from beancount_bot.task import ScheduleTask


class DailyCommandTask(ScheduleTask):
    """
    每日执行指令任务
    """

    def __init__(self, time: str, commands: List[str], message: str):
        """
        :param time: 每日更新时间
        :param commands: 执行指令
        :param message: 执行完成后发送信息
        """
        super().__init__()
        self.time = time
        self.commands = commands
        self.message = message

    def register(self, fire: callable):
        schedule.every().day.at(self.time).do(fire)

    def trigger(self, bot: TeleBot):
        # 执行指令
        for cmd in self.commands:
            os.system(cmd)
        # 发送信息
        for uid in all_user():
            bot.send_message(uid, self.message)
