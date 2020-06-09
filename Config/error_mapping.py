# -*- coding: utf-8 -*-
"""
错误码的映射表
"""
# 200
SYNC_SUCCESS = u'同步成功'
STOP_SUCCESS = u'停止成功'
CASE_RUNING = u"测试用例执行中"
REQUEST_SUCCESS = u"请求成功"
INSERT_SUCCESS = u"插入数据成功"
UPDATE_SUCCESS = u"更新成功"

# 500
iOS_DEVICES_NOT_CONNECT = u"没有已连接的iOS设备"
NO_SUCH_FILE = u"该文件不存在"
NO_SUCH_PRO = u"该项目不存在"
INTERNAL_SERVER_ERROR = u"内部错误:服务器正在维护中"
REQUEST_FAILED = u"内部错误:请求失败"
SEARCH_FAILED = u"查询数据失败"
STATUS_FAILED = u"查询状态失败"
CALCULATE_FAILED = u"计算数据失败"

# 400
BASIC_INFO_MISSING = u"缺少基本信息或者不存在"
REQUEST_ARGS_WRONG = u"请求参数有误"
REQUEST_VERANDA_WRONG = u"该甬道不存在"
UPDATE_WRONG = u"更新参数有误"
SIN_ID_WRONG = u"没有该id数据"
CT_WRONG = u"没有该ct数据"
PENDING_WRONG = u"任务还在计算中"
VERSION_WRONG = u"版本错误"

# 504
MONGO_CONNECT_FAIL = u"mongo数据库连接失败"
REQUEST_TIMEOUT = u"请求数据超时"
CONNECT_DB_TIMEOUT = u"链接数据库超时"

# 204
NO_ONLINE_CASE = u'没有上线的用例'
EXIST_RUNNING_CASE = u'存在运行中的用例'
PRO_NOT_EXIST = u"项目不存在"
PARAMS_NOT_NONE = u"参数不能为空"
BROWSER_NAME_ERROR = u"浏览器名错误"
THREAD_NUM_ERROR = u"线程数量必须控制在1~5之间"
NO_SUCH_USER = u"没有该用户数据"

# 404
PATH_ERROR = u"路径错误"


def get_error_code(code_msg):
    """
    错误码对照表: 参照http响应码写法
    :param code_msg: 错误信息
    :return: 错误码
    """

    resp_map = {
        # 200
        SYNC_SUCCESS: 31200,
        STOP_SUCCESS: 31200,
        CASE_RUNING: 31200,
        REQUEST_SUCCESS: 31200,
        UPDATE_SUCCESS: 31200,
        INSERT_SUCCESS: 31200,

        # 500
        iOS_DEVICES_NOT_CONNECT: 31500,
        NO_SUCH_FILE: 31500,
        NO_SUCH_PRO: 31500,
        INTERNAL_SERVER_ERROR: 31500,
        REQUEST_FAILED: 31500,
        SEARCH_FAILED: 31500,
        STATUS_FAILED: 31500,
        CALCULATE_FAILED: 31500,

        # 504
        MONGO_CONNECT_FAIL: 31504,
        REQUEST_TIMEOUT: 31504,
        CONNECT_DB_TIMEOUT: 31504,

        # 400
        BASIC_INFO_MISSING: 31400,
        REQUEST_ARGS_WRONG: 31400,
        REQUEST_VERANDA_WRONG: 31400,
        UPDATE_WRONG: 31400,
        SIN_ID_WRONG: 31400,
        PENDING_WRONG: 31400,
        VERSION_WRONG: 31400,

        # 204
        NO_ONLINE_CASE: 31200,
        EXIST_RUNNING_CASE: 31200,
        PRO_NOT_EXIST: 31204,
        PARAMS_NOT_NONE: 31204,
        BROWSER_NAME_ERROR: 31204,
        THREAD_NUM_ERROR: 31204,
        NO_SUCH_USER: 31204,

        # 404
        PATH_ERROR: 404,


    }

    return resp_map[code_msg]
