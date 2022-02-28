from typing import Union

from beancount.core.data import Transaction
from beancount.parser import parser

from beancount_bot.i18n import _
from beancount_bot.util import stringify_errors, indent


class Dispatcher:
    """
    交易语句处理器
    """

    def __init__(self) -> None:
        """
        处理器的构造函数将在构建 TransactionManager 时执行。如启动时、/reload 后第一条语句解析前
        构造函数参数通过 **kwargs 形式传入
        """
        super().__init__()

    def quick_check(self, input_str: str) -> bool:
        """
        快速检查输入是否符合
        此方法不必进行精准判断，但是不建议进行耗时操作
        :param input_str: 用户输入
        :return: 用户输入是否可被处理器处理
        """
        return True

    def process(self, input_str: str) -> Union[Transaction, str]:
        """
        解析输入为交易。若输入不合规，则抛出 ValueError
        一般情况下，不需要重载此方法
        :param input_str: 用户输入
        :return: 如果解析为交易，返回 Transaction；否则返回符合 beancount 语法的字符串
        :raise NotMatchException: 用户输入不可被处理器处理
        """
        tx_str = self._process_raw(input_str)
        # 解析结果
        entries, errors, __ = parser.parse_string(tx_str, dedent=True)
        if len(errors) > 0:
            # 语法错误
            name = self.get_name()
            desc = stringify_errors(errors)
            raise ValueError(_("解析结果存在语法错误！\n处理器: {name}\n解析结果：\n{result}\n错误:\n{desc}")
                             .format(name=name, result=indent(tx_str), desc=indent(desc)))
        if len(entries) > 1:
            raise ValueError(_("不支持解析结果为多条语句"))
        if len(entries) == 0:
            # 注释
            return tx_str
        # 返回
        tx = entries[0]
        if isinstance(tx, Transaction):
            return tx
        else:
            return tx_str

    def _process_raw(self, input_str: str) -> str:
        """
        解析输入为 beancount 语法
        正常处理器都应该重载此方法
        :param input_str:
        :return:
        """
        return '2010-01-01 * "Payee" "Desc"\n' \
               '  Assets:Unknown\n' \
               '  Expenses:Unknown  1 CNY\n'

    def get_name(self) -> str:
        """
        获得处理器名称。用于在 /help 中显示选项
        :return: 处理器名称
        """
        return _("未知")

    def get_usage(self) -> str:
        """
        获得帮助信息。用于在 /help 中显示具体帮助内容，应当详细
        :return:
        """
        return _("暂无帮助信息。")
