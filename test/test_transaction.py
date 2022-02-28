import tempfile
import unittest
import uuid

from beancount_bot import transaction
from beancount_bot.dispatcher import Dispatcher
from beancount_bot.transaction import TransactionManager


class TestTransactionManager(unittest.TestCase):

    def setUp(self):
        with tempfile.NamedTemporaryFile('w+b', suffix='.bean', delete=False) as f:
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

        with open(self.tmp_file, 'r', encoding='utf-8') as f:
            data = f.read()
            self.assertIn(transaction.META_TIME, data)
            self.assertIn(transaction.META_UUID, data)

        tx_str = transaction.stringfy(tx)
        self.assertIn('2010-01-01 * "Payee" "Desc"\n', tx_str)
        self.assertIn('Income:Unknown\n', tx_str)
        self.assertIn('Assets:Unknown  1 CNY\n', tx_str)

    def test_create_raw(self):
        # Mock
        class MockDispatcher(Dispatcher):
            def _process_raw(self, input_str: str) -> str:
                return '; comment'

        # 测试
        manager = TransactionManager([MockDispatcher()], self.tmp_file)
        tx_uuid, tx = manager.create_from_str('')
        self.assertEqual(tx, '; comment')
        with open(self.tmp_file, 'r', encoding='utf-8') as f:
            self.assertIn(tx_uuid, f.read())

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
        with open(self.tmp_file, 'a+', encoding='utf-8') as f:
            pre = str(uuid.uuid4())
            f.write(f'; {pre}\n')
        tx_uuid, tx = manager.create_from_str('')
        with open(self.tmp_file, 'a+', encoding='utf-8') as f:
            post = str(uuid.uuid4())
            f.write(f'; {post}\n')
        # 删除
        self.assertRaises(ValueError, manager.remove, uuid.uuid4())

        delete_tx = manager.remove(tx_uuid)
        self.assertEqual(tx_uuid, delete_tx.meta[transaction.META_UUID])

        with open(self.tmp_file, 'r', encoding='utf-8') as f:
            data = f.read()
        self.assertNotIn(poison_str, data)
        self.assertIn(pre, data)
        self.assertIn(post, data)

    def test_remove_raw(self):
        # Mock
        class MockDispatcher(Dispatcher):
            def _process_raw(self, input_str: str) -> str:
                return '; comment1\n; comment2'

        manager = TransactionManager([MockDispatcher()], self.tmp_file)
        with open(self.tmp_file, 'a+', encoding='utf-8') as f:
            pre = str(uuid.uuid4())
            f.write(f'; {pre}\n')
        tx_uuid, tx = manager.create_from_str('')
        with open(self.tmp_file, 'a+', encoding='utf-8') as f:
            post = str(uuid.uuid4())
            f.write(f'; {post}\n')
        # 删除
        self.assertRaises(ValueError, manager.remove, uuid.uuid4())

        delete_tx = manager.remove(tx_uuid)
        self.assertEqual(tx, delete_tx)

        with open(self.tmp_file, 'r', encoding='utf-8') as f:
            data = f.read()
        self.assertNotIn('comment1', data)
        self.assertNotIn('comment2', data)
        self.assertNotIn(tx_uuid, data)
        self.assertIn(pre, data)
        self.assertIn(post, data)

    def test_remove_wrong_syntax_tolerance(self):
        # Mock
        poison_str = str(uuid.uuid4())

        class MockDispatcher(Dispatcher):
            def _process_raw(self, input_str: str) -> str:
                return f'''
                2010-01-01 * "Payee" "{poison_str}"
                  Income:Unknown
                  Assets:Unknown  1 CNY
                '''

        # 添加语法错误内容
        manager = TransactionManager([MockDispatcher()], self.tmp_file)
        with open(self.tmp_file, 'a+', encoding='utf-8') as f:
            f.write(f'wrong syntax\n')
        # 添加正确语法交易
        correct_tx, _ = manager.create_from_str('')
        # 可以正常删除
        self.assertRaises(ValueError, manager.remove, uuid.uuid4())
        delete_tx = manager.remove(correct_tx)
        self.assertEqual(correct_tx, delete_tx.meta[transaction.META_UUID])

        with open(self.tmp_file, 'r', encoding='utf-8') as f:
            data = f.read()
        self.assertNotIn(poison_str, data)
        self.assertNotIn(correct_tx, data)
        self.assertIn('wrong syntax', data)

        with open(self.tmp_file, 'w', encoding='utf-8') as f:
            f.write(data.replace('wrong syntax', ''))
