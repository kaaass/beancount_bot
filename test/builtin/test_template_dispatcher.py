import datetime
import os.path
import unittest

from beancount_bot import transaction
from beancount_bot.builtin.template_dispatcher import TemplateDispatcher, split_command
from beancount_bot.transaction import NotMatchException

PATH = os.path.split(os.path.realpath(__file__))[0]


class TestTemplateDispatcher(unittest.TestCase):

    def test_quick_check(self):
        d = TemplateDispatcher(os.path.join(PATH, 'template_config.yml'))
        self.assertTrue(d.quick_check('饮料 20'))
        self.assertFalse(d.quick_check('! @饮料 '))
        self.assertFalse(d.quick_check('咖'))
        self.assertTrue(d.quick_check('饭     4.00'))
        self.assertTrue(d.quick_check('咖啡 123'))

    def test_split_command(self):
        cases = [
            ('饮料 20', ['饮料', '20']),
            ('饮料20', ['饮料20']),
            ('"饮料""20"', ['饮料', '20']),
            ('饮料 666>21', ['饮料', '666', '>', '21']),
            ('饮料 20> 521', ['饮料', '20', '>', '521']),
            ('饮料 0 >21', ['饮料', '0', '>', '21']),
            ('饮料  201     >    21', ['饮料', '201', '>', '21']),
            ('饮料 "201  ">  22', ['饮料', '201  ', '>', '22']),
            ('饮料 "201  >"  55', ['饮料', '201  >', '55']),
            ('饮料 "10\\"1  >"   ', ['饮料', '10"1  >']),
            ('"\\"""\\"\\""', ['"', '""']),
            ('"\\\\"  "\\\\233\\\\"', ['\\', '\\233\\']),
        ]
        exception_cases = [
            ('吃饭>>1', 3),
            ('吃饭> \\1', 4),
            ('123"2', 5),
            ('"\\', 2),
            ('"\\"', 3),
        ]

        for cmd, expected in cases:
            ret = split_command(cmd)
            self.assertEqual(ret, expected)

        for cmd, pos in exception_cases:
            try:
                ret = split_command(cmd)
                print(ret)
                self.fail("未发生错误")
            except ValueError as e:
                self.assertIn(str(pos), e.args[0])

    def test_process_simple(self):
        today = datetime.date.today().isoformat()
        cases = [
            ('vultr',
             f'{today} * "Vultr" "月费"\n'
             '  Assets:Digital:Alipay\n'
             '  Expenses:Tech:Cloud    5 USD\n'),
            ('vultr > wx',
             f'{today} * "Vultr" "月费"\n'
             '  Assets:Digital:Wechat\n'
             '  Expenses:Tech:Cloud    5 USD\n'),
            ('饮料 3.0',
             f'{today} * "饮料"\n'
             '  Assets:Digital:Alipay\n'
             '  Expenses:Food:Drink    3.0 CNY\n'),
            ('饮料 3.23>zfb',
             f'{today} * "饮料"\n'
             '  Assets:Digital:Alipay\n'
             '  Expenses:Food:Drink    3.23 CNY\n'),
            ('饮 3.1>wx',
             f'{today} * "饮"\n'
             '  Assets:Digital:Wechat\n'
             '  Expenses:Food:Drink    3.1 CNY\n'),
        ]
        exception_cases = [
            ('vul', NotMatchException),
            ('vultrr', NotMatchException),
            ('vultr 123', '命令不接受参数'),
            ('饮 123 456', '参数数量过多'),
        ]

        d = TemplateDispatcher(os.path.join(PATH, 'template_config.yml'))

        for cmd, expected in cases:
            ret = d.process(cmd)
            ret = transaction.stringfy(ret)
            self.assertEqual(ret, expected)

        for cmd, info in exception_cases:
            try:
                ret = d.process(cmd)
                print(ret)
                self.fail("未发生错误")
            except ValueError as e:
                self.assertIn(info, e.args[0])
            except Exception as e:
                self.assertTrue(isinstance(e, info))

    def test_process_complex(self):
        hour = datetime.datetime.now().hour
        expense = 'Expenses:Food:Extra' if hour <= 3 or hour >= 21 else \
            'Expenses:Food:Dinner:Breakfast' if hour <= 10 else \
            'Expenses:Food:Dinner:Lunch' if hour <= 16 else \
            'Expenses:Food:Dinner:Supper'

        d = TemplateDispatcher(os.path.join(PATH, 'template_config.yml'))

        ret = d.process('饭 20')
        ret = transaction.stringfy(ret)
        self.assertIn(expense, ret)
        print(ret)

        ret = d.process('饭 20>wx')
        ret = transaction.stringfy(ret)
        self.assertIn(expense, ret)
        self.assertIn('Assets:Digital:Wechat', ret)
        print(ret)
