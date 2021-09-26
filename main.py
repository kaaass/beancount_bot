from beancount_bot.dispatcher import Dispatcher
from beancount_bot.transaction import TransactionManager

if __name__ == '__main__':
    manager = TransactionManager([Dispatcher()], 'test/tmp.bean')
    manager.remove('b9901922-855f-4c52-99f1-b029047a488c')
