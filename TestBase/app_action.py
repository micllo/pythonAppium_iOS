# -*- coding:utf-8 -*-
from Common.com_func import project_path, log, mkdir
from Env import env_config as cfg
from Config import global_var as gv
import time
from Tools.mongodb import MongoGridFS
from Common.test_func import send_DD_for_FXC
import wda


def get_ios_client(pro_name, current_thread_name_index, connected_ios_device_list):
    """
    【 获取'iOS'驱动、设备名称 】
    :param pro_name
    :param current_thread_name_index: 当前线程名字的索引
    :param connected_ios_device_list: 已连接设备信息列表
    [ { "thread_index": 1, "device_name": "iPhone8(模拟器)", "wda_port": "8100", "wda_destination": "platform=iOS Simulator,name=iPhone 8" } } ,
      { "thread_index": 2, "device_name": "iPhone11(模拟器)", "wda_port": "8200", "wda_destination": "platform=iOS Simulator,name=iPhone 11" } }, ]
      { "thread_index": 2, "device_name": "iPhone7(真机)", "wda_port": "8200", "wda_destination": "id=3cbb25d055753f2305ec70ba6dede3dca5d500bb" } } ]
    :return:

    【 步 骤 】
    1.通过'当前线程名索引' 获取已连接设备列表中对应的'Android'设备信息和'Appium'服务
    2.获取设备驱动
    """

    # 通过'当前线程名索引' 获取已连接设备列表中对应的'iOS'设备信息
    device_name = None
    wda_port = None
    for connected_android_devices_dict in connected_ios_device_list:
        if current_thread_name_index == connected_android_devices_dict["thread_index"]:
            wda_port = connected_android_devices_dict["wda_port"]
            device_name = connected_android_devices_dict["device_name"]
            break
    log.info("\n\n")
    log.info("device_name -> " + device_name)
    log.info("wda_port -> " + wda_port)
    log.info("\n\n")

    client = None
    try:
        # 连接设备(通过WDA服务在设备的的监听端口)
        client = wda.Client("http://" + cfg.SERVER_IP + ":" + wda_port)

        # 等待 WDA 服务启动
        client.wait_ready(timeout=gv.WAIT_WDA_READY)

        # 设置 client 默认的元素定位超时时间 (注：在本框架中作用不大，见 find_ele 方法)
        # client.implicitly_wait(gv.IMPLICITY_WAIT)

        # 解锁（点亮屏幕）相当于点击了home健
        client.unlock()

    except Exception as e:
        log.error(("显示异常：" + str(e)))
        if "Failed to establish a new connection" in str(e):
            error_msg = pro_name + " 项目 " + device_name + " 设备 启动 WDA 服务 失败"
        else:
            error_msg = pro_name + "项目 " + device_name + " 设备 启动 WDA 服务的其他异常情况"
        send_DD_for_FXC(title=pro_name, text="#### " + error_msg + "")
        raise Exception(error_msg)
    finally:
        return client, device_name


class Base(object):

    def __init__(self, case_instance):
        """
        【 备 注 】 更多的元素定位方式，参考 facebook_wda.py 文件

        """
        self.case_instance = case_instance    # 测试用例的实例对象
        self.client = case_instance.client    # 操作 iOS 设备
        self.session = case_instance.session  # 操作 APP 应用
        self.device_name = case_instance.device_name
        self.log = log

    def find_ele(self, **kwargs):
        ele = self.session(**kwargs)
        if ele.wait(timeout=gv.IMPLICITY_WAIT, raise_error=True):  # 设置 Session 定位等待时间
            return ele
        else:
            raise Exception("元素定位失败")

    def click(self, *args):
        self.find_ele(*args).click()

    def click_exists(self, timeout, *args):
        """
        定位的元素若存在，则进行点击操作（设置等待时间）
        :param timeout: 等待元素超时时间
        :param args:
        :return:
        """
        self.find_ele(*args).click_exists(timeout)

    def content_is_exist(self, content, time_out):
        """
        判断页面内容是否存在
        （1）若存在：  True
        （2）若不存在：False
        :param content:
        :param time_out:
        :return:
        """
        time_init = 1   # 初始化时间
        polling_interval = 1  # 轮询间隔时间
        while content not in self.session.source():
        # while not self.session(text=content).exists:
            time.sleep(polling_interval)
            time_init = time_init + 1
            if time_init >= time_out:
                return False
        return True

    def content_is_gone(self, content, time_out):
        """
        判断页面内容是否消失
        （1）若消失：True
        （2）若存在：False
        :param content:
        :param time_out:
        :return:
        """
        return self.session(text=content).wait_gone(timeout=time_out)

    def screenshot(self, image_name):
        """
         截 图、保 存 mongo、记录图片ID
        :param image_name: 图片名称

        【 使 用 case_instance 逻 辑 】
        1.若'Base类的子类实例对象'调用该方法（在 object_page 中使用）：则使用该实例对象本身的 self.case_instance 属性（测试用例实例对象）
        2.若'Base类'调用该方法（在 test_case 中使用）：则使用该 self 测试用例实例对象本身
        3.由于'Base'类和'测试用例类'都含有'client'属性，所以不影响self.client的使用
        :return:
        """
        # 判断当前的'实例对象'是否是'Base'类型（考虑子类的继承关系）
        case_instance = isinstance(self, Base) and self.case_instance or self
        # 获取当前测试用例的路径 -> ../类名/方法名/
        current_test_path = cfg.SCREENSHOTS_DIR + case_instance.pro_name + "/" + case_instance.class_method_path
        mkdir(current_test_path)
        self.session.screenshot(current_test_path + image_name)
        mgf = MongoGridFS()
        files_id = mgf.upload_file(img_file_full=current_test_path + image_name)
        case_instance.screen_shot_id_list.append(files_id)

    def assert_content_and_screenshot(self, image_name, content, error_msg):
        """
        断言内容是否存在、同时截屏
        :param image_name: 图片名称
        :param content: 需要轮询的内容
        :param error_msg: 断言失败后的 错误提示
        :return:
        """
        is_exist = True
        time_init = 1   # 初始化时间
        polling_interval = 1  # 轮询间隔时间
        while content not in self.session.source():
        # while not self.session(text=content).exists:
            time.sleep(polling_interval)
            time_init = time_init + 1
            if time_init >= gv.POLLING_CONTENT_TIME_OUT:
                is_exist = False
                break
        self.screenshot(image_name)
        self.case_instance.assertTrue(is_exist, error_msg)

    def touch_click(self, x, y):
        """
        触摸点击
        :param x: 横坐标（从左上角开始）
        :param y: 从坐标（从左上角开始）
        :return:
        """
        self.session.tap(x, y)

    def swipe_up(self):
        """
        从屏幕'正中间'往'顶部'划动（效果：屏幕往'下'翻动）
        :return:
        """
        self.session.swipe_up()

    def swipe_down(self):
        """
        从屏幕'正中间'往'底部'划（效果：屏幕往'上'翻动）
        :return:
        """
        self.session.swipe_down()

    def swipe_left(self):
        """
        从屏幕'中间最右侧'往'中间最左侧'划（效果：屏幕往'右'翻动）
        :return:
        """
        self.session.swipe_left()

    def swipe_right(self):
        """
        从屏幕'中间最左侧'往'中间最右侧'划（效果：屏幕往'左'翻动）
        :return:
        """
        self.session.swipe_right()


if __name__ == "__main__":
    print(project_path())

