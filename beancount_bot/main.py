import click

from beancount_bot import bot, config as conf, __VERSION__
from beancount_bot.config import load_config, get_config
from beancount_bot.i18n import _
from beancount_bot.session import load_session
from beancount_bot.task import load_task, start_schedule_thread
from beancount_bot.transaction import get_manager
from beancount_bot.util import logger


@click.command()
@click.version_option(__VERSION__, '-V', '--version', help=_("显示版本信息"))
@click.help_option(help=_("显示帮助信息"))
@click.option('-c', '--config', default='beancount_bot.yml', help=_("配置文件路径"))
def main(config):
    """
    适用于 Beancount 的 Telegram 机器人
    """
    logger.setLevel('INFO')
    # 加载配置
    logger.info("加载配置：%s", config)
    conf.config_file = config
    load_config()
    # 设置日志等级
    logger.setLevel(get_config('log.level', 'INFO'))
    # 加载会话
    logger.info("加载会话...")
    load_session()
    # 创建管理对象
    logger.info("创建管理对象...")
    get_manager()
    # 加载定时任务
    logger.info("加载定时任务...")
    load_task()
    start_schedule_thread()
    # 启动
    logger.info("启动 Bot...")
    bot.serving()


if __name__ == '__main__':
    main()
