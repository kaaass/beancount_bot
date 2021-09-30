from beancount_bot import bot, logger, config
from beancount_bot.config import load_config, get_config
from beancount_bot.session import load_session

if __name__ == '__main__':
    # 加载配置
    config.config_file = 'beancount_bot.yml'
    load_config()
    # 设置日志等级
    logger.setLevel(get_config('log.level', 'INFO'))
    # 加载会话
    load_session()
    # 启动
    logger.info("启动 Bot...")
    bot.serving()
