import datetime
import uuid
from typing import List, Tuple, Union

from beancount.core.data import Transaction
from beancount.parser import printer, parser

from beancount_bot.dispatcher import Dispatcher

META_UUID = 'tgbot_uuid'
META_TIME = 'tgbot_time'

Uuid = str


class NotMatchException(Exception):
    pass


class TransactionManager:
    """
    交易信息管理
    """

    def __init__(self, dispatchers: List[Dispatcher], bean_file: str):
        self.dispatchers = dispatchers
        self.__bean_file = bean_file

    def create(self, tx: Union[Transaction, str]) -> Tuple[Uuid, Union[Transaction, str]]:
        """
        创建交易
        :param tx:
        :return:
        """
        tx_uuid = Uuid(uuid.uuid4())
        if isinstance(tx, str):
            # 保存至账本
            with open(self.__bean_file, 'a+', encoding='utf-8') as f:
                f.write(f"; TGBOT_START {tx_uuid}\n{tx}\n; TGBOT_END {tx_uuid}\n")
            return tx_uuid, tx
        elif isinstance(tx, Transaction):
            # 添加控制元数据
            tx.meta[META_UUID] = tx_uuid
            tx.meta[META_TIME] = str(datetime.datetime.now())
            # 保存至账本
            with open(self.__bean_file, 'a+', encoding='utf-8') as f:
                printer.print_entry(tx, file=f)
            return tx_uuid, tx
        else:
            raise ValueError()

    def remove(self, tx_uuid: Uuid) -> Union[Transaction, str]:
        """
        删除交易
        :param tx_uuid:
        :return:
        """
        entries, errors, _ = parser.parse_file(self.__bean_file)
        if len(errors) > 0:
            desc = '\n'.join(map(lambda err: f'行 {err.source["lineno"]}：{err.message}', errors))
            raise ValueError("账本文件内容错误！\n" + desc)
        # 筛选交易
        to_delete = next(
            filter(lambda tx: tx.meta[META_UUID] == tx_uuid if META_UUID in tx.meta else False, entries),
            None
        )
        if to_delete is None:
            # 可能是非交易语句
            return self._remove_comment_wrapped(tx_uuid)
        # 统计删除行。避免删除其他语句。
        min_line = to_delete.meta['lineno']
        max_line = min_line
        for posting in to_delete.postings:
            max_line = max(max_line, posting.meta['lineno'])
        # 删除
        with open(self.__bean_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        with open(self.__bean_file, 'w', encoding='utf-8') as f:
            f.write(''.join(lines[:min_line - 1] + lines[max_line:]))
        return to_delete

    def _remove_comment_wrapped(self, tx_uuid: Uuid) -> str:
        """
        使用注释包裹
        :param tx_uuid:
        :return:
        """
        with open(self.__bean_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        # 筛选列
        min_line = -1
        for i in range(len(lines)):
            if f'TGBOT_START {tx_uuid}' in lines[i]:
                min_line = i
                break
        max_line = -1
        for i in range(len(lines)):
            if f'TGBOT_END {tx_uuid}' in lines[i]:
                max_line = i
                break
        if min_line == -1 or max_line == -1:
            raise ValueError("交易不存在！")
        # 删除
        with open(self.__bean_file, 'w', encoding='utf-8') as f:
            f.write(''.join(lines[:min_line] + lines[max_line + 1:]))
        return ''.join(lines[min_line + 1:max_line])[:-1]

    def create_from_str(self, tx_str) -> Union[Tuple[Uuid, Transaction], Tuple[None, str]]:
        """
        从交易语法创建交易
        :param tx_str:
        :return:
        """
        tx = self._parse_transaction(tx_str)
        tx_uuid, _ = self.create(tx)
        return tx_uuid, tx

    def _parse_transaction(self, tx_str) -> Transaction:
        for dispatcher in self.dispatchers:
            if not dispatcher.quick_check(tx_str):
                continue
            # 尝试解析
            try:
                tx = dispatcher.process(tx_str)
                return tx
            except NotMatchException:
                # 不能通过该解析器解析
                continue
        else:
            # 没有匹配
            raise ValueError("无法识别此交易语法")


def stringfy(tx: Union[Transaction, str]) -> str:
    """
    交易转为字符串
    :param tx:
    :return:
    """
    if isinstance(tx, str):
        return tx
    return printer.format_entry(tx)
