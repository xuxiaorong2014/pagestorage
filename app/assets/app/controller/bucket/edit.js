define(['template' ], function (template) {
    var controller = function (controller,action,id) {
        $.ajax({
            url: '/api/buckets/' + id,
            type: 'get',
            datatype: 'json',
            success: function (res) {
                require(['text!app/views/bucket/edit_' + res.type + '.html'], function (tpl) {
                    admin.loadView(template.render(tpl, res));
                });
            }
        });
        $('#container').off('submit').on('submit', '.form-ajax', function () {
            var data = $(this).serializeArray();
            $.ajax({
                url: '/api/buckets/' + id,
                type: 'put',
                data:data,
                success: function (res) {
                    layer.msg('保存成功', { icon: 1, time: 2000 }, function () {
                        location.hash = '/bucket/list';
                    });
                }
            });
            return false;

        });
    };
    controller.onRouteChange = function () {
        $('#container').off('submit');
    };
    return controller;
});