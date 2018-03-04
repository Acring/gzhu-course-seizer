import logging
from concurrent.futures import *
from course_seizer.login import Login
from course_seizer.seizer import Seizer


class Info:
    def __init__(self, data):
        self.tag = data["tag"]  # 标志
        self.username = data["username"]  # 学号
        self.password = data["password"]  # 密码
        self.cour_type = data["cour_type"]  # 抢课类型
        self.value = data["teacher"]  # 老师姓名
        self.index = data["index"]  # 相同老师姓名时选第几个


class CourseManager(object):
    thread_number = 1  # 进程数
    seizer_list = []
    server_url = ['http://202.192.18.182',
                  'http://202.192.18.183',
                  'http://202.192.18.184',
                  'http://202.192.18.185']  # 抢课服务器地址

    def __init__(self, info, thread_num=4):
        self.thread_number = thread_num
        self.info = info
        logging.info(self.info.tag)
        logging.info("学号:{}".format(self.info.username))
        logging.info("抢课类型:{}".format(self.info.cour_type))
        logging.info("抢课目标:{}".format(self.info.value))

    def run(self):
        login = Login(self.info.username, self.info.password, 5)
        login.login()
        cookies = login.get_cookies()

        for n in range(self.thread_number):
            target_host = self.server_url[n % len(self.server_url)]
            self.seizer_list.append(Seizer(n, target_host, cookies, self.info, 10))

        with ThreadPoolExecutor(8) as executor:
            future_task = None
            if self.info.cour_type == "sport":
                future_task = [executor.submit(seizer.seize_sport) for seizer in self.seizer_list]
            if self.info.cour_type == "whole":
                future_task = [executor.submit(seizer.seize_whole) for seizer in self.seizer_list]
            else:
                logging.error("抢课类型错误")
            wait(future_task, return_when=FIRST_COMPLETED)  # 等待一个进程结束
            executor.shutdown()
