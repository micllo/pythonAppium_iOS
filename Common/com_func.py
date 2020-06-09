# -*- coding:utf-8 -*-
import os, configparser
from Tools.log import FrameLog
import inspect
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import traceback
from Env import env_config as cfg
from Config import global_var as gv
import requests
import json


log = FrameLog().log()

NULL_LIST = [" ", "", None, "nan", "NaN", "None", "null", []]


def is_null(tgt):
    """
    查看输入的是不是null
    :param tgt: 输入的string或者unicode
    :return: boolean
    """
    if tgt not in NULL_LIST:
        isnull_res = False
    else:
        isnull_res = True

    return isnull_res


# 获取项目路径
def project_path():
    return os.path.split(os.path.realpath(__file__))[0].split('C')[0]


# 获取当前的'类名/方法名/'(提供截屏路径使用)
def get_current_function_name(class_instance):
    return class_instance.__class__.__name__ + "/" + inspect.stack()[1][3] + "/"


# 获取'config.ini'文件中的（ 获取 [test_url] 下的 baidu_rul 的值
def get_config_ini(key, value):
    config = configparser.ConfigParser()
    config.read(project_path() + "Config/test_url.ini")
    return config.get(key, value)


# 递归创建目录
def mkdir(path):
    path = path.strip()  # 去除首位空格
    path = path.rstrip("//")  # 去除尾部 / 符号
    is_exists = os.path.exists(path)  # 判断路径是否存在(True存在，False不存在)
    # 判断结果
    if not is_exists:
        os.makedirs(path)
        log.info(path + ' 目录创建成功')
        return True
    else:
        log.info(path + ' 目录已存在')
        return False


def send_mail(subject, content, to_list, attach_file=None):
    """
    [ 发送邮件 ]
    :param subject: 邮件主题
    :param content: 邮件内容
    :param to_list: 邮件发送者列表
    :param attach_file: 附件
    :return:
    """
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = cfg.ERROR_MAIL_ACCOUNT
    msg['To'] = ";".join(to_list)
    msg.attach(MIMEText(content, _subtype='plain', _charset='utf-8'))
    if not is_null(attach_file):
        attach = MIMEText(open(attach_file, 'rb').read(), 'base64', 'utf-8')
        # 指定当前文件格式类型
        attach['Content-type'] = 'application/octet-stream'
        # 配置附件显示的文件名称,当点击下载附件时，默认使用的保存文件的名称
        attach['Content-Disposition'] = "attachment;filename=" + attach_file.split("/")[-1]
        # 把附件添加到msg中
        msg.attach(attach)
    try:
        server = smtplib.SMTP()
        server.connect(host=cfg.ERROR_MAIL_HOST, port=25)
        server.login(cfg.ERROR_MAIL_ACCOUNT, cfg.ERROR_MAIL_PASSWD)
        server.sendmail(cfg.ERROR_MAIL_ACCOUNT, to_list, msg.as_string())
        server.close()
        log.info("邮件发送成功！")
    except Exception as e:
        print(str(e))
        print(traceback.format_exc())
        log.error("邮件发送失败！")


def send_DD(dd_group_id, title, text, at_phones, is_at_all=False):
    """
    发 送 钉 钉
    :param dd_group_id: 发送的钉钉消息群
    :param title: 消息title
    :param text:  消息内容
    :param at_phones: 需要@的手机号
    :param is_at_all: 是否@所有人
    :return:
      备注：若要@某个人，则需要在'text'中@其手机号
           at_text -> \n\n@138xxxxxx @139xxxxxx
      注意：
         钉钉机器人设置了关键字过滤
         title 或 text 中必须包含 "监控" 两字
    """
    at_all = "true"
    at_mobiles = []
    at_text = ""
    if not is_at_all:
        at_all = "false"
        at_mobiles = at_phones.split(",")
        at_text += "\n\n"
        at_mobile_text = ""
        for mobile in at_mobiles:
            at_mobile_text += "@" + mobile + " "
        at_text += at_mobile_text
    data = {"msgtype": "markdown"}
    data["markdown"] = {"title": "[iOS监控] " + title, "text": text + at_text}
    data["at"] = {"atMobiles": at_mobiles, "isAtAll": at_all}
    dd_url = gv.DD_BASE_URL + dd_group_id
    log.info(data)
    headers = {'Content-Type': 'application/json'}
    try:
        requests.post(url=dd_url, data=json.dumps(data), headers=headers)
        log.info("钉钉发送成功")
    except Exception as e:
        log.error("钉钉发送失败")
        log.error(e)


# # 多线程重载 run 方法
# class MyThread(threading.Thread):
#
#     def __init__(self, func, driver, test_class_list):
#         super(MyThread, self).__init__()
#         # threading.Thread.__init__(self)
#         self.func = func
#         self.driver = driver
#         self.test_class_list = test_class_list
#
#     def run(self):
#         print("Starting " + self.name)
#         print("Exiting " + self.name)
#         self.func(self.driver, self.test_class_list)


if __name__ == "__main__":
    pass
    # attach_file = cfg.REPORTS_DIR + "report.html"
    # send_mail(subject="测试发送", content="测试内容。。。。", to_list=cfg.MAIL_LIST, attach_file=attach_file)

    # print("项目路径：" + project_path())
    # print("被测系统URL：" + get_config_ini("test_url", "ctrip_url"))
    # print()
    # print(os.path.split(os.path.realpath(__file__)))
    # print(os.path.split(os.path.realpath(__file__))[0])
    # print(os.path.split(os.path.realpath(__file__))[0].split('C'))
    # print(os.path.split(os.path.realpath(__file__))[0].split('C')[0])


