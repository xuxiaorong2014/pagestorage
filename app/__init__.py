# -*- coding: utf-8 -*-
import os
import sys
APP_ROOT = os.path.dirname(os.path.abspath("__file__"))
from flask import Flask
app = Flask(__name__,static_url_path='/assets',static_folder='assets')
app.config['JSON_AS_ASCII'] = False
from app.controllers import buckets
from app.controllers import objects
from app.controllers import posts
from app.controllers import templates