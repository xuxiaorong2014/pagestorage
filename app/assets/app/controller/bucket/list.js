define(['text!app/views/bucket/list.html', 'template'], function (tpl, template) {
    var controller = function () {
        $.ajax({
            url: '/api/buckets',
            type: 'get',
            dataType: 'json',
            success: function (res) {
                admin.loadView(template.render(tpl,res));
            }
        });
        $('#container').off('click');
 
 
        $('#container').on('click', '.btn-danger', function () {
            var row = $(this).parent();
            var id = row.data('id');
            layer.confirm('真的删除?', function (index) {
                $.ajax({
                    url: '/api/buckets/' + id,
                    type: 'delete',
                    success: function () {
                        row.remove();
                        layer.msg('已删除!', { icon: 1, time: 1000 });
                        layer.close(index);
                    }
                });
            });
        });
    };
    controller.onRouteChange = function () {
        $('#container').off('click');
    };
    return controller;
});


 