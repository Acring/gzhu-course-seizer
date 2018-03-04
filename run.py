import course_seizer.manager as manager
import logging

data = {
    "tag": "xxx",  # 标志
    "username": "xxx",  # 学号
    "password": "xxx",  # 密码
    "cour_type": "whole",  # 选课类型 sport/whole
    "teacher": "xxx",  # 目标老师
    "index": 1  # 相同老师,选第几个
}

if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s : %(levelname)s : %(message)s", level=logging.INFO)
    info = manager.Info(data)
    course_manager = manager.CourseManager(info=info, thread_num=4)
    course_manager.run()
