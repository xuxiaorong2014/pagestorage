define(['text!app/views/templates/edit.html',
    'text!app/left.html',
    'template',
    'ace/ace',
    'ace/ext/language_tools'],
    function (tpl,left, template,ace) {
        var editor;
        var controller = function (name, action, id) {
            if (id) {
                id = decodeURIComponent(id);
                $.ajax({
                    url: '/api/objects?key=' + encodeURIComponent('/theme/' + id),
                    type: 'get',
                    dataType: 'html',
                    headers: {'BucketName': admin.BucketName},
                    success: function (res) {
                        admin.loadView(template.render(tpl, { key: id, name: id, content: res }), true);
                        editor = ace.edit('content');
                        ace.require('ace/ext/language_tools');
                        editor.getSession().setMode('ace/mode/' + id.substring(id.lastIndexOf('.')+1));
                        var h = document.documentElement.clientHeight; //获取当前窗口可视操作区域高度
                        $('.ace_editor').css('height',(h-160)+'px')
                         
                    }
                });
            }
            else {
                admin.loadView(template.render(tpl), true);
                editor = ace.edit('content');
                var h = document.documentElement.clientHeight; //获取当前窗口可视操作区域高度
                $('.ace_editor').css('height',(h-160)+'px')
            }

        $('#container').off('click');
         
 
         
        $(document).off('submit', '.form-template').on('submit', '.form-template', function () {
            var key = $('input[name="key"]').val();
            var name = $('input[name="name"]').val();
            var loading = 0;
            $.ajax({
                url: '/api/templates?name=' + encodeURIComponent(name),
                type: 'put',
                data: { '': editor.getValue()},
                beforeSend: function (xhr) {
                    loading = layer.msg('正在提交数据...', { icon: 16, shade: 0.05, time: 40000 });
                },
                complete: function () {
                    layer.close(loading);
                },
                headers: {'BucketName': admin.BucketName},
                success: function (res) {
                    layer.msg('提交成功', { icon: 1 });
                    if (key != name) {
                        if (key == '') {
                            $('input[name="key"]').val(name);
                        }
                        else {
                            $.ajax({
                                url: '/api/templates?name=' + encodeURIComponent(key),
                                type: 'delete',
                                headers: {'BucketName': admin.BucketName},
                                success: function () {
                                    loadlist();
                                }
                            });
                        }
                    }
                }
            });
            return false;
        });
    };
    controller.onRouteChange = function () {
        $('#container').off('click');
        $(document).off('submit');
    };
    return controller;
});