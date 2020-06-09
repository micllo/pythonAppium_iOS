#!/bin/bash

# 设置变量
PIP_INSTALL_SOURCE="-i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com"

# 创建 虚拟环境目录 ( which python3 )
virtualenv -p /usr/local/bin/python3 venv

# 进入 虚拟环境
source venv/bin/activate

# 安装python项目依赖
pip3 install -r requirements_init.txt ${PIP_INSTALL_SOURCE}

# 退出 虚拟环境
deactivate


# 导出
# pip3 freeze > requirements.txt


# pip3 install -v logzero==1.5.0 -i http://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com