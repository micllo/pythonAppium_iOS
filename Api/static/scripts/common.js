/**
 *  请 求 接 口
 *  async: false 同步
 *  async: true  异步
 *  [ 备 注 ]
 *  1.调用该方法时，只能使用同步，因为'response_text'在异步时无法获取到内容
 *  2.调用后，可以通过返回值的属性，来判断是否请求成功
 *    判断方式一：
 *    response_info.constructor.toString().indexOf("Number") < 0
 *    （1）若匹配到'Number'（ 即返回的是 response_status ）, 表示：请求失败
 *    （2）若匹配不到'Number'（ 即返回的是 JSON.parse(response_text) ）, 表示：请求成功
 *    判断方式二：
 *    isNaN(response_info)
 *    判断是否是数字；不是返回true、是返回false
 */
function request_interface_url(url, method, data="", async=false) {
    var parameter_ajax = {
        url: url,
        type: method.toLowerCase(),
        async: async,
        dataType: "json"
    };
    if (method.toLowerCase() == "post" && data != ""){
        if(typeof data == "string"){
            parameter_ajax["data"] = data;
        }else {  // typeof data == dict()
            parameter_ajax["data"] = JSON.stringify(data);
            parameter_ajax["contentType"] = "application/json; charset=utf-8";
        }
    }
    var info_ajax = $.ajax(parameter_ajax);
    var response_text = info_ajax.responseText;
    return JSON.parse(response_text);
}

function request_interface_url_v2(url, method, data="", async=false) {
    var response_text = ""
    var parameter_ajax = {
        url: url,
        type: method.toLowerCase(),
        async: async,
        dataType: "json",
        success: function (response_info) {
            console.log("'http'请求成功.....")
            response_text = response_info
        },
        error: function () {
            console.log("'http'请求失败.....")
            response_text = "请求失败"
        }
    };
    if (method.toLowerCase() == "post" && data != ""){
        if(typeof data == "string"){
            parameter_ajax["data"] = data;
        }else {  // typeof data == dict()
            parameter_ajax["data"] = JSON.stringify(data);
            parameter_ajax["contentType"] = "application/json; charset=utf-8";
        }
    }
    var info_ajax = $.ajax(parameter_ajax);
    // var response_text = info_ajax.responseText;
    // var response_status = info_ajax.status;
    // var response_status_text = info_ajax.statusText;
    // // console.log(response_text)
    // // console.log(response_status)
    // // console.log(response_status_text)
    return response_text

}
