import unittest

from beancount_bot import transaction
from beancount_bot.dispatcher import Dispatcher


class TestDispatcher(unittest.TestCase):

    def test_process(self):
        dispatcher = Dispatcher()
        tx = dispatcher.process('')
        ret = transaction.stringfy(tx)
        self.assertEqual(ret,
                         '2010-01-01 * "Payee" "Desc"\n'
                         '  Assets:Unknown\n'
                         '  Expenses:Unknown  1 CNY\n')
