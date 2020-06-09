#!/bin/bash

# 设置变量
NPM_INSTALL_SOURCE="--save-dev --registry=https://registry.npm.taobao.org"

# 项目根目录下执行：创建package.json文件（若存在，先删除）
npm init

# 局部(项目下)安装 需要的工具包（ 项目根目录下生成 node_modules 目录）
npm install gulp@3.9.1 ${NPM_INSTALL_SOURCE}
npm install run-sequence@1.2.2 ${NPM_INSTALL_SOURCE}
npm install browser-sync@2.18.6 ${NPM_INSTALL_SOURCE}
npm install sleep@5.2.3 ${NPM_INSTALL_SOURCE}
npm install gulp-rev@7.1.2 ${NPM_INSTALL_SOURCE}
npm install gulp-clean@0.3.2 ${NPM_INSTALL_SOURCE}
npm install gulp-rev-collector@1.1.1 ${NPM_INSTALL_SOURCE}
npm install gulp-html-replace@1.6.2 ${NPM_INSTALL_SOURCE}
