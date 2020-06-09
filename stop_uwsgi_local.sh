#!/bin/bash

# 判断是否存在 uwsgi 进程，若存在则杀死进程
# 【 实 现 逻 辑 】
# 1.查询uwsgi进程并打印入临时文件中
# 2.判断该文件是否为空，若不为空则执行杀死进程命令
# 3.'-s' 表示文件存在且不为空

ps aux | grep uwsgi | grep -v 'grep' | awk '{print $2}' > tmp_uwsgi_pid.txt

if [[ -s tmp_uwsgi_pid.txt ]]; then
   echo " Find uUWSGI pid, Try to kill them !"
   cat tmp_uwsgi_pid.txt | xargs kill -9
fi