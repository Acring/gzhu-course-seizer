import re
import requests
import logging
from bs4 import BeautifulSoup
from course_seizer.until import Until


class Seizer(object):
    """
    抢课模块
    """
    _timeout = 10
    process_name = ""

    def __init__(self, index, target_host, cookies, info, timeout):
        self.cookies = cookies
        self.target_host = target_host  # 目标主机地址
        self.process_name = "线程{}".format(index)
        self.session = requests.session()
        self.sport_url = target_host + "/xf_xstyxk.aspx?xh={}&xm=&gnmkdm=N121205".format(info.username)
        self.whole_url = target_host + "/xf_xsqxxxk.aspx?xh={}&xm=&gnmkdm=N121203".format(info.username)
        self.info = info
        self._timeout = timeout

        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko)\
             Chrome/51.0.2704.63 Safari/537.36',
        }

        if not self.cookies:
            logging.warning("{}:请先登录数字广大".format(self.process_name))
            return
        self.session.cookies = cookies

    def seize_sport(self):
        """
        体育选课
        :return:
        """


        self.redirect()
        res = self.load_sport_page()
        num_teacher = self.get_sport_teacher_by_name(res)

        if num_teacher == -1:
            logging.warning("{}:未找到相应的老师,请检查".format(self.process_name))
            return

        res = self.submit_sport(res, num_teacher)
        self.show_class(res)

    def seize_whole(self):
        """
        全校性选课
        :return:
        """
        if not self.cookies:
            logging.warning("{}:请先登录数字广大".format(self.process_name))
            return

        self.redirect()
        res = self.load_whole_page()
        page_turner = self.change_show_number(res)
        num_lesson = self.get_whole_teacher_by_name(page_turner)

        page = 1
        while not self.end_of_page(page_turner) and num_lesson == -1:
            page_turner = self.turn_page(page_turner)
            num_lesson = self.get_whole_teacher_by_name(page_turner)
            page += 1

        if num_lesson == -1:
            logging.warning("{}:未找到指定老师".format(self.process_name))
            return

        res = self.submit_whole(page_turner, num_lesson, page)
        self.show_class(res)

    @Until.until
    def redirect(self):
        """
        跳转到不同的抢课服务器
        :return: bool 是否跳转成功
        """
        url = self.target_host + "/Login_gzdx.aspx"
        try:
            logging.info("{}:正在跳转抢课服务器".format(self.process_name))
            res = self.session.get(url, timeout=self._timeout)
            if res.ok:
                return True
            return False

        except Exception as e:
            logging.error(e.args)
            logging.error("{}:跳转服务器失败".format(self.process_name))
            return False

    @Until.until
    def load_sport_page(self):
        """
        进入体育选课界面并返回html
        :return: 页面HTML
        """

        try:
            logging.info("{}:进入体育选课页面".format(self.process_name))
            res = self.session.get(self.sport_url, timeout=self._timeout)
            self.check_error(res)

            if re.findall(r'name="__EVENTTARGET" value="(.*?)"', res.text):
                return res
            return None

        except Exception as e:
            logging.error(e.args)
            logging.error("{}:进入体育选课页面失败".format(self.process_name))
            return None

    @Until.until
    def load_whole_page(self):
        """
        进入全校选课界面并返回html
        :return:
        """

        try:
            logging.info("{}:进入全校选课页面".format(self.process_name))
            res = self.session.get(self.whole_url, timeout=self._timeout)
            logging.debug(self.whole_url)
            self.check_error(res)
            if re.findall(r'name="__EVENTTARGET" value="(.*?)"', res.text):
                return res
            return None

        except Exception as e:
            logging.error(e.args)
            logging.error("{}:进入全校选课页面失败".format(self.process_name))
            return None

    @Until.until
    def change_show_number(self, res):
        """
        改变全校请选课的显示数量
        :param res: 全校性选课的页面html
        :return:
        """

        try:
            logging.info("{}:改变选课数量".format(self.process_name))
            hidden_rex = self.get_hidden(res)

            change_show_req = {  # 改变显示的提交表单
                "__EVENTTARGET": hidden_rex[0],
                "__EVENTARGUMENT": hidden_rex[1],
                "__VIEWSTATEGENERATOR": hidden_rex[2],
                "__VIEWSTATE": hidden_rex[3],
                "ddl_kcxz": "",
                "ddl_ywyl": "",
                "ddl_kcgs": "",
                "ddl_xqbs": "1",
                "ddl_sksj": "",
                "TextBox1": "",
                "dpkcmcGrid:txtChoosePage": "1",
                "dpkcmcGrid:txtPageSize": "100",
                "dpDataGrid2:txtChoosePage": "1",
                "dpDataGrid2:txtPageSize": "100",
            }

            res = self.session.post(self.whole_url, data=change_show_req, timeout=self._timeout)
            self.check_error(res)
            if self.check_valid(res):
                return res
            return None
        except Exception as e:
            logging.error(e.args)
            logging.error("{}:改变选课数量失败".format(self.process_name))
            return None

    @Until.until
    def turn_page(self, res, current_page):
        """
        翻页页面, 全校性选课需要翻页
        :param res: HTML
        :param current_page: 当前页
        :return:
        """

        try:
            logging.info("{}:正在翻页".format(self.process_name))
            hidden_rex = self.get_hidden(res)

            true_page_req = {
                "__EVENTTARGET": hidden_rex[0],
                "__EVENTARGUMENT": hidden_rex[1],
                "__VIEWSTATEGENERATOR": hidden_rex[2],
                "__VIEWSTATE": hidden_rex[3],
                "ddl_kcxz": "",
                "ddl_ywyl": "",
                "ddl_kcgs": "",
                "ddl_xqbs": "1",
                # 翻页
                "dpkcmcGrid:txtChoosePage": str(current_page),
                "dpkcmcGrid:txtPageSize": "100",
                "ddl_sksj": "",
                "TextBox1": "",
                "dpkcmcGrid:btnNextPage": "ÏÂÒ»Ò³",
                # "kj": "°å¿é£¨4£©",
                "dpDataGrid2:txtChoosePage": "1",
                "dpDataGrid2:txtPageSize": "100",
            }

            res = self.session.post(self.whole_url, data=true_page_req, timeout=self._timeout)
            self.check_error(res)
            if self.check_valid(res):
                return res
            return None
        except Exception as e:
            logging.error(e.args)
            logging.error("{}:翻页失败".format(self.process_name))
            return None

    @Until.until
    def submit_sport(self, res, num_teacher):
        """
        提交选课表单
        :param res: HTML
        :param num_teacher: 老师编号
        :return:
        """
        try:
            logging.info("{}:提交体育选课表单".format(self.process_name))
            hidden_rex = self.get_hidden(res)

            sport_req = {
                "__EVENTTARGET": hidden_rex[0],
                "__EVENTARGUMENT": hidden_rex[1],
                "__VIEWSTATEGENERATOR": hidden_rex[2],
                "__VIEWSTATE": hidden_rex[3],
                "kcmcGrid:_ctl" + str(num_teacher) + ":xk": "on",
                "Button1": "+Ìá+½»+"
            }
            res = self.session.post(self.sport_url, data=sport_req, timeout=self._timeout)

            self.check_error(res)
            if self.not_in_time(res):  # 没有到选课时间
                return None

            return res
        except Exception as e:
            logging.error(e.args)
            logging.error("提交体育选课表单失败")
            return None

    @Until.until
    def submit_whole(self, res, lesson, page):
        """
        提交全校选课表单
        :return:
        """
        try:
            logging.info("{}:提交全校性选课表单".format(self.process_name))
            hidden_rex = self.get_hidden(res)

            submit_req = {
                "__EVENTTARGET": hidden_rex[0],
                "__EVENTARGUMENT": hidden_rex[1],
                "__VIEWSTATEGENERATOR": hidden_rex[2],
                "__VIEWSTATE": hidden_rex[3],
                "ddl_kcxz": "",
                "ddl_ywyl": "",
                "ddl_kcgs": "",
                "ddl_xqbs": "1",
                "dpkcmcGrid:txtChoosePage": str(page),
                "dpkcmcGrid:txtPageSize": "100",
                "ddl_sksj": "",
                "TextBox1": "",
                "kcmcGrid:_ctl" + str(lesson) + ":xk": "on",
                "dpDataGrid2:txtChoosePage": "1",
                "dpDataGrid2:txtPageSize": "100",
                "Button1": "++%CC%E1%BD%BB++"
            }

            res = self.session.post(self.whole_url, data=submit_req, timeout=self._timeout)
            self.check_error(res)
            if self.not_in_time(res):
                return None
            return res

        except Exception as e:
            logging.error(e.args)
            logging.error("{}:提交全校性选课表单失败".format(self.process_name))
            return None

    def get_sport_teacher_by_name(self, res):
            """
            通过姓名找到体育教师的序号
            :param res: HTML
            :return: 教师序号
            """
            inf = BeautifulSoup(res.text, "html.parser")
            try:
                kcmc = inf.select("#kcmcGrid")[0]  # 课程信息
                tr = kcmc.select("tr")  # 每一行
            except Exception as e:
                logging.error(e.args)
                logging.error("{}:体育选课可能未开放".format(self.process_name))
                return -1

            for i in range(len(tr)):
                td = tr[i].select("td")[1]  # 教师姓名
                if td.text == self.info.value:
                    logging.info("{}:找到教师:{}".format(self.process_name, self.info.value))
                    break
            else:
                return -1
            return i + 1

    def get_whole_teacher_by_name(self, res):
        """
        通过姓名找到体育教师的序号
        :param res: HTML
        :return: 教师序号
        """
        inf = BeautifulSoup(res.text, "html.parser")
        kcmc = inf.select("#kcmcGrid")[0]  # 课程信息
        tr = kcmc.select("tr")  # 每一行
        for i in range(len(tr)):
            td = tr[i].select("td")  # 教师姓名
            if td[4].text == self.info.value:
                logging.info("{}:找到教师: {}".format(self.process_name, td[4].text))
                for x in td[2:7]:
                    print(x.text, end=" ")
                print("")
                break
        else:
            logging.warning("{}:未找到教师".format(self.process_name))
            return -1
        return i + 1

    def get_whole_teacher_by_id(self, res):
        """
        通过课程序号找课程
        :param res: HTML
        :return: 序号
        """
        inf = BeautifulSoup(res.text, "html.parser")
        kcmc = inf.select("#kcmcGrid")[0]
        tr = kcmc.select("tr")  # 每一行

        for i in range(len(tr)):
            td = tr[i].select("td")  # 课程代码
            if td[3].text == self.info.value:
                logging.info("{}:找到课程代码{}".format(self.process_name, self.info.value))
                for x in td[2:7]:
                    print(x.text, end=" ")
                print("")
                return i + 1
        else:
            logging.warning("{}:未找到课程代码{}".format(self.process_name, self.info.value))
            return -1

    @staticmethod
    def show_class(res):
        """
        打印选到的课程
        :param: res 选课返回页面
        :return:
        """
        logging.info("已选课程如下")
        bs4_result = BeautifulSoup(res.text, "html.parser")

        data = bs4_result.select("#DataGrid2")[0]

        for tr in data.select("tr"):
            for x in tr.select("td"):
                print(x.text, end=" ")
            print("\n")

    @staticmethod
    def end_of_page(res):
        """
        检查是否是全校性选课的最后一页
        :param res: 页面HTML
        :return: True or False
        """
        inf = BeautifulSoup(res.text, "html.parser")
        current_page = inf.select("#dpkcmcGrid_lblCurrentPage")[0].text
        total_page = inf.select("#dpkcmcGrid_lblTotalPages")[0].text
        if current_page == total_page:
            return True
        return False

    @staticmethod
    def get_hidden(res):
        """
        获取页面中的隐藏码, 提交的时候需要
        :param res: 页面html
        :return:
        """
        hidden_rex = list()

        hidden_rex.append(re.findall(r'name="__EVENTTARGET" value="(.*?)"', res.text)[0])
        hidden_rex.append(re.findall(r'name="__EVENTARGUMENT" value="(.*?)"', res.text)[0])
        hidden_rex.append(re.findall(r'name="__VIEWSTATEGENERATOR" value="(.*?)"', res.text)[0])
        hidden_rex.append(re.findall(r'name="__VIEWSTATE" value="(.*?)"', res.text)[0])

        return hidden_rex

    @staticmethod
    def check_error(res):
        """
        检查Error页面，表示服务正忙
        :param res: 页面HTML
        :return: 无
        :exception: ERROR页面
        """
        if "ERROR" in res.text or res.is_redirect:  # ERROR 或重定向
            raise Exception("ERROR页面")

    @staticmethod
    def check_valid(res):
        """
        检查页面的正确性
        :param res: 页面HTML
        :return:
        """
        return re.findall(r'name="__EVENTTARGET" value="(.*?)"', res.text)

    def not_in_time(self, res):
        """
        未到抢课时间
        :return:
        """
        remind = re.findall("alert\(('.*?')\)", res.text)
        if remind:
            remind = remind[0]
            logging.warning("{}:----------{}----------".format(self.process_name, remind))
            if "现在不是选课时间" in remind:
                return True
        return False
