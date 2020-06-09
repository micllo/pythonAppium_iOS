# -*- coding:utf-8 -*-
#  URL: http://tungwaiyip.info/software/HTMLTestRunner.html

__author__ = "Wai Yip Tung,  Findyou"
__version__ = "0.8.2.2"

# TODO: color stderr
# TODO: simplify javascript using ,ore than 1 class in the class attribute?

import datetime
import io
import unittest
from xml.sax import saxutils
import sys
from Env import env_config as cfg
import requests


class OutputRedirector(object):
    """ Wrapper to redirect stdout or stderr """
    def __init__(self, fp):
        self.fp = fp

    def write(self, s):
        self.fp.write(s)

    def writelines(self, lines):
        self.fp.writelines(lines)

    def flush(self):
        self.fp.flush()


"""
  【 问 题 】
   由于这两个是公用的变量，所有当多线程执行用例的时候可能会出现不同用例交叉使用，导致相互影响
"""
stdout_redirector = OutputRedirector(sys.stdout)
stderr_redirector = OutputRedirector(sys.stderr)

# ----------------------------------------------------------------------
# Template


class Template_mixin(object):
    """
    Define a HTML template for report customerization and generation.
    Overall structure of an HTML report
    HTML
    +------------------------+
    |<html>                  |
    |  <head>                |
    |                        |
    |   STYLESHEET           |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |  </head>               |
    |                        |
    |  <body>                |
    |                        |
    |   HEADING              |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |   REPORT               |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |   ENDING               |
    |   +----------------+   |
    |   |                |   |
    |   +----------------+   |
    |                        |
    |  </body>               |
    |</html>                 |
    +------------------------+
    """

    STATUS = {0: '通过', 1: '失败', 2: '错误'}

    DEFAULT_TITLE = '单元测试报告'
    DEFAULT_DESCRIPTION = ''
    DEFAULT_TESTER = '最棒QA'

    # ------------------------------------------------------------------------
    # HTML Template

    HTML_TMPL = r"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>%(title)s</title>
    <meta charset="utf-8" />
    <meta name="generator" content="%(generator)s"/>
    <meta http-equiv="Content-Type" content="text/html; charset=UTF-8"/>
    <link href="http://libs.baidu.com/bootstrap/3.0.3/css/bootstrap.min.css" rel="stylesheet">
    <script src="http://libs.baidu.com/jquery/2.0.0/jquery.min.js"></script>
    <script src="http://libs.baidu.com/bootstrap/3.0.3/js/bootstrap.min.js"></script>
    %(stylesheet)s
</head>
<body >
<script language="javascript" type="text/javascript">
output_list = Array();
/* 标签筛选功能
0:Summary -> all hiddenRow
1:Failed  -> pt hiddenRow, et hiddenRow, ft none
2:Error   -> pt hiddenRow, ft hiddenRow, et none
3:Pass    -> ft hiddenRow, et hiddenRow, pt none
4:All     -> all none
------------------------
ft -> 0 hiddenRow, 1 none, 2 hiddenRow, 3 hiddenRow, 4 none
et -> 0 hiddenRow, 1 hiddenRow, 2 none, 3 hiddenRow, 4 none
pt -> 0 hiddenRow, 1 hiddenRow, 2 hiddenRow, 3 none, 4 none
*/
function showCase(level) {
    trs = document.getElementsByTagName("tr");
    for (var i = 0; i < trs.length; i++) {
        tr = trs[i];
        id = tr.id;
        if (id.substr(0,2) == 'ft') {
            if (level == 0 || level == 2 || level == 3 ) {
                tr.className = 'hiddenRow';
            }
            else {
                tr.className = '';
            }
        }
        if (id.substr(0,2) == 'et') {
            if (level == 0 || level == 1 || level == 3 ) {
                tr.className = 'hiddenRow';
            }
            else {
                tr.className = '';
            }
        }
        if (id.substr(0,2) == 'pt') {
            if (level < 3) {
                tr.className = 'hiddenRow';
            }
            else {
                tr.className = '';
            }
        }
    }
    //加入[详细]切换文字变化
    detail_class=document.getElementsByClassName('detail');
	//console.log(detail_class.length)
	if (level == 3) {
		for (var i = 0; i < detail_class.length; i++){
			detail_class[i].innerHTML="收起"
		}
	}
	else{
        for (var i = 0; i < detail_class.length; i++){
			detail_class[i].innerHTML="详细"
		}
	}
}
function showClassDetail(cid, count) {
    var id_list = Array(count);
    var toHide = 1;  // 标记：是整体显示0，还是整体隐藏1
    // 获取'测试类行'下的所有'测试方法行'的'id'列表
    for (var i = 0; i < count; i++) {
        tid0 = 't' + cid.substr(1) + '_' + (i+1);
        tid = 'f' + tid0;
        tr = document.getElementById(tid);
        if (!tr) {
            tid = 'e' + tid0;
            tr = document.getElementById(tid);
            if(!tr){
                tid = 'p' + tid0;
                tr = document.getElementById(tid);
            }
        }
        id_list[i] = tid;
        // 只要有一个是被隐藏的，那就标记为整体显示
        if (tr.className) {
            toHide = 0;
        }
    }
    // 循环展示效果（整体显示 or 整体隐藏）
    for (var i = 0; i < count; i++) {
        tid = id_list[i];
        //修改点击无法收起的BUG，加入【详细】切换文字变化 --Findyou
        if (toHide) {
            document.getElementById(tid).className = 'hiddenRow';
            document.getElementById(cid).innerText = "详细"
        }
        else {
            document.getElementById(tid).className = '';
            document.getElementById(cid).innerText = "收起"
        }
    }
}
function html_escape(s) {
    s = s.replace(/&/g,'&amp;');
    s = s.replace(/</g,'&lt;');
    s = s.replace(/>/g,'&gt;');
    return s;
}
</script>
%(heading)s
%(report)s
%(ending)s
%(script_request)s
</body>
</html>
"""
    # variables: (title, generator, stylesheet, heading, report, ending, script_request)

    # ------------------------------------------------------------------------
    # Stylesheet
    #
    # alternatively use a <link> for external style sheet, e.g.
    #   <link rel="stylesheet" href="$url" type="text/css">

    STYLESHEET_TMPL = """
<style type="text/css" media="screen">
body        { font-family: Microsoft YaHei,Tahoma,arial,helvetica,sans-serif;padding: 20px; font-size: 100%;}
table       { font-size: 100%; }
/* -- heading ---------------------------------------------------------------------- */
.heading {
    margin-top: 0ex;
    margin-bottom: 1ex;
    font-size: 150%;
    font-weight: bold;
}
.heading .description {
    margin-top: 2ex;
    margin-bottom: 2ex;
    font-size: 150%;
}
/* -- report ------------------------------------------------------------------------ */
#total_row  { font-weight: bold; }
.passCase   { color: #5cb85c; }
.failCase   { color: #d9534f; font-weight: bold; }
.errorCase  { color: #f0ad4e; font-weight: bold; }
.hiddenRow  { display: none; }
.testcase   { margin-left: 2em;  font-size: 13px;}
</style>
"""

    # ------------------------------------------------------------------------
    # Heading
    #

    HEADING_TMPL = """<div class='heading'>
<h1 style="font-family: Microsoft YaHei">%(title)s</h1>
%(parameters)s
<p class='description'>%(description)s</p>
</div>
"""  # variables: (title, parameters, description)

    HEADING_ATTRIBUTE_TMPL = """<p class='attribute'><strong>%(name)s : </strong> %(value)s</p>
"""  # variables: (name, value)

    # ------------------------------------------------------------------------
    # Report
    #
    # variables: (test_list, count, Pass, fail, error ,passrate)
    REPORT_TMPL = """
<p id='show_detail_line'>
<a class="btn btn-primary" href='javascript:showCase(0)'>概要{ %(passrate)s }</a>
<a class="btn btn-danger" href='javascript:showCase(1)'>失败{ %(fail)s }</a>
<a class="btn btn-warning" href='javascript:showCase(2)'>错误{ %(error)s }</a>
<a class="btn btn-success" href='javascript:showCase(3)'>通过{ %(Pass)s }</a>
<a class="btn btn-info" href='javascript:showCase(4)'>所有{ %(count)s }</a>
</p>
<table id='result_table' class="table table-condensed table-bordered table-hover">
<colgroup>
<col align='left' />
<col align='right' />
<col align='right' />
<col align='right' />
<col align='right' />
<col align='right' />
</colgroup>
<tr id='header_row' class="text-center success" style="font-weight: bold;font-size: 15px;">
    <td>用例集/测试用例</td>
    <td>总计</td>
    <td>通过</td>
    <td>失败</td>
    <td>错误</td>
    <td>详细</td>
</tr>
%(test_list)s
<tr id='total_row' class="text-center active">
    <td>总计</td>
    <td>%(count)s</td>
    <td>%(Pass)s</td>
    <td>%(fail)s</td>
    <td>%(error)s</td>
    <td>通过率：%(passrate)s</td>
</tr>
</table>
"""

    # variables: (style, desc, count, Pass, fail, error, cid)
    REPORT_CLASS_TMPL = r"""
<tr class='%(style)s warning'>
    <td style="font-weight: bold;font-size: 13px;">%(desc)s</td>
    <td class="text-center">%(count)s</td>
    <td class="text-center">%(Pass)s</td>
    <td class="text-center">%(fail)s</td>
    <td class="text-center">%(error)s</td>
    <td class="text-center"><a href="javascript:showClassDetail('%(cid)s',%(count)s)" class="detail" id='%(cid)s'>详细</a></td>
</tr>
"""

    # '失败'或'错误'的样式 (tid, Class, style, desc, status, script, btn_color, screen_shot_btn_tmpl, show_img_div_tmpl)
    REPORT_TEST_FOR_EF_TMPL = r"""
<tr id='%(tid)s' class='%(Class)s'>
    <td class='%(style)s'><div class='testcase'>%(desc)s</div></td>
    <td colspan='5' align='center'>
    
    <!-- 默认收起错误信息 --> 
    <!-- <button id='btn_%(tid)s' type="button"  class="btn btn-%(btn_color)s btn-xs collapsed" data-toggle="collapse" data-target='#div_%(tid)s'>%(status)s</button>
    <div id='div_%(tid)s' class="collapse">  -->
    
    <!-- 默认展开错误信息  -->
    <button id='btn_%(tid)s' type="button"  class="btn btn-%(btn_color)s btn-xs" data-toggle="collapse" data-target='#div_%(tid)s'>%(status)s</button>
    %(screen_shot_btn_tmpl)s
    <div id='div_%(tid)s' class="collapse in"><pre>%(script)s</pre></div>
    %(show_img_div_tmpl)s
    </td>
</tr>
"""

    # '通过'的样式 (tid, Class, style, desc, status, screen_shot_btn_tmpl, show_img_div_tmpl)
    REPORT_TEST_FOR_PASS_TMPL = r"""
<tr id='%(tid)s' class='%(Class)s'>
    <td class='%(style)s'><div class='testcase'>%(desc)s</div></td>
    <td colspan='5' align='center'>
    <span class="label label-success success">%(status)s</span>
    %(screen_shot_btn_tmpl)s
    
    %(show_img_div_tmpl)s
    
    </td>
</tr>
"""

    # '无图'span 样式
    SCREENSHOT_SPAN_TMPL = r"""<span class="label label-info" style="float:right">无图</span>"""

    # '截图'btn 样式 (tid)
    SCREENSHOT_BTN_TMPL = r"""<button id='btn_%(tid)s_screenshot' type="button" class="btn btn-primary btn-xs" 
    data-toggle="collapse" data-target='#div_%(tid)s_screenshot' style="float:right">截图</button>"""

    # 展示'图片'的div ( tid、get_screenshot_tmpl_list )
    SHOW_SCREENSHOT_DIV_TMPL = r"""<div id='div_%(tid)s_screenshot' class="collapse">
    %(get_screenshot_tmpl_list)s
    </div>
    """

    # 获取'图片' ( screen_shot_id、width、height )
    # 另一种方式：src='data:image/png;base64,%(img_base64)s'
    GET_SCREENSHOT_TMPL = r"""
    <div>
    <br><HR align=center width=300color=#987cb9 SIZE=1><br>
    <img id='img_%(screen_shot_id)s' style='width:%(width)spx; height:%(height)spx' alt="'%(screen_shot_id)s'图片未显示">
    </div>
    """

    # variables: (id, output)
    REPORT_TEST_OUTPUT_TMPL = r"""%(id)s: %(output)s"""

    # ------------------------------------------------------------------------
    # ENDING
    #
    # 增加返回顶部按钮
    ENDING_TMPL = """<div id='ending'>&nbsp;</div>
    <div style=" position:fixed;right:50px; bottom:30px; width:20px; height:20px;cursor:pointer">
    <a href="#"><span class="glyphicon glyphicon-eject" style = "font-size:30px;" aria-hidden="true">
    </span></a></div>
    """

    # 循环发送请求 获取图片base64码的脚本模板 ( api_url_base, img_id_list_str )
    # 获取后将base64码注入'img'标签的'src'属性中
    REQUEST_IMG_SCRIPT_TMPL = """
    <script language="javascript" type="text/javascript">
        $(document).ready(function () {
            var api_url_base = "%(api_url_base)s";
            var img_id_list_str = "%(img_id_list_str)s";
            var img_id_list = img_id_list_str.split(".");
            console.log(img_id_list);
            console.log(typeof(img_id_list));
            <!-- 遍历 图片id列表 -->
            $.each(img_id_list, function(index, img_id){
                $.ajax({
                    type: "Get",
                    url: api_url_base + img_id,
                    dataType: "json",
                    async: true,
                    success: function (response) {
                        console.log("'http'请求成功 ！！！");
                        console.log(response)
                        var file_id = response.data.file_id;
                        var img_base64 = response.data.img_base64;
                        $('#img_' + file_id).attr({"src": "data:image/png;base64," + img_base64});
                    },
                    error: function () {
                        console.log("'http'请求失败.....");
                    }
                });
                
            });
            
        });
    </script>
    """

# -------------------- The end of the Template class -------------------


TestResult = unittest.TestResult


class _TestResult(TestResult):
    # note: _TestResult is a pure representation of results.
    # It lacks the output and reporting ability compares to unittest._TextTestResult.

    def __init__(self, verbosity=1):
        TestResult.__init__(self)
        self.stdout0 = None
        self.stderr0 = None
        self.success_count = 0
        self.failure_count = 0
        self.error_count = 0
        self.verbosity = verbosity

        # result is a list of result in 4 tuple
        # (
        #   result code (0: success; 1: fail; 2: error),
        #   TestCase object,
        #   Test output (byte string),
        #   stack trace,
        # )
        self.result = []
        # 增加一个测试通过率
        self.passrate=float(0)

    def startTest(self, test):
        TestResult.startTest(self, test)
        # just one buffer for both stdout and stderr

        # 创建'字符串缓冲对象'
        self.outputBuffer = io.StringIO()
        """【 问题 】当多线程执行用例的时候可能会出现不同用例的'self.outputBuffer'属性交叉使用了'stdout_redirector'公用变量"""
        stdout_redirector.fp = self.outputBuffer
        stderr_redirector.fp = self.outputBuffer
        self.stdout0 = sys.stdout
        self.stderr0 = sys.stderr
        """
         【 将'标准输出'指向了'字符串缓冲对象' 】
          作用：
             将'print、sys.stdout.write、sys.stderr.write'等输出内容保存入该对象中，
             等'标准输出'还原后，再执行上述输出操作，即可将之前缓存的内容全部输出
          问题：
             由于sys.stdout是公用的方法，所有当多线程执行用例的时候可能会出现不同用例交叉使用，导致相互影响
        """
        sys.stdout = stdout_redirector
        sys.stderr = stderr_redirector

    def complete_output(self):
        """
        作用：
        1.将 stdout、stderr 都指向控制台输出
           sys.stdout = self.stdout0（sys.stdout）
           sys.stderr = self.stderr0（sys.stderr）
        2.返回'字符串缓冲对象的值'
            self.outputBuffer.getvalue()
          空的，因为没有内容
            self.outputBuffer = io.StringIO()

        Disconnect output redirection and return buffer.
        Safe to call multiple times.
        """
        if self.stdout0:
            sys.stdout = self.stdout0
            sys.stderr = self.stderr0
            self.stdout0 = None
            self.stderr0 = None
        return self.outputBuffer.getvalue()

    def stopTest(self, test):
        # Usually one of addSuccess, addError or addFailure would have been called.
        # But there are some path in unittest that would bypass this.
        # We must disconnect stdout in stopTest(), which is guaranteed to be called.
        self.complete_output()

    # 在'unittest模块的case.py文件'中的'run'方法中被用到
    def addSuccess(self, test):
        self.success_count += 1
        TestResult.addSuccess(self, test)
        output = self.complete_output()
        self.result.append((0, test, output, ''))
        if self.verbosity > 1:
            sys.stderr.write('ok ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('.')

    def addError(self, test, err):
        self.error_count += 1
        TestResult.addError(self, test, err)
        _, _exc_str = self.errors[-1]
        output = self.complete_output()
        self.result.append((2, test, output, _exc_str))
        if self.verbosity > 1:
            sys.stderr.write('E  ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('E')

    def addFailure(self, test, err):
        self.failure_count += 1
        TestResult.addFailure(self, test, err)
        _, _exc_str = self.failures[-1]
        output = self.complete_output()
        self.result.append((1, test, output, _exc_str))
        if self.verbosity > 1:
            sys.stderr.write('F  ')
            sys.stderr.write(str(test))
            sys.stderr.write('\n')
        else:
            sys.stderr.write('F')


class HTMLTestRunner(Template_mixin):
    """
    """
    def __init__(self, stream=sys.stdout, verbosity=1,title=None,description=None,tester=None):
        self.stream = stream
        self.verbosity = verbosity
        if title is None:
            self.title = self.DEFAULT_TITLE
        else:
            self.title = title
        if description is None:
            self.description = self.DEFAULT_DESCRIPTION
        else:
            self.description = description
        if tester is None:
            self.tester = self.DEFAULT_TESTER
        else:
            self.tester = tester

        self.startTime = datetime.datetime.now()
        self.img_id_list = []

    def run(self, suite):
        """ Run the given test case or test suite. """
        result = _TestResult(self.verbosity)  # 初始化'测试结果'变量
        suite(result)  # 执行测试并记录测试结果
        self.stopTime = datetime.datetime.now()
        self.generateReport(suite, result)  # 通过测试结果生成测试报告
        print('\nTime Elapsed: %s' % (self.stopTime-self.startTime), file=sys.stderr)
        return result

    """
    【 将'result_list'测试结果列表中，按照'测试类'进行归类 】
    举例：若有两种测试类<class 'test_case.train_test.TrainTest'>、<class 'test_case.demo_test.DemoTest'>
    结果：[ (测试类1, [ (测试用例1结果), (测试用例2结果) ] ), ( 测试类2, [ (测试用例1结果) ] ) ]
    [(<class 'test_case.train_test.TrainTest'>, [(1,<test_case.train_test.TrainTest testMethod=test_01>,'','失败信息'),
                                                 (2,<test_case.train_test.TrainTest testMethod=test_02>,'','错误信息')]),
     (<class 'test_case.demo_test.DemoTest'>, [(0,<test_case.demo_test.DemoTest testMethod=test_demo_01>,'','成功无')])
    ]
    """
    def sortResult(self, result_list):
        # unittest does not seems to run in any particular order.
        # Here at least we want to group them together by class.
        rmap = {}     # 存放'测试类'对应的'结果信息' < 字典 >
        classes = []  # 存放'测试类' < 列表 >
        for n, t, o, e in result_list:
            cls = t.__class__
            if cls not in rmap:
                rmap[cls] = []
                classes.append(cls)
            rmap[cls].append((n,t,o,e))
        r = [(cls, rmap[cls]) for cls in classes]
        return r

    # 替换测试结果status为通过率
    def getReportAttributes(self, result):
        """
        Return report attributes as a list of (name, value).
        Override this to add custom attributes.
        """
        startTime = str(self.startTime)[:19]
        duration = str(self.stopTime - self.startTime)[:7]
        status = []
        status.append('共 %s' % (result.success_count + result.failure_count + result.error_count))
        if result.success_count: status.append('通过 %s' % result.success_count)
        if result.failure_count: status.append('失败 %s' % result.failure_count)
        if result.error_count:   status.append('错误 %s' % result.error_count)
        if status:
            status = '，'.join(status)
            self.passrate = str("%.2f%%" % (float(result.success_count) / float(result.success_count + result.failure_count + result.error_count) * 100))
        else:
            status = 'none'
        return [
            ('测试人员', self.tester),
            ('开始时间', startTime),
            ('合计耗时', duration),
            ('测试结果', status + "，通过率= "+self.passrate),
        ]

    def generateReport(self, suite, result):
        screen_shot_id_dict = suite.screen_shot_id_dict  # 获取截图ID字典
        ios_device_info_dict = suite.ios_device_info_dict  # 获取使用iOS设备信息：name、width、height
        report_attrs = self.getReportAttributes(result)
        generator = 'HTMLTestRunner %s' % __version__
        stylesheet = self._generate_stylesheet()
        heading = self._generate_heading(report_attrs)
        report = self._generate_report(result, screen_shot_id_dict, ios_device_info_dict)
        ending = self._generate_ending()
        script_request = self._script_request()
        output = self.HTML_TMPL % dict(
            title=saxutils.escape(self.title),  # 将内容转义后替换入HTML（举例："<"/">"/"&" 对应"&lt;"/"&gt;"/"&amp;"）
            generator=generator,
            stylesheet=stylesheet,
            heading=heading,
            report=report,
            ending=ending,
            script_request=script_request
        )
        self.stream.write(output.encode('utf8'))

    def _generate_stylesheet(self):
        return self.STYLESHEET_TMPL

    # 增加Tester显示 -Findyou
    def _generate_heading(self, report_attrs):
        a_lines = []
        for name, value in report_attrs:
            line = self.HEADING_ATTRIBUTE_TMPL % dict(
                    name=saxutils.escape(name),
                    value=saxutils.escape(value),
                )
            a_lines.append(line)
        heading = self.HEADING_TMPL % dict(
            title=saxutils.escape(self.title),
            parameters=''.join(a_lines),
            description=saxutils.escape(self.description),
            tester=saxutils.escape(self.tester),
        )
        return heading

    # 生成报告
    def _generate_report(self, result, screen_shot_id_dict, ios_device_info_dict):
        """
        :param result:
        :param screen_shot_id_dict: 截图ID字典 -> { "测试类名.测试方法名":['aaa', 'bbb'], "测试类名.测试方法名":['ccc'] }
        :param ios_device_info_dict: 使用的iOS设备信息：name、width、height
            ->  { "测试类名.测试方法名": {"device_name": "iPhone8(模拟器)", "device_width": "414", "device_height": "896"},
                  "测试类名.测试方法名": {"device_name": "iPhone7(真机)", "device_width": "540", "device_height": "960"} }
        :return:
        【 显 示 截 图 的 逻 辑 】
         1.根据'测试类名'取出该类下的所有'测试方法'对应的'截图ID列表'的字典 -> { "测试方法名":['aaa', 'bbb'], "测试方法名":['ccc'] }
         2.在有截图的'测试方法'下创建<img id='img_图片id'>的标签
         3.获取所有截图id的列表 self.img_id_list = ['aaa', 'bbb', 'ccc']
         4.在页面中嵌入<script>脚本循环调用接口获取图片的base64码，并赋值给对应的<img>标签的'src'属性中
            eg：src='data:image/png;base64,%(img_base64)s'
        """
        rows = []
        sortedResult = self.sortResult(result.result)
        for cid, (cls, cls_results) in enumerate(sortedResult):  # 遍历'测试类'
            # subtotal for a class
            np = nf = ne = 0
            for n, t, o, e in cls_results:
                if n == 0: np += 1
                elif n == 1: nf += 1
                else: ne += 1

            # format class description
            if cls.__module__ == "__main__":
                name = cls.__name__
            else:
                name_long = "%s.%s" % (cls.__module__, cls.__name__)
                name_long_list = name_long.split(".")
                name = name_long_list[1] + "." + name_long_list[4]
            doc = cls.__doc__ and cls.__doc__.split("\n")[0] or ""

            # 获取测试用例类的__doc__备注信息（目的：注明该测试类的作用）
            desc = doc and '%s: %s' % (name, doc) or name

            # 添加'测试用例类'模板样式
            row = self.REPORT_CLASS_TMPL % dict(
                style=ne > 0 and 'errorClass' or nf > 0 and 'failClass' or 'passClass',
                desc=desc,
                count=np+nf+ne,
                Pass=np,
                fail=nf,
                error=ne,
                cid='c%s' % (cid+1),
            )
            rows.append(row)

            # 根据'测试类名'取出该类下的所有'测试方法'对应的'截图ID列表'的字典 -> { "测试方法名":['aaa', 'bbb'], "测试方法名":['ccc'] }
            screen_shot_id_dict_with_test_method = {}
            for key, value in screen_shot_id_dict.items():
                if key.split(".")[0] == cls.__name__:
                    screen_shot_id_dict_with_test_method[key.split(".")[1]] = value

            # 根据'测试类名'取出该类下的所有'测试方法'对应的'使用的iOS设备名称'的字典
            ios_device_info_dict_with_test_method = {}
            for key, value in ios_device_info_dict.items():
                if key.split(".")[0] == cls.__name__:
                    ios_device_info_dict_with_test_method[key.split(".")[1]] = value

            # 为每个'测试用例类'循环添加'测试用例执行结果'模板样式 保存在'rows'列表中
            for tid, (n, t, o, e) in enumerate(cls_results):
                self._generate_report_test(rows, cid, tid, n, t, o, e, screen_shot_id_dict_with_test_method, ios_device_info_dict_with_test_method)

        report = self.REPORT_TMPL % dict(
            test_list=''.join(rows),
            count=str(result.success_count+result.failure_count+result.error_count),
            Pass=str(result.success_count),
            fail=str(result.failure_count),
            error=str(result.error_count),
            passrate=self.passrate,
        )
        return report

    def _generate_report_test(self, rows, cid, tid, n, t, o, e, screen_shot_id_dict_with_test_method, ios_device_info_dict_with_test_method):
        """
        :param rows:
        :param cid:
        :param tid:
        :param n: 0->通过，1->失败，2->错误
        :param t: 测试实例对象
        :param o: 测试过程中输出的内容（一般都是空的）
        :param e: 错误信息、失败的信息
        :param screen_shot_id_dict_with_test_method: { "测试方法名":['aaa', 'bbb'], "测试方法名":['ccc'] }
        :param ios_device_info_dict_with_test_method:
                ->  { "测试方法名": {"device_name": "iPhone8(模拟器)", "device_width": "414", "device_height": "896"},
                      "测试方法名": {"device_name": "iPhone7(真机)", "device_width": "540", "device_height": "960"} }
        :return:
        """
        # 'pt1_1', 'et1_1', 'ft1_1', 支持Bootstrap折叠展开特效
        tid = (n == 0 and "p" or (n == 1 and "f" or "e")) + 't%s_%s' % (cid+1, tid+1)

        # t.id() 是unittest.TestCase中的实例方法，返回自定义测试类中的测试方法的全路径
        # t.id() -> test_case.train_test.TrainTest.test_01
        # name -> test_01
        name = t.id().split('.')[-1]

        # 获取该'测试方法'的'截图ID列表'
        screen_shot_list = screen_shot_id_dict_with_test_method[name]

        # 获取该'测试方法'的'使用的iOS设备名称'
        device_info = ios_device_info_dict_with_test_method[name]
        device_name = device_info.get("device_name")
        device_width = device_info.get("device_width")
        device_height = device_info.get("device_height")

        # 获取'截图按钮'样式
        if screen_shot_list:
            screen_shot_btn_tmpl = self.SCREENSHOT_BTN_TMPL % dict(tid=tid)
        else:
            screen_shot_btn_tmpl = self.SCREENSHOT_SPAN_TMPL

        # 获取'展示图片'的样式
        show_img_div_tmpl = ""
        if screen_shot_list:
            get_screenshot_tmpl_list = ""
            for i, screen_shot_id in enumerate(screen_shot_list):
                self.img_id_list.append(screen_shot_id)  # 将截图id添加到总列表中
                get_screenshot_tmpl_list += self.GET_SCREENSHOT_TMPL % dict(screen_shot_id=screen_shot_id, width=device_width, height=device_height)
            show_img_div_tmpl = self.SHOW_SCREENSHOT_DIV_TMPL % dict(tid=tid, get_screenshot_tmpl_list=get_screenshot_tmpl_list)

        # 获取测试方法中的 __doc__, 并加上（使用的iOS设备名称）
        doc = t.shortDescription() or ""
        desc = doc and ('%s: %s' % (name, doc)) or name
        desc = desc + " [" + device_name + "]"

        # 若n==0表示通过，则使用'通过'的样式，否则使用'失败'或'错误'的样式
        tmpl = n == 0 and self.REPORT_TEST_FOR_PASS_TMPL or self.REPORT_TEST_FOR_EF_TMPL

        # utf-8 支持中文 - Findyou
        # o and e should be byte string because they are collected from stdout and stderr?
        if isinstance(o, str):
            # TODO: some problem with 'string_escape': it escape \n and mess up formating
            # uo = unicode(o.encode('string_escape'))
            # uo = o.decode('latin-1')
            uo = o
        else:
            uo = o
        if isinstance(e, str):
            # TODO: some problem with 'string_escape': it escape \n and mess up formating
            # ue = unicode(e.encode('string_escape'))
            # ue = e.decode('latin-1')
            ue = e
        else:
            ue = e

        # 测试用例需要显示的相关错误信息
        # ft1_2: Traceback (most recent call last): ...... AssertionError: '1' not found in '2'
        script = self.REPORT_TEST_OUTPUT_TMPL % dict(
            id=tid,
            # output=saxutils.escape(uo+ue),
            # 忽略'o'中的内容：由于多线程执行用例的原因，使用了某些公用的变量，可能会导致数据的交叉影响
            output=saxutils.escape(ue),
        )

        row = tmpl % dict(
            tid=tid,
            Class=(n == 0 and 'hiddenRow' or 'none'),
            style=(n == 2 and 'errorCase' or (n == 1 and 'failCase' or 'passCase')),
            desc=desc,
            script=script,
            btn_color=(n == 2 and 'warning' or (n == 1 and 'danger' or 'success')),
            status=self.STATUS[n],
            screen_shot_btn_tmpl=screen_shot_btn_tmpl,
            show_img_div_tmpl=show_img_div_tmpl
        )
        rows.append(row)

    def _generate_ending(self):
        return self.ENDING_TMPL

    def _script_request(self):
        script_request_tmpl = ""
        if self.img_id_list:
            api_url_base = "http://" + cfg.API_ADDR + "/iOS/get_img/"
            img_id_list_str = ".".join(self.img_id_list)
            script_request_tmpl = self.REQUEST_IMG_SCRIPT_TMPL % dict(api_url_base=api_url_base,
                                                                      img_id_list_str=img_id_list_str)
        return script_request_tmpl


if __name__ == "__main__":
    api_url = "http://" + cfg.API_ADDR + "/iOS/get_img/" + "5e609cdacd380a0cef68056f"
    res_dict = requests.get(api_url).json()
    img_base64 = res_dict.get("result").get("img_base64")
    print(img_base64[2:-1])

