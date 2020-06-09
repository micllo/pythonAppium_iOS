# -*- coding:utf-8 -*-
from Env import env_config as cfg
from Common.com_func import log, is_null
from Common.test_func import mongo_exception_send_DD
import os
from Tools.mongodb import MongoGridFS
from Tools.date_helper import get_date_by_days
from Tools.mongodb import MongodbUtils
import unittest
from Config.pro_config import get_test_class_list
from Tools.date_helper import get_current_iso_date
# sys.path.append("./")


"""
api 服务底层的业务逻辑
"""


def sync_run_case(pro_name, connected_ios_device_list):
    """
    同时执行不同的用例
    :param pro_name
    :param connected_ios_device_list: 已连接的设备列表
    :return:
    """
    from TestBase.sync_run_case import suite_sync_run_case
    suite_sync_run_case(pro_name=pro_name, connected_ios_device_list=connected_ios_device_list)


def clear_reports_logs(time, pro_name):
    """
    删除指定时间之前 生成的报告和日志
      -mmin +1 -> 表示1分钟前的
      -mtime +1 -> 表示1天前的
    :param time:
    :param pro_name:
    :return:
    """
    rm_log_cmd = "find '" + cfg.LOGS_DIR + "' -name '*.log' -mmin +" + str(time) + " -type f -exec rm -rf {} \\;"
    rm_report_cmd = "find '" + cfg.REPORTS_DIR + pro_name + "/history' -name '*.html' -mmin +" + str(time) + \
                    " -type f -exec rm -rf {} \\;"
    print(rm_log_cmd)
    print(rm_report_cmd)
    os.system(rm_log_cmd)
    os.system(rm_report_cmd)


def clear_screen_shot(days):
    """
    删除指定日期之前的所有的截图
    :param days:
    :return:
    """
    date_str = get_date_by_days(days=days, time_type="%Y-%m-%dT%H:%M:%S")
    mgf = MongoGridFS()
    del_num = mgf.del_file_by_date(date_str)
    if is_null(del_num):
        log.error("\n清理'" + date_str + "'之前的截图时出错了！\n")
    else:
        log.info("\n已清理'" + date_str + "'之前的截图：" + str(del_num) + " 个\n")


def case_import_mongo(pro_name):
    """
    更新项目测试用例数据 同步入mongo库中，默认状态为'下线'
    :param pro_name:
    :return:
    【 备 注 】
    1.run_status ：运行状态 （ pending 待运行、runninng 运行中、stopping 已停止）
    2.start_time ：运行开始时间
    3.run_time ：运行时间
    """
    test_class_list = get_test_class_list(pro_name)
    if test_class_list:
        insert_list = []
        test_loader = unittest.TestLoader()
        for test_class in test_class_list:
            test_methods_name = test_loader.getTestCaseNames(test_class)
            for test_method_name in test_methods_name:
                # 生成'测试方法'的实例对象，并反射获取'测试方法'
                test_instance = test_class(pro_name=pro_name, test_method=test_method_name)
                testMethod = getattr(test_instance, test_method_name)
                # 获取'测试方法'中的备注，作为'测试用例名称'
                test_case_name = testMethod.__doc__.split("\n")[0].strip()
                test_case_dict = {}
                test_case_dict["pro_name"] = pro_name
                test_case_dict["test_class_name"] = test_class.__name__
                test_case_dict["test_method_name"] = test_method_name
                test_case_dict["test_case_name"] = test_case_name
                test_case_dict["case_status"] = False
                test_case_dict["run_status"] = "stopping"
                test_case_dict["start_time"] = "----"
                test_case_dict["run_time"] = "----"
                test_case_dict["create_time"] = get_current_iso_date()
                insert_list.append(test_case_dict)
        # 将'测试用例'列表更新入对应项目的数据库中
        with MongodbUtils(ip=cfg.MONGODB_ADDR, database=cfg.MONGODB_DATABASE, collection=pro_name) as pro_db:
            try:
                pro_db.drop()
                pro_db.insert_many(insert_list)
            except Exception as e:
                mongo_exception_send_DD(e=e, msg="更新'" + pro_name + "'项目测试用例数据")
                return "mongo error"
        return insert_list
    else:
        return "no such pro"


def update_case_status(pro_name, test_method_name):
    """
    更新项目测试用例状态
    :param pro_name:
    :param test_method_name:
    :return:
    """
    with MongodbUtils(ip=cfg.MONGODB_ADDR, database=cfg.MONGODB_DATABASE, collection=pro_name) as pro_db:
        try:
            query_dict = {"test_method_name": test_method_name}
            result = pro_db.find_one(query_dict, {"_id": 0})
            old_case_status = result.get("case_status")
            new_case_status = bool(1 - old_case_status)  # 布尔值取反
            update_dict = {"$set": {"case_status": new_case_status}}
            pro_db.update_one(query_dict, update_dict)
            return new_case_status
        except Exception as e:
            mongo_exception_send_DD(e=e, msg="更新'" + pro_name + "'项目测试用例状态(单个)")
            return "mongo error"


def update_case_status_all(pro_name, case_status=False):
    """
    更新项目所有测试用例状态(上下线)
    :param pro_name:
    :param case_status:
    :return: 返回 test_method_name_list 列表
    """
    with MongodbUtils(ip=cfg.MONGODB_ADDR, database=cfg.MONGODB_DATABASE, collection=pro_name) as pro_db:
        try:
            update_dict = {"$set": {"case_status": case_status}}
            pro_db.update({}, update_dict, multi=True)
            results = pro_db.find({}, {"_id": 0})
            return [res.get("test_method_name") for res in results]
        except Exception as e:
            mongo_exception_send_DD(e=e, msg="更新'" + pro_name + "'项目所有测试用例状态")
            return "mongo error"


def get_test_case(pro_name):
    """
    根据项目获取测试用例列表（上线的排在前面）
    :param pro_name:
    :return: 返回值
    """
    test_case_list = []
    on_line_list = []
    off_line_list = []
    with MongodbUtils(ip=cfg.MONGODB_ADDR, database=cfg.MONGODB_DATABASE, collection=pro_name) as pro_db:
        try:
            results = pro_db.find({}, {"_id": 0})
            for res in results:
                test_case_dict = dict()
                test_case_dict["case_status"] = res.get("case_status")
                test_case_dict["test_case_name"] = res.get("test_case_name")
                test_case_dict["test_class_name"] = res.get("test_class_name")
                test_case_dict["test_method_name"] = res.get("test_method_name")
                test_case_dict["run_status"] = res.get("run_status")
                test_case_dict["start_time"] = res.get("start_time")
                test_case_dict["run_time"] = res.get("run_time")
                test_case_dict["create_time"] = res.get("create_time")
                if res.get("case_status"):
                    on_line_list.append(test_case_dict)
                else:
                    off_line_list.append(test_case_dict)
            test_case_list = on_line_list + off_line_list
        except Exception as e:
            mongo_exception_send_DD(e=e, msg="获取'" + pro_name + "'项目测试用例列表")
            return "mongo error"
        finally:
            return test_case_list


def stop_case_run_status(pro_name):
    """
    强行修改项目用例运行状态 -> 停止
    :param pro_name:
    :return:
    """
    with MongodbUtils(ip=cfg.MONGODB_ADDR, database=cfg.MONGODB_DATABASE, collection=pro_name) as pro_db:
        try:
            update_dict = {"$set": {"run_status": "stopping"}}
            pro_db.update({}, update_dict, multi=True)
            return True
        except Exception as e:
            mongo_exception_send_DD(e=e, msg="强行修改'" + pro_name + "'项目用例运行状态")
            return "mongo error"


def get_case_run_status(pro_name):
    """
    获取项目用例的运行状态
    :param pro_name:
    :return:
    """
    case_run_status_list = []
    with MongodbUtils(ip=cfg.MONGODB_ADDR, database=cfg.MONGODB_DATABASE, collection=pro_name) as pro_db:
        try:
            results = pro_db.find({"case_status": True}, {"_id": 0})
            for res in results:
                test_case_dict = dict()
                test_case_dict["test_method_name"] = res.get("test_method_name")
                test_case_dict["run_status"] = res.get("run_status")
                test_case_dict["start_time"] = str(res.get("start_time"))
                test_case_dict["run_time"] = str(res.get("run_time"))
                case_run_status_list.append(test_case_dict)
            return case_run_status_list
        except Exception as e:
            mongo_exception_send_DD(e=e, msg="获取'" + pro_name + "'项目用例的运行状态")
            return "mongo error"


def get_progress_info(pro_name):
    """
    获取项目用例执行进度信息：总执行数(上线数)、已执行数(上线数中'已停止'的数量)、进度百分比
    :param pro_name:
    :return:
    """
    with MongodbUtils(ip=cfg.MONGODB_ADDR, database=cfg.MONGODB_DATABASE, collection=pro_name) as pro_db:
        try:
            progress_info = dict()
            results = pro_db.find({"case_status": True})
            on_line_run_status_list = [res.get("run_status") for res in results]
            run_num = len(on_line_run_status_list)
            if run_num == 0:
                progress_info["run_num"] = 0
                progress_info["done_num"] = 0
                progress_info["percent"] = 0
            else:
                progress_info["run_num"] = run_num
                # 将 '上线的运行状态列表'中'run_status=stopping'的运行状态保存入列表
                has_stop_run_status_list = [run_status for run_status in on_line_run_status_list if run_status == "stopping"]
                stop_num = len(has_stop_run_status_list)
                progress_info["done_num"] = stop_num
                # 计算百分比
                percent = int(float(stop_num) / float(run_num) * 100)
                progress_info["percent"] = percent
            return progress_info
        except Exception as e:
            mongo_exception_send_DD(e=e, msg="获取'" + pro_name + "项目用例执行进度信息")
            return "mongo error"


if __name__ == "__main__":
    pass
    # clear_screen_shot(4)
    # case_import_mongo("pro_demo_1")
    # update_case_status("pro_demo_1", "test_02")
    # update_case_status_all(pro_name="pro_demo_1", status=False)
    # get_progress_info("pro_demo_1")
    print(get_case_run_status("pro_demo_1"))