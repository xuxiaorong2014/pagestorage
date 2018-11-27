define(['director', 'template'], function (Router, template) {
    var currentController = null;
    //用于把字符串转化为一个函数，而这个也是路由的处理核心
    var routeHandler = function () {
        return function () {
            var params = arguments;
            var url = 'app/controller/';
            if (params[0]) {
                url = url + params[0];
            }
            if (params[1]) {
                url = url +'/'+ params[1] ;
            }
            var id = '';
            if (params[2]) {
                id = params[2];
            }
            require([url], function (controller) {
                if (currentController && currentController !== controller) {
                    currentController.onRouteChange && currentController.onRouteChange();
                }
                currentController = controller;
                controller.apply(null, params);
            });
        }
    };
    //路由信息表
    var routes = {
        '/?([^\/]*)/?([^\/]*)/?([^\/]*)': routeHandler()
    };
    var options = {
        notfound: function () {
            $('#container').html('404页面不存在');
        } 
    };
    return Router(routes).configure(options);
});