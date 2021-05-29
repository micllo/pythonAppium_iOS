# -*- coding: utf-8 -*-
from fabric.api import *
from Common.com_func import mkdir
from Env import env_config_docker as cfg
import time


# 设置变量
host = cfg.SERVER_IP
port = "1522"
user = "centos"
passwd = "centos"
pro_name = "pythonAppium_iOS"
pro_name_tar = pro_name + ".tar.gz"
tmp_path = "/Users/micllo/tmp/"
pro_tmp_path = tmp_path + pro_name
deploy_file = tmp_path + pro_name_tar
pro_path = "/Users/micllo/Documents/works/GitHub/" + pro_name
remote_tmp_path = "/opt/project/tmp/"


# 本地操作
def local_action():
    # 若临时目录不存在则创建
    mkdir(tmp_path)
    # 清空临时目录中的内容, 将项目代码拷贝入临时文件夹
    with lcd(tmp_path):
        local("rm -rf " + pro_name)
        local("rm -rf " + deploy_file)
        local("cp -r " + pro_path + " " + tmp_path)
    # 删除临时文件夹中不需要的文件目录
    with lcd(pro_tmp_path):
        local("rm -rf .DS_Store")
        local("rm -rf .git")
        local("rm -rf .gitignore")
        local("rm -rf .idea")
        local("rm -rf Logs")
        local("rm -rf Reports")
        local("rm -rf Screenshots")
        local("rm -rf vassals_local")
        local("rm -rf venv")
        local("rm -rf gulpfile.js")
        local("rm -rf gulpfile_install.sh")
        local("rm -rf package.json")
        local("rm -rf package-lock.json")
        local("rm -rf node_modules")
        local("rm -rf nohup.out")
        local("rm -rf tmp_uwsgi_pid.txt")
        local("rm -rf venv_install.sh")
        local("rm -rf requirements.txt")
        local("rm -rf requirements_init.txt")
        local("ls")
    # 归档压缩 临时文件夹中的项目（ 可以不进入目录，直接执行 ）
    with lcd(tmp_path):
        local("tar -czvf " + pro_name_tar + " " + pro_name)
    # 将部署文件上传服务器
    with settings(host_string="%s@%s:%s" % (user, host, port), password=passwd):
        put(remote_path=remote_tmp_path, local_path=deploy_file)


# 服务器端操作
def server_action():
    with settings(host_string="%s@%s:%s" % (user, host, port), password=passwd):
        # 停止'nginx、uwsgi、mongo'服务
        run("sh /home/centos/stop_nginx.sh", warn_only=True)  # 忽略失败的命令,继续执行
        run("sh /home/centos/stop_uwsgi.sh", warn_only=True)
        # run("pgrep mongod | sudo xargs kill -9", warn_only=True)
        run("pwd")
        # 解压'部署文件'
        run("tar -xzvf " + remote_tmp_path + pro_name_tar + " -C " + remote_tmp_path, warn_only=True)
        # 替换'项目'和'uwsgi.ini'配置文件
        with cd(remote_tmp_path):
            run("rm -rf /opt/project/" + pro_name, warn_only=True)
            run("cp -r " + pro_name + " /opt/project/", warn_only=True)
            run("rm -r /etc/uwsgi/vassals/*.ini", warn_only=True)
            run("cp -r /opt/project/" + pro_name + "/vassals/*.ini /etc/uwsgi/vassals/", warn_only=True)
        # 替换Env环境配置文件
        with cd("/opt/project/" + pro_name + "/Env"):
            run("rm -r env_config.py && mv env_config_docker.py env_config.py", warn_only=True)

        # 启动'mongo、nginx、uwsgi'服务
        # run("sudo mongod -f /tools/mongodb/bin/mongodb.conf", warn_only=False)  # 不忽略失败的命令，不能继续执行
        run("sh /home/centos/start_nginx.sh", warn_only=False)
        run("sh /home/centos/start_uwsgi.sh", warn_only=False, pty=False)  # 参数pty：解决'fabric'执行'nohub'的问题

        # 清空临时文件夹
        with cd(remote_tmp_path):
            run("rm -rf " + pro_name, warn_only=True)
            run("rm -rf " + pro_name + ".tar.gz", warn_only=True)



if __name__ == "__main__":
    local_action()
    server_action()

