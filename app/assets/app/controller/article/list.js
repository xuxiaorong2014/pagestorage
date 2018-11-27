define(['text!app/views/article/list.html', 'template'], function (tpl, template) {

    var controller = function () {
        var cfg = JSON.parse(localStorage.getItem('config'));
        var websiteurl = cfg.url.endWith('/')?cfg.url.substring(0,cfg.url.length-1) :cfg.url;
        var loadposts = function () {
            $.ajax({
                url: '/api/posts',
                type: 'get',
                datetype: 'json',
                headers: {'BucketName': admin.BucketName},
                success: function (res) {
                    admin.loadView( template.render(tpl, {url: websiteurl, posts:res}),true);
                }
            });
        }();
        $('#container').off('click').on('click', '#grid button', function () {
            var action = $(this).data('action');
            var row = $(this).parent().parent();
             
            var id = row.data('id');
            if (action == 'publish') {
                row.find('button[data-action="publish"]').replaceWith('<span class="loading"><img width="16" src="assets/layer/theme/default/loading-1.gif" /></span>');
                $.ajax({
                    url: '/api/publish/' + id,
                    type: 'post',
                    headers: {'BucketName': admin.BucketName},
                    success: function (res) {
                        row.find('.loading').addClass('label label-success').html('已发布');
                    }
                });
            }
            else if (action == 'del') {
                layer.confirm('真的删除?', function (index) {
                    $.ajax({
                        url: '/api/posts/' + id,
                        type: 'delete',
                        headers: {'BucketName': admin.BucketName},
                        success: function () {
                            row.remove();
                            layer.msg('已删除!', { icon: 1, time: 1000 });
                            layer.close(index);
                        }
                    });
                });
            }
        });
		controller.onRouteChange = function () {
		    $('#container').off('click');   //解除所有click事件监听
        };
    };

	
    return controller;
});