from beancount_bot.dispatcher import Dispatcher


class ExampleDispatcher(Dispatcher):
    """
    示例交易语句处理器
    在配置中加入：
      - class: 'example.ExampleDispatcher'
        args:
          payee: '对方'
    """

    def __init__(self, payee) -> None:
        super().__init__()
        self.payee = payee

    def quick_check(self, input_str: str) -> bool:
        return True

    def _process_raw(self, input_str: str) -> str:
        return f'''
                2010-01-01 * "{self.payee}" "{input_str}"
                  Income:Unknown
                  Assets:Unknown  1 CNY
                '''

    def get_name(self) -> str:
        return '示例处理器'

    def get_usage(self) -> str:
        return f'输入任何字符串，将会被视为交易描述。交易目标为：{self.payee}。'
