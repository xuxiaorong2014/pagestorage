# -*- coding: utf-8 -*-
import os
import sys
APP_ROOT = os.path.dirname(os.path.abspath("__file__"))

if not APP_ROOT in sys.path: #如果允许在 python embeddable 环境
    sys.path.append(APP_ROOT)
    sys.path.append(os.path.abspath(os.path.join(__file__, '../packages.zip')))
print (sys.path)

from app import app
@app.route('/', methods=['GET'])
def _get_index():
    return app.send_static_file('index.html')
@app.route('/favicon.ico', methods=['GET'])
def _get_favicon():
    return app.send_static_file('favicon.ico')


if __name__ == '__main__':
    app.run(debug=True)
 