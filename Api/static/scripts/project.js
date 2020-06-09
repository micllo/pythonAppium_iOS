/**
 * 修改案件状态（单个）
 */
function update_case_status(pro_name, test_method_name, nginx_api_proxy) {
    // 调用ajax请求(同步)
    var request_url = "/" + nginx_api_proxy + "/iOS/set_case_status/" + pro_name + "/" + test_method_name
    var response_info = request_interface_url_v2(url=request_url, method="GET", async=false);
    if(response_info != "请求失败"){
        if(response_info.data.new_case_status == true){
            $("#case_status_" + test_method_name).html("上 线");
            $("#case_status_" + test_method_name).removeClass().addClass("btn btn-success btn-sm");
            $("#case_status_" + test_method_name + "_tr").removeClass().addClass("passClass success");
        }else{
            $("#case_status_" + test_method_name).html("下 线");
            $("#case_status_" + test_method_name).removeClass().addClass("btn btn-danger btn-sm");
            $("#case_status_" + test_method_name + "_tr").removeClass().addClass("passClass danger");
        }
        setTimeout(function(){location.reload();}, 1000);
    }
}


/**
 * 修改案件状态（所有）
 */
function update_case_status_all(pro_name, case_status, nginx_api_proxy) {
    // 调用ajax请求(同步)
    var request_url = "/" + nginx_api_proxy + "/iOS/set_case_status_all/" + pro_name + "/" + case_status
    var response_info = request_interface_url_v2(url=request_url, method="GET", async=false);
    if(response_info != "请求失败"){
        $.each(response_info.data.test_method_name_list,function (i, test_method_name) {
            if(case_status == "true"){
                $("#case_status_" + test_method_name).html("上 线");
                $("#case_status_" + test_method_name).removeClass().addClass("btn btn-success btn-sm");
                $("#case_status_" + test_method_name + "_tr").removeClass().addClass("passClass success");
            }else{
                $("#case_status_" + test_method_name).html("下 线");
                $("#case_status_" + test_method_name).removeClass().addClass("btn btn-danger btn-sm");
                $("#case_status_" + test_method_name + "_tr").removeClass().addClass("passClass danger");
            }
        })
        setTimeout(function(){location.reload();}, 1000);
    }
}


/**
 * 同步用例列表
 */
function sync_case_list(pro_name, nginx_api_proxy) {
    swal({
        title: "确 定 要 同 步 用 例 吗 ?",
        text: "",
        type: "warning",
        showCancelButton: true,
        confirmButtonText: "确定",
        cancelButtonText: "取消"
    }).then(function(isConfirm){
        if (isConfirm) {
            // 调用ajax请求(同步)
            var request_url = "/" + nginx_api_proxy + "/iOS/sync_case_list/" + pro_name
            var response_info = request_interface_url_v2(url=request_url, method="GET", async=false);
            if(response_info == "请求失败"){
                swal({text: response_info, type: "error", confirmButtonText: "知道了"});
            }else{
               if(response_info.status == "success"){
                   swal({text: response_info.msg, type: "success", confirmButtonText: "知道了"});
                   setTimeout(function(){location.reload();}, 2000);
                }else{
                   swal({text: response_info.msg, type: "error", confirmButtonText: "知道了"});
                }
            }
        }
    }).catch((e) => {
        console.log(e)
        console.log("cancel");
    });
}


/**
 * 强行修改用例运行状态 -> 停止
 */
function stop_run_status(pro_name, nginx_api_proxy) {
    swal({
        title: "确 定 要 修 改 运 行 状 态 吗 ?",
        text: "",
        type: "warning",
        showCancelButton: true,
        confirmButtonText: "确定",
        cancelButtonText: "取消"
    }).then(function(isConfirm){
        if (isConfirm) {
            // 调用ajax请求(同步)
            var request_url = "/" + nginx_api_proxy + "/iOS/stop_run_status/" + pro_name
            var response_info = request_interface_url_v2(url=request_url, method="GET", async=false);
            if(response_info == "请求失败"){
                swal({text: response_info, type: "error", confirmButtonText: "知道了"});
            }else{
               if(response_info.status == "success"){
                   swal({text: response_info.msg, type: "success", confirmButtonText: "知道了"});
                   setTimeout(function(){location.reload();}, 2000);
                }else{
                   swal({text: response_info.msg, type: "error", confirmButtonText: "知道了"});
                }
            }
        }
    }).catch((e) => {
        console.log(e)
        console.log("cancel");
    });
}


/**
 *  批量执行
 */
function run_case(pro_name, nginx_api_proxy) {
    swal({
        title: "确 定 执 行 用 例 吗 ?",
        text: "",
        type: "warning",
        showCancelButton: true,
        confirmButtonText: "确定",
        cancelButtonText: "取消"
    }).then(function(isConfirm){
        if (isConfirm) {
            // 调用ajax请求(同步)
            var request_url = "/" + nginx_api_proxy + "/iOS/sync_run_case/" + pro_name
            var response_info = request_interface_url_v2(url=request_url, method="GET", async=false);
            if(response_info == "请求失败"){
                swal({text: response_info, type: "error", confirmButtonText: "知道了"});
            }else{
               if(response_info.msg == "测试用例执行中"){
                   // swal({text: response_info.msg, type: "success", confirmButtonText: "知道了"});
                   background_update_process(pro_name, nginx_api_proxy);
                }else{
                   swal({text: response_info.msg, type: "error", confirmButtonText: "知道了"});
                   $("#run_result").html(response_info.msg);
                   $("#run_result").removeClass().addClass("label label-warning");
                   if(response_info.msg == "存在运行中的用例"){
                       setTimeout(function(){location.reload();}, 3000);
                   }
                }
            }
        }
    }).catch((e) => {
        console.log(e)
        console.log("cancel");
    });
}


/**
 *  后台轮询 并 更新进度条
 *  1.进度条清零
 *  2.禁灰 相关按钮(总上下线、同步用例、批量执行)
 *  3.禁灰 所有项目的 '上下线'按钮，更新在线用例的'开始时间、运行时间'
 *  4.定时器：每间隔1秒钟
 *  （1）更新 用例'运行状态、开始时间、运行时间'
 *  （2）更新 进度条记录
 *  （3）更新 进度条样式
 */
function background_update_process(pro_name, nginx_api_proxy) {
    // 更新 标题显示：上次 -> 当前
    $("#title_show").html("当&nbsp;&nbsp;&nbsp;前&nbsp;&nbsp;&nbsp;用&nbsp;&nbsp;&nbsp;例&nbsp;&nbsp;&nbsp;运&nbsp;&nbsp;&nbsp;行&nbsp;&nbsp;&nbsp;进&nbsp;&nbsp;&nbsp;度");
    // 进度条清零
    $("#progress_bar").css({"width": "0 %"});
    $("#progress_label").html("0 % -- 0 / 0");
    // 禁灰相关按钮(总上下线、同步用例、批量执行)
    $("#on_line_all").attr('disabled', 'true');
    $("#off_line_all").attr('disabled', 'true');
    $("#sync_case_list").attr('disabled', 'true');
    $("#run_case").attr('disabled', 'true');
    $("#run_result").html("测试运行中。。。");
    $("#run_result").attr('class', 'label label-warning');
    // 禁灰所有项目的 '上下线'按钮，更新在线用例的'开始时间、运行时间'
    var request_url = "/" + nginx_api_proxy + "/iOS/refresh_case_run_status/" + pro_name
    var response_info = request_interface_url_v2(url=request_url, method="GET", async=false);
    var case_run_status_list = response_info.data.case_run_status_list
    $.each(case_run_status_list,function (i, case_info) {
        $("#case_status_" + case_info.test_method_name).attr('disabled', 'true');
        $("#start_time_" + case_info.test_method_name).html("----");
        $("#run_time_" + case_info.test_method_name).html("----");
    })

    // 轮询修改进度信息
    var interval = setInterval(function () {  // 间隔指定的毫秒数不停地执行指定的代码，定时器
        // 更新 用例'运行状态、开始时间、运行时间'
        var request_url_1 = "/" + nginx_api_proxy + "/iOS/refresh_case_run_status/" + pro_name
        var response_info_1 = request_interface_url_v2(url=request_url_1, method="GET", async=false);
        var case_run_status_list = response_info_1.data.case_run_status_list
        $.each(case_run_status_list,function (i, case_info) {
            if(case_info.run_status == "pending") {
                $("#run_status_" + case_info.test_method_name).html("待运行");
                $("#run_status_" + case_info.test_method_name).attr('class', 'label label-warning warning');
            }else if(case_info.run_status == "running"){
                $("#run_status_" + case_info.test_method_name).html("运行中");
                $("#run_status_" + case_info.test_method_name).attr('class', 'label label-success success');
                $("#start_time_" + case_info.test_method_name).html(case_info.start_time);
            }else{
                $("#run_status_" + case_info.test_method_name).html("已停止");
                $("#run_status_" + case_info.test_method_name).attr('class', 'label label-danger danger');
                $("#start_time_" + case_info.test_method_name).html(case_info.start_time);
                $("#run_time_" + case_info.test_method_name).html(case_info.run_time);
            }
        })
        // 更新 进度条
        var request_url_2 = "/" + nginx_api_proxy + "/iOS/refresh_run_progress/" + pro_name
        var response_info_2 = request_interface_url_v2(url=request_url_2, method="GET", async=false);
        var progress_info = response_info_2.data.progress_info
        if (progress_info.percent < 100 ) {
            // 更新进度条记录
            $("#progress_bar").css({"width": progress_info.percent + "%"}); // 方式一：修改css样式（修改的是'style'属性中的内容）
            // $("#progress_bar").attr("style", "width:" + progress_info.percent + "%");  // 方式二：修改属性
            $("#progress_label").html(progress_info.percent + " % -- " + progress_info.done_num + " / " + progress_info.run_num);
            // 更新进度条样式
            $("#progress_bar_active").attr("class", "progress progress-striped active");
            if(progress_info.percent > 0 && progress_info.percent < 60 ){
                $("#progress_bar").attr("class", "progress-bar progress-bar-warning");
            }else{
                $("#progress_bar").attr("class", "progress-bar progress-bar-success");
            }
        } else {
            clearInterval(interval); // 用于停止 setInterval() 方法执行的函数代码
            location.reload();
        }
    }, 1000);
}




// // 将按钮禁灰不可点击
// $("#stop_run_status").attr('disabled', true);
//
// // 改变当前结果状态
// $("#stop_run_status_result").html(" 处 理 中 。。。");
// $("#stop_run_status_result").removeClass().addClass("label label-info");
//
// $("#stop_run_status_result").html(response_info.msg);
// $("#stop_run_status_result").removeClass().addClass("label label-success");
// $("#stop_run_status_result").removeClass().addClass("label label-warning");
// $("#stop_run_status_result").removeClass().addClass("label label-danger");
//
// // 将按钮还原可点击
// $("#stop_run_status").removeattr('disabled');
// $("#stop_run_status").attr('disabled', false);

// readonly
