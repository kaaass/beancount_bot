import click

from beancount_bot import bot, config as conf
from beancount_bot.config import load_config, get_config
from beancount_bot.session import load_session
from beancount_bot.util import logger


@click.command()
@click.option('-c', '--config', default='beancount_bot.yml', help='配置文件路径')
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
    # 启动
    logger.info("启动 Bot...")
    bot.serving()


if __name__ == '__main__':
    main()
