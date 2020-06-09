# -*- coding:utf-8 -*-
import logging,time
from Env import env_config as cfg


class FrameLog(object):
    """
     日志级别： debug < info < warning < error < critical
    """
    def __init__(self, logger=None):

        # 创建一个logger <记录器> 、 <记录器>指定日志级别（决定消息是否要传递给<处理器>）
        self.logger = logging.getLogger(logger)
        self.logger.setLevel(logging.DEBUG)

        # 每个实例对象都要先清空 handlers ，否则会出现重复的日志
        # self.logger.handlers.clear()

        # 判断是否已经添加过 handlers，否则会出现重复的日志记录
        if not self.logger.handlers:
            # 指定日志 存放路径 和 名称
            # self.log_path = project_path() + "Logs/"
            self.log_time = time.strftime("%Y_%m_%d_")
            self.log_name = cfg.LOGS_DIR + self.log_time + 'log.log'
            # print("日志路径：" + self.log_name)

            # 【 创建 handler <处理器>, 写入日志文件 <fh>、终端输出 <ch> 】
            # 1.创建日志句柄：指定日志文件 ( mode：'a'追加、'w'覆盖写入 )
            fh = logging.FileHandler(self.log_name, mode='a', encoding="utf-8")
            # ch = logging.StreamHandler()

            # 2.<处理器>句柄指定日级别（决定消息是否要发送至文件和终端）
            fh.setLevel(logging.INFO)
            # ch.setLevel(logging.INFO)

            # 3.设置<处理器>句柄的显示格式
            fm = logging.Formatter("[%(asctime)s] %(filename)s -> %(funcName)s line:%(lineno)d [%(levelname)s]  %(message)s")
            fh.setFormatter(fm)
            # ch.setFormatter(fm)

            # 4.将<处理器>句柄添加入日志对象
            self.logger.addHandler(fh)
            # self.logger.addHandler(ch)

            # 6.关闭<处理器>句柄
            fh.close()
            # ch.close()

    def log(self):
        return self.logger


if __name__ == '__main__':
    fl = FrameLog()
    log = fl.log()
    log.critical("严重")
    log.error("Error")
    log.warning("Warning")
    log.info("Info")
    log.debug("Debug")


