from typing import Union

from beancount.core.data import Transaction
from beancount.parser import parser


class Dispatcher:
    """
    交易语句处理器
    """

    def quick_check(self, input_str: str) -> bool:
        """
        快速检查输入是否符合
        :param input_str:
        :return:
        """
        return True

    def process(self, input_str: str) -> Union[Transaction, str]:
        """
        解析输入为交易。若输入不合规，则抛出 ValueError
        :param input_str:
        :return:
        """
        tx_str = self._process_raw(input_str)
        try:
            tx = parser.parse_one(tx_str)
            if isinstance(tx, Transaction):
                return tx
            else:
                return tx_str
        except AssertionError:
            return tx_str

    def _process_raw(self, input_str: str) -> str:
        """
        解析输入为交易字符串
        :param input_str:
        :return:
        """
        return '''
               2010-01-01 * "Payee" "Desc"
                 Assets:Unknown
                 Expenses:Unknown    + 1 CNY
               '''

    def get_name(self) -> str:
        """
        获得处理器名称。用于在 /help 中显示
        :return:
        """
        return '未知'

    def get_usage(self) -> str:
        """
        获得帮助信息
        :return:
        """
        return '暂无帮助信息。'
