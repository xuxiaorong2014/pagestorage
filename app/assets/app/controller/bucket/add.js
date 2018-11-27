define(['template' ], function (template) {
    var controller = function (controller,action,id) {
        require(['text!app/views/bucket/edit_' + id + '.html'], function (tpl) {
            admin.loadView(template.render(tpl));
        });
        $('#container').off('submit').on('submit', '.form-ajax', function () {      
            var bucket = $('input[name="[4].value"]').val();
            var BucketName = bucket;
            if($('input[name="[1].value"]').val()=='cos'){
                BucketName = bucket + '-' + $('input[name="[5].value"]').val();
            }
            $('input[name="[0].value"]').val(BucketName);
            var data = $(this).serializeArray();
            var index =layer.load();
            $.ajax({
                url: '/api/buckets',
                type: 'post',
                data:data,
                success: function (res) {
                    layer.close(index);
                    layer.confirm('网站添加成功，需要上传示例数据吗？', {
                        btn: ['是的', '不用'] //按钮
                    }, function () {
                        layer.load();
                        $.ajax({
                            url: '/api/buckets/' + BucketName,
                            type: 'post',
                            success: function () {
                                location.hash = '/bucket/list';
                            }
                        })
                    }, function () {
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