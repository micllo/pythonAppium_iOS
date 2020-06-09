import time
from Common.com_func import log
from Project.pro_demo_1.page_object.heart_page import AddPage
from TestBase.test_case_unit import ParaCase
from TestBase.app_action import Base


class HealthTest(ParaCase):

    """ Health 用 例 集"""

    def test_add_heart_rate_66(self):
        """ 测试搜索'添加心率66'(通过)  """
        log.info("user(test_add_heart_rate_66): " + self.user)
        log.info("passwd(test_add_heart_rate_66): " + self.passwd)

        # 根据不同用例特定自定义设置 (注：在本框架中作用不大，见 find_ele 方法)
        # self.client.implicitly_wait(5)

        # 通过Base类调用实例方法 ：self（测试用例实例对象）
        Base.screenshot(self, "home.png")

        add_page = AddPage(self)
        add_page.add_heart_rate_66("66")
        # self.assertIn('test_search', "test_search", "test_search用例测试失败")

    def test_add_heart_rate_33(self):
        """ 测试搜索'添加心率33'(失败)  """
        log.info("user(test_add_heart_rate_33): " + self.user)
        log.info("passwd(test_add_heart_rate_33): " + self.passwd)

        add_page = AddPage(self)
        add_page.add_heart_rate_33("33")

    def test_add_heart_rate_11(self):
        """ 测试搜索'添加心率11'(错误)  """
        log.info("user(test_add_heart_rate_11): " + self.user)
        log.info("passwd(test_add_heart_rate_11): " + self.passwd)

        add_page = AddPage(self)
        add_page.add_heart_rate_11("11")

