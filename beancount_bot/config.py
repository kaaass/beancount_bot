import yaml

from beancount_bot.i18n import _

global_object_map = {}

GLOBAL_CONFIG = 'config'
GLOBAL_MANAGER = 'manager'
GLOBAL_TASK = 'task'

config_file = ''


def set_global(key: str, obj):
    """
    设置全局对象
    :param key:
    :param obj:
    :return:
    """
    global global_object_map
    global_object_map[key] = obj


def get_global(key: str, default_producer: callable):
    """
    获取全局对象
    :param key:
    :param default_producer:
    :return:
    """
    global global_object_map
    if key not in global_object_map:
        set_global(key, default_producer())
    return global_object_map[key]


def load_config(path=None):
    """
    从文件加载配置，将清空全局对象
    :param path:
    :return:
    """
    if path is None:
        path = config_file
    global global_object_map
    with open(path, 'r', encoding='utf-8') as f:
        data = yaml.full_load(f)
    global_object_map = {}
    set_global(GLOBAL_CONFIG, data)


def get_config_obj():
    """
    获得配置对象
    :return:
    """

    def _exception():
        raise ValueError(_("配置未载入！"))

    return get_global(GLOBAL_CONFIG, _exception)


def get_config(key_path: str, default_value=None):
    """
    获得配置
    :param key_path:
    :param default_value:
    :return:
    """
    obj = get_config_obj()
    for ind in key_path.split('.'):
        if ind not in obj:
            return default_value
        obj = obj[ind]
    return obj
