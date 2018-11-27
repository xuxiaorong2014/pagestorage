define(['text!app/views/article/edit.html', 'template', 'tinymce/tinymce.min'], function (tpl, template) {
    var panel = '<div class="panel panel-default"><div class="panel-heading"><h2>标题</h2></div><div class="panel-body"><p>内容</p></div></div>';
 
    var h = document.documentElement.clientHeight; //获取当前窗口可视操作区域高度
    var tinymce_config = {
        selector: '#content',
        height: (h - 284),
        menubar: false,
        language: 'zh_CN',
        plugins: 'advlist autolink lists link image charmap preview anchor textcolor visualblocks code media table contextmenu paste',
        toolbar: 'insert | undo redo | bold italic removeformat | bullist numlist | uploadimage addbox | code',
        content_css: ['/assets/bootstrap/css/bootstrap.min.css'],
        setup: function (editor) {
            editor.addButton('uploadimage', {
                tooltip: '上传图片',
                icon: 'image',
                onclick: function () {
                    $('#upfile').click();
                }
            });
            editor.addButton('addbox', {
                tooltip: '添加段落框',
                icon: 'template',
                onclick: function () {
                    var tmp = editor.getContent();
                    editor.setContent(tmp + panel);
                }
            });
        }
    };
    
    var loadpost = function (id, o) {
        
        if (id) {
            $.ajax({
                url: '/api/posts/' + id,
                type: 'get',
                headers: {'BucketName': admin.BucketName},
                success: function (res) {
                    admin.loadView(template.render(tpl, { Model: res, Options: o }), true);
                    tinymce.remove('#content');
                    tinymce.init(tinymce_config);
                }
            });
        }
        else {
            admin.loadView(template.render(tpl, { Model: { Content: panel,Catalog:'/' }, Options: o }),true);
            tinymce.remove('#content');
            tinymce.init(tinymce_config);
        }
    };
    var dialog = ['<div style="padding:10px" id="dialog">',
                '<div class="form-group">',
                '<input class="form-control" type="text" name="key" placeholder="请输入字段名" value="{{key}}">',
                '</div>',
                '<div class="form-group">',
                '<textarea name="value" class="form-control">{{value}}</textarea>',
                '</div>',
                '</div>'
    ].join('');

    var controller = function (name, action, id) {
        //加载模板列表
        $.ajax({
            url: '/api/templates',
            type: 'get',
            headers: {'BucketName': admin.BucketName},
            success: function (res) {
                var result = [];
                $.each(res, function (i, f) {
                    if ((f.indexOf('/') < 0) && f.endWith('.html')) {
                        result.push(f);
                    }
                });
                //加载视图
                loadpost(id,result);
            }
        });
        $('#container').off('click');
        $('#container').on('click', '#addmeta', function () {
            layer.open({
                type: 1,
                title: '添加字段',
                area: ['400px', 'auto'],
                content: template.render(dialog, { key:'',value:'' }),
                btn: ['确定', '取消'],
                yes: function (index) {
                    var idx = $('#metas').find('input').length / 2;
                    var input_key = $('#dialog input[name="key"]').val();
                    var input_value = $('#dialog textarea[name="value"]').val();
                    var metas = ' <span data-idx="' + idx + '" class="label label-info">' + input_key + ' <span>&times;</span></span> ';
                    var meta_key = $('<input type="hidden" name="Metas[' + idx + '].key" />')
                    var meta_value = $('<input type="hidden" name="Metas[' + idx + '].value" />')
                    meta_key.val(input_key);
                    meta_value.val(input_value);
                    $('#metas').append(metas);
                    $('#metas').append(meta_key);
                    $('#metas').append(meta_value);
                    layer.close(index);
                }
            })
        });
        $('#container').on('click', '#metas>.label', function () {
            var idx = $(this).data('idx');
            var input_key = $('input[name="Metas[' + idx + '].key"').val();
            var input_value = $('input[name="Metas[' + idx + '].value"').val();
            layer.open({
                type: 1,
                title: '编辑字段',
                area: ['400px', 'auto'],
                content: template.render(dialog, { key: input_key, value: input_value }),
                btn: ['确定', '取消'],
                yes: function (index) {
                    var dlg_key = $('#dialog input[name="key"]').val();
                    var dlg_value = $('#dialog textarea[name="value"]').val();
                    $('input[name="Metas[' + idx + '].key"').val(dlg_key);
                    $('input[name="Metas[' + idx + '].value"').val(dlg_value);
                    $('#metas span[data-idx="' + idx + '"]').html(dlg_key + ' <span>&times;</span>');
                    layer.close(index);
                }
            });
        });
        $('#container').on('click', '#metas>.label>span', function () {
            var meta = $(this).parent();
            var idx = meta.data('idx');
            meta.remove();
            $('input[name="Metas[' + idx + '].key"').remove();
            $('input[name="Metas[' + idx + '].value"').remove();
            //遍历更改索引属性
            $('#metas>.label').each(function (index, label) {
                var data_idx = $(label).data('idx');
                $(label).data({idx:index});
                $('input[name="Metas[' + data_idx + '].key"').prop('name', 'Metas[' + index + '].key');
                $('input[name="Metas[' + data_idx + '].value"').prop('name', 'Metas[' + index + '].value');
            });
            return false;
        });
        $('#container').off('change').on('change', '#upfile', function () {
            var yymm = new Date().Format('yyMM');
            var fileObjs = document.getElementById("upfile").files; // js 获取文件对象
            fileObj = fileObjs[0];
            if (typeof (fileObj) == "undefined" || fileObj.size <= 0) {
                alert("请选择图片");
                return;
            }
            var formFile = new FormData();
            formFile.append("file", fileObj); //加入文件对象
            $.ajax({
                url: '/api/objects?prefix=attachments/' + yymm + '/',
                data: formFile,
                type: "post",
                dataType: "json",
                cache: false,//上传文件无需缓存
                processData: false,//用于对data参数进行序列化处理 这里必须false
                contentType: false, //必须
                headers: {'BucketName': admin.BucketName},
                success: function (result) {
                    var cfg = JSON.parse(localStorage.getItem('config'));
                    tinymce.execCommand('mceInsertContent', '#content', '<img class="img-responsive center-block" src="' + cfg.url + result[0] + '" />');
                },
            })
        });
        $('#container').off('submit').on('submit', '.form-post', function () {
            var action,method, me = $(this);
            var id = $('input[name="Id"]').val();
            if (id) {
                method = 'put';
                action = '/api/posts/' + id;
            }
            else {
                method = 'post';
                action = '/api/posts';
            }
            var data = me.serialize();
            var loading = layer.msg('正在提交数据...', { icon: 16, shade: 0.05, time: 40000 });
            $.ajax({
                url: action,
                type: method,
                data: data,
                headers: {'BucketName': admin.BucketName},
                success: function (res) {
                    if (!id) {
                        id = res.Id;
                    }
                    $.ajax({
                        url: '/api/publish/' + id,
                        type: 'post',
                        headers: {'BucketName': admin.BucketName},
                        success: function (res) {
                            layer.msg('保存成功', { icon: 1, time: 1000 });
                            location.hash = '/article/list';
                        }
                    });
                }
            });
            return false;
        });

        controller.onRouteChange = function () {
            $('#container').off('click');   //解除所有click事件监听
            $('#container').off('change');
            $('#container').off('submit');
        };
    };
    return controller;
});