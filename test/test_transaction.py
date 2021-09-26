import tempfile
import unittest
import uuid

from beancount_bot import transaction
from beancount_bot.dispatcher import Dispatcher
from beancount_bot.transaction import TransactionManager


class TestTransactionManager(unittest.TestCase):

    def setUp(self):
        with tempfile.TemporaryFile('w+b', suffix='.bean') as f:
            self.tmp_file = f.name

    def test_create(self):
        # Mock
        class MockDispatcher(Dispatcher):
            def _process_raw(self, input_str: str) -> str:
                return '''
                2010-01-01 * "Payee" "Desc"
                  Income:Unknown
                  Assets:Unknown  1 CNY
                '''

        # 测试
        manager = TransactionManager([MockDispatcher()], self.tmp_file)
        tx_uuid, tx = manager.create_from_str('')
        self.assertTrue(transaction.META_TIME in tx.meta)
        self.assertTrue(transaction.META_UUID in tx.meta)

        tx_str = transaction.stringfy(tx)
        self.assertTrue('2010-01-01 * "Payee" "Desc"\n' in tx_str)
        self.assertTrue('Income:Unknown\n' in tx_str)
        self.assertTrue('Assets:Unknown  1 CNY\n' in tx_str)

    def test_remove(self):
        # Mock
        poison_str = str(uuid.uuid4())

        class MockDispatcher(Dispatcher):
            def _process_raw(self, input_str: str) -> str:
                return f'''
                2010-01-01 * "Payee" "{poison_str}"
                  Income:Unknown
                  Assets:Unknown  1 CNY
                '''

        manager = TransactionManager([MockDispatcher()], self.tmp_file)
        tx_uuid, tx = manager.create_from_str('')
        # 删除
        delete_tx = manager.remove(tx_uuid)
        self.assertEqual(tx.meta[transaction.META_UUID], delete_tx.meta[transaction.META_UUID])

        with open(self.tmp_file, 'r', encoding='utf-8') as f:
            data = f.read()
        self.assertFalse(poison_str in data)
