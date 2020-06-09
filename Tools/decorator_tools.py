# -*- coding: utf-8 -*-
"""
装饰器
"""
import time
from Tools.log import FrameLog
from Tools.date_helper import current_timestamp
from threading import Thread
import threading
from functools import wraps

save_mutex = threading.Lock()
log = FrameLog().log()


def async(func):
    """
    异步开线程调用
    :param func: 被修饰的函数
    :return:
    """
    def wrapper(*args, **kwargs):
        thr = Thread(target=func, args=args, kwargs=kwargs)
        thr.start()
    return wrapper


def elapse_time(func):
    """
    计算方法耗时
    :param func: 被修饰的函数
    :return:
    """
    def wrapper(*args, **kwargs):
        st = current_timestamp()
        res = func(*args, **kwargs)
        et = current_timestamp()
        log.info("%s ELAPSE TIME: %s" % (func.__name__, (et-st)/1000.0))
        return res
    return wrapper


def thread_save(func):
    @wraps(func)
    def processed_res(*args, **kwargs):
        save_mutex.acquire()
        st = time.time()
        res = func(*args, **kwargs)
        et = time.time()
        save_mutex.release()
        log.info(u"%s: DONE %s" % (func.__name__, (et-st)))
        return res
    return processed_res

