from Env import env_config as cfg
from Project.pro_demo_1.test_case.demo_test import HealthTest


def get_test_class_list(pro_name):
    """
    通过'项目名'获取'测试类'列表
    :param pro_name:
    :return:
    """
    if pro_name == "pro_demo_1":
        test_class_list = [HealthTest]
    else:
        test_class_list = None
    return test_class_list


def pro_exist(pro_name):
    """
    判断项目名称是否存在
    :param pro_name:
    :return:
    """
    pro_name_list = ["pro_demo_1", "pro_demo_2"]
    if pro_name in pro_name_list:
        return True
    else:
        return False


def get_login_accout(current_thread_name_index):
    """
    通过线程名的索引 获取登录账号
    :param current_thread_name_index:
    :return:
    """
    if current_thread_name_index == 1:
        return "user_1", "passwd_1"
    elif current_thread_name_index == 2:
        return "user_2", "passwd_2"
    else:
        return "user_3", "passwd_3"


def get_app_bundleId(pro_name):
    """
    通过项目名称 获取APP应用的'bundleId'
    :param pro_name:
    :return:

    """
    if pro_name == "pro_demo_1":  # 应用宝
        app_package = "com.apple.Health"
    else:
        app_package = None
    return app_package


def config_ios_device_list():
    """
    配置 iOS 设备信息 列表
    [ { "device_name": "iPhone8(模拟器)", "wda_port": "8100", "wda_destination": "platform=iOS Simulator,name=iPhone 8" } } ,
      { "device_name": "iPhone11(模拟器)", "wda_port": "8200", "wda_destination": "platform=iOS Simulator,name=iPhone 11" } }, ]
      { "device_name": "iPhone7(真机)", "wda_port": "8200", "wda_destination": "id=3cbb25d055753f2305ec70ba6dede3dca5d500bb" } } ]

    【 备 注 】
    'wda_port'：WDA服务的启动端口（可以通过修改WebDriverAgent项目进行调整）
    'wda_destination'：WDA服务连接的iOS设备

    :return:
    """
    ios_device_info_list = []

    iphone8 = dict()
    iphone8["device_name"] = "iPhone8(模拟器)"
    iphone8["wda_port"] = "8100"
    iphone8["wda_destination"] = "platform=iOS Simulator,name=iPhone 8"
    ios_device_info_list.append(iphone8)

    iphone11 = dict()
    iphone11["device_name"] = "iPhone11(模拟器)"
    iphone11["wda_port"] = "8200"
    iphone11["wda_destination"] = "platform=iOS Simulator,name=iPhone 11"
    ios_device_info_list.append(iphone11)

    iphone7 = dict()
    iphone7["device_name"] = "iPhone7(真机)"
    iphone7["wda_port"] = "8100"
    iphone7["wda_destination"] = "id=3cbb25d055753f2305ec70ba6dede3dca5d500bb"
    ios_device_info_list.append(iphone7)

    return ios_device_info_list
