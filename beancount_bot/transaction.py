import datetime
import uuid
from typing import List, Tuple

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

    def create(self, tx: Transaction) -> Tuple[Uuid, Transaction]:
        """
        创建交易
        :param tx:
        :return:
        """
        tx_uuid = Uuid(uuid.uuid4())
        # 添加控制元数据
        tx.meta[META_UUID] = tx_uuid
        tx.meta[META_TIME] = str(datetime.datetime.now())
        # 保存至账本
        with open(self.__bean_file, 'a+', encoding='utf-8') as f:
            printer.print_entry(tx, file=f)
        return tx_uuid, tx

    def remove(self, tx_uuid: Uuid) -> Transaction:
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
            raise ValueError("交易不存在！")
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

    def create_from_str(self, tx_str) -> Tuple[Uuid, Transaction]:
        """
        从交易语法创建交易
        :param tx_str:
        :return:
        """
        tx = self._parse_transaction(tx_str)
        return self.create(tx)

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


def stringfy(tx: Transaction) -> str:
    """
    交易转为字符串
    :param tx:
    :return:
    """
    return printer.format_entry(tx)
