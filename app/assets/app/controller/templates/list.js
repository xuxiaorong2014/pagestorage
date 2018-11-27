define(['text!app/views/templates/list.html',
    'text!app/left.html',
    'template'],
    function (tpl,left, template) {
 
    var controller = function () {
        var loadlist = function () {
            $.ajax({
                url: '/api/templates',
                type: 'get',
                headers: {'BucketName': admin.BucketName},
                success: function (res) {
                    admin.loadView(template.render(tpl, res),true);
                }
            });
        };
        loadlist();
        $('#container').off('click');
        $('#container').on('click', '#grid .btn-danger', function () {
            var row = $(this).parent().parent();
            var name = row.data("name");
            layer.confirm('真的删除?', function (index) {
                $.ajax({
                    url: '/api/templates?name=' + encodeURIComponent(name),
                    type: 'delete',
                    headers: {'BucketName': admin.BucketName},
                    success: function () {
                        row.remove();
                        layer.msg('已删除!', { icon: 1, time: 1000 });
                        layer.close(index);
                    }
                });
            });
        });
        $('#container').on('click', '#download', function () {
            layer.load();
            $.ajax({
                url: '/api/objects?prefix=theme%2F&delimiter=',
                type: 'get',
                headers: {'BucketName': admin.BucketName},
                success: function (res) {
                    var dataSet = [];
                    if (res.Contents) {
                        if (isNaN(res.Contents.length)) {
                            dataSet.push(res.Contents);
                        }
                        else {
                            $.each(res.Contents, function (i, row) {
                                dataSet.push(row);
                            });
                        }
                    }
                    layer.closeAll('loading');
                    layer.open({
                        type: 1,
                        shadeClose: true, 
                        content: '<div id="msg-result" style="padding:10px"> </div>'
                    });
                    $.each(dataSet, function (i, row) {
                        $.ajax({
                            url: '/api/templates/download?name=' + encodeURIComponent(row.Key),
                            type: 'get',
                            headers: {'BucketName': admin.BucketName},
                            success: function () {
                                $('#msg-result').append(row.Key + ' 下载成功<br/>')
                            },
                            error:function(){
                                $('#msg-result').append(row.Key + ' 下载失败<br/>')
                            }
                        });
                    });
                }
            });
        });
        $('#container').on('click', '#upload', function () {
            layer.load();
            $.ajax({
                url: '/api/templates',
                type: 'post',
                headers: {'BucketName': admin.BucketName},
                success: function (res) {
                    layer.alert('上传成功');
                },
                error: function () {
                    layer.alert('上传出错');
                },
                complete: function () {
                    layer.closeAll('loading');
                }
            });
        });
         
    };
    controller.onRouteChange = function () {
        $('#container').off('click');
    };
    return controller;
});