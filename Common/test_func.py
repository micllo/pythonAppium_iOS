# -*- coding:utf-8 -*-
from TestBase.HTMLTestReport import HTMLTestRunner
import time
import os
from Common.com_func import send_mail, mkdir, send_DD, log
from Env import env_config as cfg
from dateutil import parser
from Tools.date_helper import get_current_iso_date
import subprocess
from fabric.api import *


def generate_report(pro_name, suite, title, description, tester, verbosity=1):
    """
    生 成 测 试 报 告
    备注：每次生成的报告都存放在../logs/history/中，同时替换../logs/下的report.html
    :param pro_name:
    :param suite: suite 实例对象（包含了所有的测试用例实例，即继承了'unittest.TestCase'的子类的实例对象 test_instance ）
    :param title:
    :param description:
    :param tester:
    :param verbosity: 结果显示的详细程度
    :return:
    """
    print("实例对象suite是否存在'thread_num'属性：" + str(hasattr(suite, "thread_num")))
    print("实例对象suite是否存在'screen_shot_id_dict'属性：" + str(hasattr(suite, "screen_shot_id_dict")))
    print("实例对象suite是否存在'run_test_custom'方法：" + str(hasattr(suite, "run_test_custom")))
    print("实例对象suite是否存在'show_result_custom'方法：" + str(hasattr(suite, "show_result_custom")))
    print("实例对象suite是否存在'run'方法：" + str(hasattr(suite, "run")))
    print(suite)
    print(suite.__class__)
    print(suite.__class__.__base__)
    print("+++++++++++++++++++++++++++++++++++")

    now = time.strftime("%Y-%m-%d_%H_%M_%S", time.localtime(time.time()))
    current_report_name = "[iOS_report]" + pro_name + "[" + now + "].html"
    pro_report_path = cfg.REPORTS_DIR + pro_name + "/"
    history_report_path = pro_report_path + "history/"
    mkdir(history_report_path)
    current_report_file = history_report_path + current_report_name
    with open(current_report_file, 'wb') as fp:
        runner = HTMLTestRunner(stream=fp, title=title, description=description, tester=tester, verbosity=verbosity)
        test_result = runner.run(suite)

    # 将最新报告替换../Reports/{{pro_name}}/下的[iOS_report]{{pro_name}}.html
    res = os.system("cp " + current_report_file + " " + pro_report_path + " && "
                    "mv " + pro_report_path + current_report_name + " " + pro_report_path + "[iOS_report]" + pro_name + ".html")
    if res != 0:
        log.error("测试报告替换操作有误！")

    # log.info(test_result)
    # log.info("执行总数：" + str(test_result.error_count + test_result.success_count + test_result.failure_count))
    # log.info("执行的用例列表：" + str(test_result.result))
    # log.info("错误数：" + str(test_result.error_count))
    # log.info("错误的用例列表：" + str(test_result.errors))
    # log.info("失败数：" + str(test_result.failure_count))
    # log.info("失败的用例列表：" + str(test_result.failures))
    # log.info("成功数：" + str(test_result.success_count))
    # log.info("成功的用例列表：" + str([success[1] for success in test_result.result if success[0] == 0]))
    # log.info(suite.screen_shot_id_dict)
    return test_result, current_report_file


def send_warning_after_test(pro_name, test_result, report_file):
    """
       测 试 后 发 送 预 警 （ 邮件、钉钉 ）
       :param pro_name:
       :param test_result:
       :param report_file:
       :return:
       error_type 标识：
         (1)有'失败'的，则标记为'失败'
         (2)无'失败'、有'错误'的，则标记为'错误'
         (3)无'失败'、无'错误'的，则标记为'None'
    """
    report_name = report_file.split("/")[-1]
    error_type = (test_result.failure_count > 0 and "失败" or (test_result.error_count > 0 and "错误" or None))
    if error_type:
        send_mail_after_test(error_type=error_type, report_name=report_name, report_file=report_file, pro_name=pro_name)
        send_DD_after_test(error_type=error_type, report_name=report_name, pro_name=pro_name, is_at_all=(error_type == "失败" and True or False))


def send_mail_after_test(error_type, report_name, report_file, pro_name):
    """
    测 试 后 发 送 邮 件
    :param error_type: "失败"、"错误"
    :param report_name:
    :param report_file:
    :param pro_name:
    :return:
    """
    subject = "iOS自动化测试'" + report_name.split(".")[-2] + "'存在'" + error_type + "'的用例"
    content = "在'" + report_name + "'测试报告中 存在'" + error_type + "'的用例\n测试报告地址： " + cfg.BASE_REPORT_PATH + pro_name + "/history/" + report_name
    send_mail(subject=subject, content=content, to_list=cfg.MAIL_LIST, attach_file=report_file)


def send_DD_after_test(error_type, report_name, pro_name, is_at_all=False):
    """
    测 试 后 发 送 钉 钉
    :param error_type: "失败"、"错误"
    :param report_name:
    :param pro_name:
    :param is_at_all:
    :return:

    """
    text = "#### 在'" + report_name + "'测试报告中 存在'" + error_type + "'的用例\n\n ***测试报告地址***\n" + cfg.BASE_REPORT_PATH + pro_name + "/history/" + report_name
    send_DD(dd_group_id=cfg.DD_MONITOR_GROUP, title=report_name, text=text, at_phones=cfg.DD_AT_PHONES, is_at_all=is_at_all)


def send_DD_for_FXC(title, text):
    """
    发 送 钉 钉 to FXC
    :param title:
    :param text:
    :return:

    """
    send_DD(dd_group_id=cfg.DD_MONITOR_GROUP, title=title, text=text, at_phones=cfg.DD_AT_FXC, is_at_all=False)


def mongo_exception_send_DD(e, msg):
    """
    发现异常时钉钉通知
    :param e:
    :param msg:
    :return:
    """
    title = "'mongo'操作通知"
    text = "#### iOS自动化测试'mongo'操作错误\n\n****操作方式：" + msg + "****\n\n****错误原因：" + str(e) + "****"
    send_DD(dd_group_id=cfg.DD_MONITOR_GROUP, title=title, text=text, at_phones=cfg.DD_AT_FXC, is_at_all=False)


def is_exist_start_case(pro_name):
    """
    判断项目是否存在 启动的用例（pending、running）
    :param pro_name:
    :return:
      判断逻辑：若存在'pending'或'running',则表示存在启动的用例
      备注：若返回'mongo error', 默认表示'存在'运行中的用例
    """
    from Tools.mongodb import MongodbUtils
    with MongodbUtils(ip=cfg.MONGODB_ADDR, database=cfg.MONGODB_DATABASE, collection=pro_name) as pro_db:
        try:
            results = pro_db.find({}, {"_id": 0})
            run_status_list = [res.get("run_status") for res in results]
        except Exception as e:
            mongo_exception_send_DD(e=e, msg="获取'" + pro_name + "'项目测试用例列表")
            return "mongo error"
    return "pending" in run_status_list or "running" in run_status_list


def is_exist_online_case(pro_name):
    """
    判断项目是否存在 上线的用例
    :param pro_name:
    :return:
    """
    from Tools.mongodb import MongodbUtils
    with MongodbUtils(ip=cfg.MONGODB_ADDR, database=cfg.MONGODB_DATABASE, collection=pro_name) as pro_db:
        try:
            results = pro_db.find({}, {"_id": 0})
            case_status_list = [res.get("case_status") for res in results]
        except Exception as e:
            mongo_exception_send_DD(e=e, msg="获取'" + pro_name + "'项目测试用例列表")
            return "mongo error"
    return True in case_status_list and True or False


def start_case_run_status(pro_name, test_method_name):
    """
    启动测试用例：设置用例的'运行状态=running'和'开始时间'
    :param pro_name:
    :param test_method_name:
    :return:
    """
    from Tools.mongodb import MongodbUtils
    with MongodbUtils(ip=cfg.MONGODB_ADDR, database=cfg.MONGODB_DATABASE, collection=pro_name) as pro_db:
        try:
            query_dict = {"test_method_name": test_method_name}
            update_dict = {"$set": {"run_status": "running", "start_time": get_current_iso_date()}}
            pro_db.update(query_dict, update_dict, multi=True)
        except Exception as e:
            mongo_exception_send_DD(e=e, msg="启动'" + pro_name + "'项目中的测试用例")
            return "mongo error"


def stop_case_run_status(pro_name, test_method_name):
    """
    停止测试用例：设置用例的'运行状态=stopping'和'运行时间'
    :param pro_name:
    :param test_method_name:
    :return:
    """
    from Tools.mongodb import MongodbUtils
    with MongodbUtils(ip=cfg.MONGODB_ADDR, database=cfg.MONGODB_DATABASE, collection=pro_name) as pro_db:
        try:
            # 获取 开始时间
            query_dict = {"test_method_name": test_method_name}
            result = pro_db.find_one(query_dict, {"_id": 0})
            start_time = result.get("start_time")
            # 获取 当前时间
            now_str = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time()))
            now_time = parser.parse(now_str)
            # 更新数据
            update_dict = {"$set": {"run_status": "stopping", "run_time": str(now_time - start_time)}}
            print(update_dict)
            pro_db.update(query_dict, update_dict)
        except Exception as e:
            mongo_exception_send_DD(e=e, msg="停止'" + pro_name + "'项目中的测试用例")
            return "mongo error"


def get_connected_ios_devices_info(pro_name):
    """
    【 获取 已连接的 iOS 设备信息列表 】
     1.通过'SSH'登录'WDA'服务器
     2.获取 配置的 iOS 设备信息列表
     3.通过 ps aux 命令 查看 WDA服务连接的iOS设备情况
     （1）-destination "platform=iOS Simulator,name=iPhone 8"
     （2）-destination "platform=iOS Simulator,name=iPhone 11"
     （3）-destination "id=3cbb25d055753f2305ec70ba6dede3dca5d500bb"
     4.将'已连接'的设备增加其对应的'thread_index'，并保存入列表
     5.将'未连接'的设备，发送钉钉通知

     [ { "thread_index": 1, "device_name": "iPhone8(模拟器)", "wda_port": "8100", "wda_destination": "platform=iOS Simulator,name=iPhone 8" } } ,
       { "thread_index": 2, "device_name": "iPhone7(真机)", "wda_port": "8200", "wda_destination": "id=3cbb25d055753f2305ec70ba6dede3dca5d500bb" } } ]

     :return: 已连接设备信息列表

    【 备注 】
    1.若 SSH 登录失败，则返回 空列表
    2.本地执行命令：subprocess.check_output(["ps", "aux", "|", "grep", "-v", "\"grep\"", "|", "grep", "WebDriverAgentRunner"], shell=True)

    """
    # 获取 配置的 iOS 设备信息列表
    from Config.pro_config import config_ios_device_list
    ios_device_list = config_ios_device_list()
    device_num = 0
    connected_ios_device_list = []

    with settings(host_string="%s@%s:%s" % (cfg.WDA_SERVER_USER, cfg.WDA_SERVER_HOST, cfg.WDA_SERVER_PORT),
                  password=cfg.WDA_SERVER_PASSWD):
        try:
            cmd_res = run("ps -ef | grep -v \"grep\" | grep WebDriverAgentRunner", warn_only=True)  # 忽略失败的命令,继续执行
            # 若 iOS 设备对应的 destination 出现在查询结果中则保存入列表
            for ios_device_dict in ios_device_list:
                if "-destination " + ios_device_dict["wda_destination"] in str(cmd_res):
                    device_num += 1
                    connected_ios_device_dict = ios_device_dict
                    connected_ios_device_dict["thread_index"] = device_num
                    connected_ios_device_list.append(connected_ios_device_dict)
                else:
                    send_DD_for_FXC(title=pro_name, text="#### " + pro_name + " 项目 " + ios_device_dict["device_name"] + " 设 备 未 连 接 WDA 服 务")
        except Exception as e:
            print(str(e))
            send_DD_for_FXC(title=pro_name, text="#### " + pro_name + " 项目 通过'SSH'登录'WDA'服务器失败，无法获取iOS设备连接情况")

    return connected_ios_device_list


if __name__ == "__main__":
    pass
    # send_DD_after_test("失败", "报告名称", False)
    # print(get_test_case(pro_name="pro_demo_1"))
    # print(is_exist_online_case(pro_name="pro_demo_1"))
    # stop_case_run_status("pro_demo_1", "test_demo_01")

    print(get_connected_ios_devices_info("pro_demo_1"))

