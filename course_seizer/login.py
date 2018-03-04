import logging
import requests
import re
import pickle
import time
import os
from course_seizer.until import Until


class Login(object):
    """
    数字广大登录模块
    """

    def __init__(self, username, password, timeout):
        self.username = username  # 学号
        self.password = password  # 密码
        self.session = requests.session()
        self._timeout = timeout
        self.cookies = None
        self.cookies_save_path = "cookie" + os.sep

        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko)\
             Chrome/51.0.2704.63 Safari/537.36',
        }

    def login(self):
        result = self.load_cookies()
        if result:
            return
        login_page_res = self.load_login_page()
        login_req = self.gen_login_req(login_page_res)
        self.try_login(login_req)
        self.save_cookies()
        return

    @Until.until
    def load_login_page(self):
        """
        加载登录界面
        :return: 登录界面反馈
        """
        login_page_url = "https://cas.gzhu.edu.cn/cas_server/login"

        try:
            logging.info("尝试进入登录界面")
            login_page_res = self.session.get(login_page_url, timeout=self._timeout)
            return login_page_res
        except Exception as e:
            logging.error(e.args[0])
            logging.error("进入登录界面失败")
            return None

    def gen_login_req(self, res):
        """
        生成登录请求
        :param res: 登录界面html
        :return: 登录请求结构
        """
        if not res:
            return None

        logging.info("生成登录表单")
        # 获取lt参数 用于登录
        lt = re.findall(r'name="lt" value="(.*?)"', res.text)

        # 其中lt和_eventId还有execution是必须的参数
        login_req = {  # 登录发送的请求参数
            'username': self.username,
            'password': self.password,
            "lt": lt[0],
            "execution": "e1s1",
            "_eventId": "submit"
        }
        return login_req

    @Until.until
    def try_login(self, login_req):
        """
        发送登录请求,保存登录Cookies
        :param login_req: 请求参数
        :return:  bool
        """

        login_url = "https://cas.gzhu.edu.cn/cas_server/login"  # 登陆网址

        try:
            logging.info("发送登录请求")
            res = self.session.post(login_url, data=login_req, timeout=self._timeout)
            if res.ok:
                self.cookies = self.session.cookies  # 返回cookie供后面的使用
                logging.debug(res.text)
            return True
        except Exception as e:
            logging.error(e.args[0])
            logging.error("发送登录请求失败")
            return False

    def save_cookies(self):
        """
        保存cookie到./cookie路径下，方便下次快速登录
        :return: 无
        """
        if not os.path.exists("cookie"):  # 创建cookie文件夹
            os.mkdir("cookie")

        if not self.cookies:
            return

        filename = self.cookies_save_path + self.username
        with open(filename, 'wb') as f:
            pickle.dump(requests.utils.dict_from_cookiejar(self.cookies), f)
            pickle.dump(time.time(), f)

    def load_cookies(self):
        if not os.path.exists(self.cookies_save_path):
            return False

        filename = self.cookies_save_path + self.username

        if not os.path.exists(filename):
            return False

        logging.info("加载本地cookie")
        try:
            with open(filename, "rb") as f:
                cookies = requests.utils.cookiejar_from_dict(pickle.load(f))
                overtime = time.time() - pickle.load(f)  # cookie超时
                if not cookies or overtime > 3000:
                    return False
                self.cookies = cookies
                return True
        except Exception as e:
            logging.error(e.args)
            logging.error("加载本地cookie出错")
            return False

    def get_cookies(self):
        return self.cookies
