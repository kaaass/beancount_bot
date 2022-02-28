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

    def test_process_raw(self):
        class MockDispatcher(Dispatcher):
            def _process_raw(self, input_str: str) -> str:
                return '2022-01-01 event "Festival" "New Year"\n'

        dispatcher = MockDispatcher()
        tx = dispatcher.process('')
        self.assertEqual(tx, '2022-01-01 event "Festival" "New Year"\n')

    def test_bad_syntax(self):
        class MockDispatcher(Dispatcher):
            def _process_raw(self, input_str: str) -> str:
                return 'wrong syntax'

        dispatcher = MockDispatcher()
        with self.assertRaises(ValueError):
            dispatcher.process('')
