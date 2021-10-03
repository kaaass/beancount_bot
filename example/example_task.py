import schedule
from telebot import TeleBot

from beancount_bot.session import all_user
from beancount_bot.task import ScheduleTask


class ExampleTask(ScheduleTask):
    """
    示例定时任务
    在配置中加入：
      - name: example
        class: 'example.ExampleTask'
        args:
          time: '18:30'
          info: '广播消息~'
    """

    def __init__(self, time: str, info: str):
        super().__init__()
        self.time = time
        self.info = info

    def register(self, fire: callable):
        # 每日 self.time 时触发
        schedule.every().day.at(self.time).do(fire)

    def trigger(self, bot: TeleBot):
        # 向所有已鉴权用户广播消息
        for uid in all_user():
            bot.send_message(uid, self.info)
