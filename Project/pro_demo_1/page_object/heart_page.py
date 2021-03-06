# -*- coding:utf-8 -*-
from TestBase.app_action import Base
import time


class AddPage(Base):

    """
        【 元 素 定 位 】
    """

    # ======== 模 拟 器 用 例 元 素 ========

    # 触摸 Browse 图标
    def touch_browser_cron(self):
        self.touch_click(315, 846)

    # 'Browse'图标
    def browser_cron(self):
        return self.find_ele(xpath='//XCUIElementTypeButton[@name="Browse"]')
        # return self.find_ele(name='Browse')
        # return self.find_ele(nameContains='Bro')  # 匹配name文本包含的内容

    # 搜索文本框
    def search_field(self):
        return self.find_ele(xpath='//XCUIElementTypeSearchField[@name="Search"]')
        # return self.find_ele(label="Search")
        # return self.find_ele(name="Search")

    # "心率"tab
    def heart_rate_tab(self):
        return self.find_ele(nameContains="BPM")

    # '添加数据'按钮
    def add_data_btn(self):
        return self.find_ele(xpath='//XCUIElementTypeButton[@name="Add Data"]')
        # return self.find_ele(xpath='//NavigationBar/Button[2]')
        # return self.find_ele(name="Add Data")

    # '心率'输入框
    def bpm_field(self):
        # return self.find_ele(xpath='//XCUIElementTypeTextField[@name="BPM"]')
        return self.find_ele(label="BPM")

    # '添加'按钮
    def add_btn(self):
        # return self.find_ele(xpath='//XCUIElementTypeButton[@name="Add"]')
        return self.find_ele(label="Add")

    # ======== 真 机 用 例 元 素 ========

    # "身体测量" 按钮
    def body_check_cron(self):
        return self.find_ele(name='身体测量')

    # "体重" 按钮
    def weight_cron(self):
        return self.find_ele(name='体重')

    # "添加" 按钮
    def add_cron(self):
        return self.find_ele(name='添加')

    # "公斤" 输入框
    def weight_field(self):
        return self.find_ele(name='公斤')

    """
        【 页 面 功 能 】
    """

    def iphone7_flow(self):
        """
        真机测试流程
        :return:
        """
        # 从屏幕'正中间'往'顶部'划动（效果：屏幕往'下'翻动）
        self.swipe_up()
        time.sleep(2)
        self.screenshot(image_name="iphone7_1.png")

        # 点击'身体测量'
        self.body_check_cron().click()
        time.sleep(2)
        self.screenshot(image_name="iphone7_2.png")

        # 点击'体重'
        self.weight_cron().click()
        time.sleep(2)
        self.screenshot(image_name="iphone7_3.png")

        # 点击'添加'
        self.add_cron().click()
        time.sleep(2)
        self.screenshot(image_name="iphone7_4.png")

        # '公斤'输入框 输入 65
        wf = self.weight_field()
        wf.click()
        wf.set_text("65")
        time.sleep(2)
        self.screenshot(image_name="iphone7_5.png")

        # 点击'添加'
        self.add_cron().click()
        time.sleep(2)

        # 验证 '平均值' 文本内容
        self.assert_content_and_screenshot(image_name="iphone7_6.png", content="平均值",
                                           error_msg="页面跳转失败！- 找不到'平均值'内容")

    def add_heart_rate_66(self, heart_rate):
        """
        添加心率66
        :return:
        """
        if "真机" in self.device_name:
            self.iphone7_flow()
        else:
            # 从屏幕'正中间'往'顶部'划动（效果：屏幕往'下'翻动）
            self.swipe_up()
            time.sleep(2)
            self.screenshot(image_name="heart_66_rate_1.png")

            # 点击 Browse 图标
            # self.touch_browser_cron()
            self.browser_cron().click()
            time.sleep(2)
            self.screenshot(image_name="heart_66_rate_2.png")

            # 搜索框输入 Heart
            search_input = self.search_field()
            self.log.info("search_input.name : " + str(search_input.name))
            self.log.info("search_input.bounds.width : " + str(search_input.bounds.width))
            self.log.info("search_input.bounds.height : " + str(search_input.bounds.height))
            search_input.click_exists(timeout=3.0)
            time.sleep(1)
            search_input.set_text("Heart")
            time.sleep(2)
            self.screenshot(image_name="heart_66_rate_3.png")

            # 判断"Nutrition"内容是否消失
            is_gone = self.content_is_gone("Nutrition", 4.0)
            self.log.info("内容 Nutrition 是否消失: " + str(is_gone))
            time.sleep(2)

            # 判断"Heart Rate"内容是否存在
            is_exist = self.content_is_exist("Heart Rate", 5.0)
            self.log.info("内容 Heart Rate 是否存在: " + str(is_exist))
            time.sleep(2)

            # 点击'心率'tab
            self.heart_rate_tab().click()
            time.sleep(2)
            self.screenshot(image_name="heart_66_rate_4.png")

            # 点击'添加数据'按钮
            self.add_data_btn().click()
            self.screenshot(image_name="heart_66_rate_5.png")

            # 输入心率数据
            bpm_input = self.bpm_field()
            bpm_input.click()
            bpm_input.set_text(heart_rate)
            time.sleep(2)
            self.screenshot(image_name="heart_66_rate_6.png")

            # 点击添加按钮
            self.add_btn().click()
            time.sleep(2)
            self.assert_content_and_screenshot(image_name="heart_66_rate_7.png", content="BPM",
                                               error_msg="页面跳转失败！- 找不到'BPM'内容")

    def add_heart_rate_33(self, heart_rate):
        """
        添加心率33
        :return:
        """
        if "真机" in self.device_name:
            self.iphone7_flow()
        else:
            # 从屏幕'正中间'往'底部'划（效果：屏幕往'上'翻动）
            self.swipe_down()
            time.sleep(2)
            self.screenshot(image_name="heart_33_rate_1.png")

            # 点击 Browse 图标
            # self.touch_browser_cron()
            self.browser_cron().click()
            time.sleep(2)
            self.screenshot(image_name="heart_33_rate_2.png")

            # 搜索框输入 Heart
            search_input = self.search_field()
            search_input.click_exists(timeout=3.0)
            time.sleep(1)
            search_input.set_text("Heart")
            time.sleep(2)
            self.screenshot(image_name="heart_33_rate_3.png")

            # 点击'心率'tab
            self.heart_rate_tab().click()
            time.sleep(2)
            self.screenshot(image_name="heart_33_rate_4.png")

            # 点击'添加数据'按钮
            self.add_data_btn().click()
            self.screenshot(image_name="heart_33_rate_5.png")

            # 输入心率数据
            bpm_input = self.bpm_field()
            bpm_input.click()
            bpm_input.set_text(heart_rate)
            time.sleep(2)
            self.screenshot(image_name="heart_33_rate_6.png")

            # 点击添加按钮
            self.add_btn().click()
            time.sleep(2)
            self.assert_content_and_screenshot(image_name="heart_33_rate_7.png", content="哈哈哈",
                                               error_msg="页面跳转失败！- 找不到'哈哈哈'内容")

    def add_heart_rate_11(self, heart_rate):
        """
        添加心率11
        :return:
        """
        if "真机" in self.device_name:
            self.iphone7_flow()
        else:
            # 从屏幕'正中间'往'底部'划（效果：屏幕往'上'翻动）
            self.swipe_down()
            time.sleep(2)
            self.screenshot(image_name="heart_11_rate_1.png")

            # 点击 Browse 图标
            # self.touch_browser_cron()
            self.browser_cron().click()
            time.sleep(2)
            self.screenshot(image_name="heart_11_rate_2.png")

            # 搜索框输入 Heart
            search_input = self.search_field()
            search_input.click_exists(timeout=3.0)
            time.sleep(1)
            search_input.set_text("Heart")
            time.sleep(2)
            self.screenshot(image_name="heart_11_rate_3.png")

            # 点击'心率'tab
            self.heart_rate_tab().click()
            time.sleep(2)
            self.screenshot(image_name="heart_11_rate_4.png")

            # 点击'添加数据'按钮
            self.add_data_btn().click()
            self.screenshot(image_name="heart_11_rate_5.png")

            # 输入心率数据
            bpm_input = self.bpm_field()
            bpm_input.click()
            bpm_input.set_text(heart_rate)
            time.sleep(2)
            self.screenshot(image_name="heart_11_rate_6.png")

            # 故意定位一个不存在的元素 导致错误
            self.search_field()

            # 点击添加按钮
            self.add_btn().click()
            time.sleep(2)
            self.assert_content_and_screenshot(image_name="heart_11_rate_7.png", content="11 BPM",
                                               error_msg="页面跳转失败！- 找不到'11 BPM'内容")