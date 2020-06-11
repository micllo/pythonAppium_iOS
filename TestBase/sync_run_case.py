# -*- coding:utf-8 -*-
from concurrent.futures import ThreadPoolExecutor
from unittest.suite import _isnotsuite
from types import MethodType
from Common.com_func import log, is_null
from Common.test_func import generate_report, send_DD_for_FXC, send_warning_after_test, is_exist_start_case, \
    stop_case_run_status, start_case_run_status, get_connected_ios_devices_info
from Tools.decorator_tools import async
import threading

"""
 [ 动态修改 suite.py 文件中 TestSuite 类中的 run 方法 ]

 def run(self, result, debug=False) 
    ......... 
    for index, test in enumerate(self):
        .........
        test(result) 
        .........

 self ：
 -> 表示 suite 实例对象（包含了所有的测试用例实例，即继承了'unittest.TestCase'的子类的实例对象 test_instance ）
 <unittest.suite.TestSuite tests=[<test_case.train_test.TrainTest testMethod=test_01>, 
                                  <test_case.train_test.TrainTest testMethod=test_02>, 
                                  <test_case.train_test.TrainTest testMethod=test_baidu>]>

 result:
 -> 表示 result.py 文件中的 TestResult 类的 实例对象

 test(result) ：等同于 test_instance(result)
 -> 表示 调用'unittest.TestCase'中的__call__方法执行该类中的 run 方法
 -> 理解：实例对象'test'通过'__call__'方法将自己变成一个函数来调用

"""


def run_test_custom(self, test, result, debug, index):
    """
    :param self: 表示'suit'实例对象
    :param test: 表示'测试用例'实例对象
    :param result: 测试结果报告
    :param debug:
    :param index:
    :return:

      多线程中执行的内容
       1.需要为实例对象'suite'<TestSuite>动态添加该方法
       2.目的：供多线程中调用
    """
    # 启动测试用例：设置用例的'运行状态=running'和'开始时间'
    start_case_run_status(pro_name=test.pro_name, test_method_name=test.test_method)

    # 获取当前线程名称 -> ThreadPoolExecutor-1_0
    thread_name = threading.currentThread().getName()
    # 获取当前线程名称索引+1，并赋值给实例对象的属性
    test.current_thread_name_index = int(thread_name.split("_")[1]) + 1

    if not debug:
        test(result)
    else:
        test.debug()

    # (self)实例对象'suite'<TestSuite> 为每个执行完毕的(test)'测试用例'实例 保存'截图ID列表'
    self.screen_shot_id_dict[test.class_method_name] = test.screen_shot_id_list

    # (self)实例对象'suite'<TestSuite> 为每个执行完毕的(test)'测试用例'实例 保存'使用的设备信息：name、width、height'
    # ->  { "测试类名.测试方法名": {"device_name": "iPhone8(模拟器)", "device_width": "375", "device_height": "667"},
    #       "测试类名.测试方法名": {"device_name": "iPhone7(真机)", "device_width": "540", "device_height": "960"} }
    self.ios_device_info_dict[test.class_method_name] = test.device_info

    if self._cleanup:
        self._removeTestAtIndex(index)

    # 停止测试用例：设置用例的'运行状态=stopping'和'运行时间'
    stop_case_run_status(pro_name=test.pro_name, test_method_name=test.test_method)

    # 返回值<'tuple'>：返回测试用例实例对象的两个属性值（ 项目名称、测试方法名 ）供回调函数使用
    return test.pro_name, test.test_method


def show_result_custom(res):
    """
    :param res: 某个线程执行完毕后的返回结果
    :return:

     多线程回调函数
      1.需要为实例对象'suite'<TestSuite>动态添加该方法
      2.目的：供多线程中调用
    """

    # 停止测试用例：设置用例的'运行状态=stopping'和'运行时间'
    result = res.result()
    stop_case_run_status(pro_name=result[0], test_method_name=result[1])


def new_run(self, result, debug=False):
    """
    :param self: 表示'suit'实例对象
    :param result: 测试结果报告
    :param debug:
    :return:

     动态修改'suite.py'文件中'TestSuite'类中的'run'方法
      1.为实例对象'suite'<TestSuite>动态修改实例方法'run'
      2.目的：启用多线程来执行case
    """
    topLevel = False
    if getattr(result, '_testRunEntered', False) is False:
        result._testRunEntered = topLevel = True

    # 多线程执行测试
    pool = ThreadPoolExecutor(self.thread_num)
    for index, test in enumerate(self):
        if result.shouldStop:
            break

        if _isnotsuite(test):
            self._tearDownPreviousClass(test, result)
            self._handleModuleFixture(test, result)
            self._handleClassSetUp(test, result)
            result._previousTestClass = test.__class__

            if (getattr(test.__class__, '_classSetupFailed', False) or
                    getattr(result, '_moduleSetUpFailed', False)):
                continue

        """ 启用多线程 调用方法 """
        pool.submit(run_test_custom, self, test, result, debug, index).add_done_callback(show_result_custom)

    """ 等待所有线程执行完毕 """
    pool.shutdown()

    log.info("线程全部执行完毕")

    if topLevel:
        self._tearDownPreviousClass(None, result)
        self._handleModuleTearDown(result)
        result._testRunEntered = False
    return result


@async
def suite_sync_run_case(pro_name, connected_ios_device_list=[]):
    """
    同时执行不同用例（ 通过动态修改'suite.py'文件中'TestSuite'类中的'run'方法，使得每个线程中的结果都可以记录到测试报告中 ）
    :param pro_name: 项目名称
    :param connected_ios_device_list: 已连接的设备列表 （ 以 列表数量 作为 线程数量 ）
            （1）若 == [] ：表示当前是'定时任务'
            （2）若 =! [] ：表示当前是'页面执行'，并且 已经获取到已连接的iOS设备

        【 备 注 】
        1.suite 实例对象（包含了所有的测试用例实例，即继承了'unittest.TestCase'的子类的实例对象 test_instance ）
        2.启动 iOS 设备中的 APP 应用（每个用例执行一次）：在每个'测试类'的 setUp 方法中执行 ( 继承 ParaCase 父类 )
        3.关闭 iOS 设备中的 APP 应用 （每个用例执行一次）：在每个'测试类'的 tearDown 方法中执行 ( 继承 ParaCase 父类 )

        【 保 存 截 屏 图 片 ID 的 逻 辑 】
        1.为实例对象'suite'<TestSuite>动态添加一个属性'screen_shot_id_dict' -> screen_shot_id_dict = {}
        2.每个测试方法中将所有截屏ID都保存入'screen_shot_id_list' -> screen_shot_id_dict = ['aaa', 'bbb', 'ccc']
        3.实例对象'suite'在重写的'new_run'方法中 将'screen_shot_id_list'添加入'screen_shot_id_dict'
        4.screen_shot_id_dict = { "测试类名.测试方法名":['aaa', 'bbb'], "测试类名.测试方法名":['cccc'] }

        【 并 发 线 程 数 逻 辑 】
        1.通过 ps aux 命令 查看 WDA服务连接的iOS设备情况
        2.将'已连接'的设备列表数量 作为 并发线程数量
        [ { "thread_index":1,"device_name":"iPhone 8(模拟器)","wda_port":"8100","wda_destination":"name=iPhone 8","appium_server","http://xxx:4723/wd/hub","platform_version":"","device_udid":"" } } ,
          { "thread_index":2,"device_name":"iPhone 7(真机)",  "wda_port":"8200","wda_destination":"id=xxxxxxxxx", "appium_server","http://xxx:4733/wd/hub","platform_version":"","device_udid":"" } } ]

        【 每 个 用 例 使 用 iOS 设 备 逻 辑 】
        通过'当前线程名索引' 获取已连接设备列表中对应的'iOS'设备信息

    """

    if is_null(connected_ios_device_list):  # 表示当前是'定时任务'

        # （定时任务）需要判断 是否存在运行中的用例
        if is_exist_start_case(pro_name):
            send_DD_for_FXC(title=pro_name, text="#### '" + pro_name + "' 项目存在<运行中>的用例而未执行测试（定时任务）")
            return "Done"

        # （定时任务）需要获取 已连接的 iOS 设备信息列表
        connected_ios_device_list = get_connected_ios_devices_info(pro_name)
        if len(connected_ios_device_list) == 0:
            send_DD_for_FXC(title=pro_name, text="#### '" + pro_name + "' 项目 未连接任何 iOS 设备")
            return "Done"

    # '已连接设备的' 列表数量 作为 线程数量
    log.info("线程数量 ： " + str(len(connected_ios_device_list)))
    log.info("已连接的iOS设备信息列表：" + str(connected_ios_device_list) + "\n")

    # 将'测试类'中的所有'测试方法'添加到 suite 对象中（每个'测试类'实例对象包含一个'测试方法'）
    from TestBase.test_case_unit import ParaCase
    suite, on_line_test_method_name_list = ParaCase.get_online_case_to_suite(pro_name, connected_ios_device_list)

    if suite != "mongo error":
        if is_null(on_line_test_method_name_list):
            send_DD_for_FXC(title=pro_name, text="#### '" + pro_name + "' 项目<没有上线>的用例而未执行测试（定时任务）")
        else:
            # 为实例对象'suite'<TestSuite>动态添加一个属性'screen_shot_id_dict'（目的：保存截图ID）
            setattr(suite, "screen_shot_id_dict", {})

            # 为实例对象'suite'<TestSuite>动态添加一个属性'ios_device_info_dict'（目的：保存使用的设备信息：name、width、height）
            setattr(suite, "ios_device_info_dict", {})

            # 为实例对象'suite'<TestSuite>动态添加一个属性'thread_num'（目的：控制多线程数量）
            setattr(suite, "thread_num", len(connected_ios_device_list))

            # 为实例对象'suite'<TestSuite>动态添加两个方法'run_test_custom'、'show_result_custom'（ 目的：供多线程中调用 ）
            suite.run_test_custom = MethodType(run_test_custom, suite)
            suite.show_result_custom = MethodType(show_result_custom, suite)

            # 为实例对象'suite'<TestSuite>动态修改实例方法'run'（ 目的：启用多线程来执行case ）
            suite.run = MethodType(new_run, suite)

            # 运行测试，并生成测试报告
            test_result, current_report_file = generate_report(pro_name=pro_name, suite=suite, title='iOS自动化测试报告 - ' + pro_name,
                                                               description='详细测试用例结果', tester="自动化测试", verbosity=2)

            # 测试后发送预警
            # send_warning_after_test(pro_name, test_result, current_report_file)


if __name__ == "__main__":
    suite_sync_run_case(pro_name="pro_demo_1")

