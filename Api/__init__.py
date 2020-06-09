# -*- coding: utf-8 -*-
from flask import Flask
from Config.scheduler_job import Config
from flask_apscheduler import APScheduler
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR
from Env import env_config as cfg

flask_app = Flask(__name__, static_folder=cfg.GULP_STATIC_PATH, template_folder=cfg.GULP_TEMPLATE_PATH)


# flask 添加 定时任务配置
flask_app.config.from_object(Config())

# 初始化定时任务
scheduler = APScheduler()
scheduler.init_app(flask_app)

# 为定时任务添加监听器
scheduler.add_listener(Config.my_listener, EVENT_JOB_EXECUTED | EVENT_JOB_ERROR)

# 启动定时任务
scheduler.start()

