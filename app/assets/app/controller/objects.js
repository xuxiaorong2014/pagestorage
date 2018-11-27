define(['text!app/views/objects/tpl.html', 'text!app/views/objects/dialog.html', 'template'], function (tpl, dialog, template) {
    //配置插件
    template.defaults.imports.Action = function (value) {
        if (value.endWith('.json') || value.endWith('.txt') || value.endWith('.css') || value.endWith('.html') || value.endWith('.htm')|| value.endWith('.js')) {
            return '<button data-action="edit" class="btn btn-primary btn-xs"><span class="glyphicon glyphicon-edit"></span></button> <button data-action="del" class="btn btn-danger btn-xs" ><span class="glyphicon glyphicon-trash"></span></button>';
        }
        else if (value.endWith('.jpg') || value.endWith('.gif') || value.endWith('.png') || value.endWith('.ico')) {
            return '<button data-action="preview"  class="btn btn-default btn-xs"><span class="glyphicon glyphicon-eye-open"></span></button> <button data-action="del"  class="btn btn-danger btn-xs" ><span class="glyphicon glyphicon-trash"></span></button>';
        }
        else {
            return '<button data-action="download"  class="btn btn-default btn-xs"><span class="glyphicon glyphicon-download-alt"></span></button> <button data-action="del"  class="btn btn-danger btn-xs" ><span class="glyphicon glyphicon-trash"></span></button>';
        }
    }

    //控制器
    var controller = function () {
        var cfg = JSON.parse(localStorage.getItem('config'));
        var data = { prefix: '', nav: [], folders: [], files: [] };
        //获取query参数
        data.prefix = admin.QueryString('path');
        if (data.prefix) {
            var p = data.prefix.split('/');
            var link = '';
            for (var i = 0; i < p.length; i++) {
                if (p[i] != '') {
                    link = link + p[i] + '/';
                    if (i == p.length - 2) {
                        link = '';
                    }
                    data.nav.push({ link: link, title: p[i] });
                }
            }
        }

        var loadlist = function () {
            data.folders = [];
            data.files = [];
            $.ajax({
                url: '/api/objects?delimiter=%2f&prefix=' + encodeURIComponent(data.prefix),
                type: 'get',
                headers: {'BucketName': admin.BucketName},
                success: function (res) {
                    if (res.CommonPrefixes) {
                        if (isNaN(res.CommonPrefixes.length)) {
                            data.folders.push({ Key: res.CommonPrefixes.Prefix });
                        }
                        else {
                            $.each(res.CommonPrefixes, function (i, row) {
                                data.folders.push({ Key: row.Prefix });
                            });
                        }
                    }
                    if (res.Contents) {
                        if (isNaN(res.Contents.length)) {
                            if (res.Contents.Key != data.prefix) {
                                data.files.push(res.Contents);
                            }
                        }
                        else {
                            $.each(res.Contents, function (i, row) {
                                if (row.Key != data.prefix) {
                                    data.files.push(row);
                                }
                            });
                        }
                    }
                    admin.loadView( template.render(tpl, data),true);
                }
            });
        };
        loadlist();
        $('#container').off('click');
        $('#container').on('click', '#add', function () {
            layer.open({
                type: 1,
                area: ['880px', 'auto'],
                title: '新建文件',
                content: template.render(dialog, { key: '', content: '' })
            });
        });
        $('#container').on('click', '#grid .tool button', function () {
            var action = $(this).data('action');
            var row = $(this).parent().parent().parent();
            var key = row.data('key');
            if (action == 'edit') {
                $.ajax({
                    url: '/api/objects?key=' + encodeURIComponent('/' + key),
                    type: 'get',
                    dataType: 'html',
                    headers: {'BucketName': admin.BucketName},
                    success: function (res) {
                        layer.open({
                            type: 1,
                            area: ['880px', 'auto'],
                            title: '编辑文件',
                            content: template.render(dialog, { key: key.substr(data.prefix.length).replace('/', ''), content: res })
                        });
                    }
                });
            }
            else if (action == 'preview') {
                layer.open({
                    type: 1,
                    title: false,
                    //closeBtn: 0,
                    //area: '516px',
                    skin: 'layui-layer-nobg', //没有背景色
                    shadeClose: true,
                    content: '<img style="max-width:600px" src="' + cfg.url + key + '" />'
                });
            }
            else if (action == 'download') {
                var endpoint = admin.endpoint();
                location.href = 'https://' + endpoint + '/' + key;
            }
            else if (action == 'del') {
                layer.confirm('真的删除?', function (index) {
                    $.ajax({
                        url: '/api/objects?key=' + encodeURIComponent(key),
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
            else if (action == 'deltree') {
                layer.confirm('真的删除?', function (index) {
                    $.ajax({
                        url: '/api/objects?key=' + encodeURIComponent(key),
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
        $('#container').on('click', '#FileUploadButton', function () {
            $('#FileUpload').click();
        });
        $('#container').off('change').on('change', '#FileUpload', function () {
            var fileObjs = document.getElementById("FileUpload").files; // js 获取文件对象
            fileObj = fileObjs[0];
            if (typeof (fileObj) == "undefined" || fileObj.size <= 0) {
                alert("请选择图片");
                return;
            }
            var formFile = new FormData();

            for (var i = 0; i < fileObjs.length; i++) {
                formFile.append("file", fileObjs[i]); //加入文件对象
            }
            $.ajax({
                url: '/api/objects?prefix=' + encodeURIComponent(data.prefix),
                data: formFile,
                type: "post",
                dataType: "json",
                cache: false,//上传文件无需缓存
                processData: false,//用于对data参数进行序列化处理 这里必须false
                contentType: false, //必须
                headers: {'BucketName': admin.BucketName},
                success: function (result) {
                    loadlist();
                    layer.alert("上传完成!");
                },
            })
        });
        $(document).off('submit').on('submit', '.form-object', function () {
            var me = $(this);
            var key = $('input[name="key"]').val();
            var oldkey = $('input[name="oldkey"]').val();
            var loading = 0;
            $.ajax({
                url: '/api/objects?key=' + encodeURIComponent(data.prefix + key),
                type: 'put',
                data: { '': $('#content').val() },
                beforeSend: function (xhr) {
                    loading = layer.msg('正在提交数据...', { icon: 16, shade: 0.05, time: 40000 });
                },
                complete: function () {
                    layer.close(loading);
                },
                headers: {'BucketName': admin.BucketName},
                success: function (res) {
                    layer.msg('提交成功', { icon: 1 });
                    if (key != oldkey) {
                        if (oldkey == '') {
                            loadlist();
                        }
                        else {
                            $.ajax({
                                url: '/api/objects?key=' + encodeURIComponent(data.prefix + oldkey),
                                type: 'delete',
                                headers: {'BucketName': admin.BucketName},
                                success: function () {
                                    loadlist();
                                }
                            });
                        }
                    }
                    layer.closeAll('page');
                }
            });
            return false;
        });
        controller.onRouteChange = function () {
            $('#container').off('click');
            $('#container').off('change');
            $(document).off('submit');
        };
    };
    return controller;
});