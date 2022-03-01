import json
import os.path
from types import MappingProxyType
from typing import Dict, Iterable

from beancount_bot.config import get_config
from beancount_bot.util import logger

SESS_AUTH = 'auth'
SESS_TX_TAGS = 'tx_tags'

_session_cache: Dict[str, dict] = {}


def load_session():
    """
    从文件恢复会话数据
    :return:
    """
    global _session_cache
    session_file = get_config('bot.session_file')
    if os.path.exists(session_file):
        with open(session_file, 'r', encoding='utf-8') as f:
            _session_cache = json.load(f)
        logger.debug("从文件恢复会话 %s", _session_cache)


def get_session_for(uid: int) -> MappingProxyType:
    """
    返回用户会话的不可变视图
    :param uid:
    :return:
    """
    uid = str(uid)
    if uid not in _session_cache:
        _session_cache[uid] = {}
    return MappingProxyType(_session_cache[uid])


def get_session(uid: int, key: str, default_value=None) -> object:
    """
    返回用户会话的某一值
    :param uid:
    :param key:
    :param default_value:
    :return:
    """
    uid = str(uid)
    if uid not in _session_cache:
        _session_cache[uid] = {}
    if key not in _session_cache[uid]:
        return default_value
    return _session_cache[uid][key]


def set_session(uid: int, key: str, value: object):
    """
    设置用户会话值
    :param uid:
    :param key:
    :param value:
    :return:
    """
    uid = str(uid)
    if uid not in _session_cache:
        _session_cache[uid] = {}
    _session_cache[uid][key] = value
    # 保存缓存
    session_file = get_config('bot.session_file')
    with open(session_file, 'w', encoding='utf-8') as f:
        json.dump(_session_cache, f)


def all_user(auth=True) -> Iterable[int]:
    """
    获得所有用户
    :param auth:
    :return:
    """
    if auth:
        return map(lambda t: int(t[0]), filter(lambda t: SESS_AUTH in t[1] and t[1][SESS_AUTH], _session_cache.items()))
    else:
        return map(int, _session_cache.keys())
