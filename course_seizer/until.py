import time
from functools import wraps


class Until:
    """
    装饰器类, 确保某些请求函数一定成功
    """
    @classmethod
    def until(cls, func):
        """
        在高并发情况下要求某些函数一定要执行成功
        :param func:
        :return:
        """
        wraps(func)
        wait_time = 5  # 请求失败后的等待时间

        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            while not result:
                result = func(*args, **kwargs)
                time.sleep(wait_time)
            return result

        return wrapper
