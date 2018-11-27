String.prototype.startWith = function (str) {
    var reg = new RegExp("^" + str);
    return reg.test(this);
}
String.prototype.endWith = function (str) {
    var reg = new RegExp(str + "$");
    return reg.test(this);
}
Date.prototype.Format = function (fmt) {
    var o = {
        "M+": this.getMonth() + 1,
        "d+": this.getDate(),
        "h+": this.getHours(),
        "m+": this.getMinutes(),
        "s+": this.getSeconds(),
        "q+": Math.floor((this.getMonth() + 3) / 3),
        "S": this.getMilliseconds()
    };
    if (/(y+)/.test(fmt)) fmt = fmt.replace(RegExp.$1, (this.getFullYear() + "").substr(4 - RegExp.$1.length));
    for (var k in o)
        if (new RegExp("(" + k + ")").test(fmt)) fmt = fmt.replace(RegExp.$1, (RegExp.$1.length == 1) ? (o[k]) : (("00" + o[k]).substr(("" + o[k]).length)));
    return fmt;
}

var admin = {
	BucketName : '',
    templates:[],
    QueryString: function (name) {
        if (window.location.hash.indexOf('?') > 0) {
            var reg = new RegExp('(^|&)' + name + '=([^&]*)(&|$)', 'i');  //i 表示区分大小写
            r = window.location.hash.split('?')[1].match(reg);
            if (r != null) {
                return unescape(r[2]);
            }
        }
        return '';
    } 
};

(function (win) {
	require.config({
		baseUrl: 'assets',
		paths: {
			director: 'js/director.min',
			jquery:'js/jquery-1.10.2.min',
			template: 'js/template-web',
			text: 'js/text.min',
			bootstrap:'bootstrap/js/bootstrap.min',
			layer: 'layer/layer',
			ace: 'ace'
		},
		shim:{
		    jquery:{exports:'$'},
		    director: {exports: 'Router'},
		    bootstrap:{deps:['jquery']},
		    layer: { deps: ['jquery'], exports: 'layer' }
		}
	});
	require(['jquery', 'app/router', 'layer', 'template', 'text!app/left.html', 'bootstrap'], function ($, router, layer, template,tpl) {
		layer.config({
		　　path: 'assets/layer/'      //layer.js所在的目录，可以是绝对目录，也可以是相对目录
		});


		
		$.ajaxSetup({
		    cache: false,
		    error: function (xhr, status, info) {
		        if (xhr.responseText) {
		            layer.alert(xhr.responseText, { title: '错误', icon: 2 ,area:['700px','500px']});
		        }
		        else if (info) {
		            layer.alert(info, { title: '错误', icon: 2,area:'800px' });
		        }
		        else {
		            layer.alert('连接错误', { title: '连接错误', icon: 2 });
				}
				layer.closeAll('loading')
		    }
		});
		
		template.defaults.imports.dateFormat = function (value, format) {
		    if (value == '') {
		        return '';
		    }
		    if (format == '') {
		        format = 'yyyy-MM-dd hh:mm:ss';
		    }
		    var date = new Date(value);
		    return date.Format(format);
		};
		template.defaults.imports.Icon = function (value) {
		    if (value.endWith('.html')) {
		        if (value == 'index.html') {
		            return 'glyphicon glyphicon-home';
		        }
		        else {
		            return 'glyphicon glyphicon-globe';
		        }
		    }
		    else if (value.endWith('.jpg') || value.endWith('.gif') || value.endWith('.png') || value.endWith('.ico')) {
		        return 'glyphicon glyphicon-picture';
		    }
		    else {
		        return 'glyphicon glyphicon-file';
		    }
		};
		template.defaults.imports.encodeURIComponent = function (a) {
		    return encodeURIComponent(a);
		};
		win.$ = $;
		admin.loadView = function(main,left) {
		    if (left) {
		        if (!$('#container .sidebar').length) {
		            $('#container').html(tpl);
		        }
		        $('#container .main').html(main);
		        $('#container .sidebar .nav li').removeClass('active');
		        var r = window.location.hash.split('?')[0];
		        $('#container .sidebar a[href="' + r + '"]').parent().addClass('active');
		    }
		    else {
		        $('#container').html(main);
		    }
		};
        router.init();                      //开始监控url变化
        var cfg = JSON.parse(localStorage.getItem('config'));
        if (cfg) {
			admin.BucketName = cfg.id;
        }
        if (!location.hash) { //打开默认页
            if (cfg) {
                location.hash = '/article/list';
            }
            else {
                location.hash = '/bucket/list';       
            }
        }
	});

})(window);

