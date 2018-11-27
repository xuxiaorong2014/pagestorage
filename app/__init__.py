#encoding: utf-8
import os
from flask import Flask

APP_ROOT = os.path.dirname(os.path.abspath("__file__"))
app = Flask(__name__,static_url_path='/assets',static_folder='assets')
app.config['JSON_AS_ASCII'] = False

from .ctypeof import content_type_of

from .clients import get_client
from .controller.buckets import * 
from .controller.posts import *
from .controller.templates import *
from .controller.objects import *

@app.route('/', methods=['GET'])
def _get_index():
    return app.send_static_file('index.html')
@app.route('/favicon.ico', methods=['GET'])
def _get_favicon():
    return app.send_static_file('favicon.ico')
if __name__ == "__main__":
    pass