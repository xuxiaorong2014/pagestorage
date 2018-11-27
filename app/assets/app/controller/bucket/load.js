define([], function () {
    var controller = function (controller,action,id) {
        if (id) {
            $.ajax({
                url: '/api/buckets/' + id,
                type: 'get',
                datatype: 'json',
                success: function (res) {
                    localStorage.setItem('config', JSON.stringify(res));
                    admin.BucketName=res.id;
                    $('#website').html(res.sitename);
                    $('#website').prop('href', res.url);
                    admin.loadView('<div style="padding:100px 10px 10px 100px">正在加载数据........</div>',true);
                    location.hash = '/article/list';
                }
            });
        }
    };
    return controller;
});