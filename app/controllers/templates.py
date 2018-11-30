#encoding: utf-8
import os
import json
from app import app
from flask import Blueprint,request,jsonify,abort
from app.clients.get_client import get_client
from app.clients.ctypeof import content_type_of

@app.route('/api/templates', methods=['GET'])
def get_templates():
    if 'BucketName' in request.headers:
        BucketName = request.headers.get('BucketName')
    else:
        abort(500)
    themes = []
    i = len(BucketName) + 15
    for root,dirs,files in os.walk("./sites/" + BucketName + "/theme"):
        for name in files:
            themes.append((root.replace("\\","/") + "/" + name)[i:])
    return jsonify(themes)
@app.route('/api/templates/download', methods=['GET'])
def download_template():
    if 'BucketName' in request.headers:
        BucketName = request.headers.get('BucketName')
    else:
        abort(500)
    client = get_client(BucketName)
    name=request.args.get("name")
    if name[0] != "/":
        name = "/" + name
    response = client.get_object(Bucket=BucketName,Key=name)
    if not os.path.exists(os.path.dirname("./sites/" + BucketName + name)):
        os.makedirs(os.path.dirname("./sites/" + BucketName + name))
    response['Body'].get_stream_to_file("./sites/" + BucketName + name)
    return '{"code":0}' , {'Content-Type': 'application/json'}

@app.route('/api/templates', methods=['POST'])
def post_template():
    if 'BucketName' in request.headers:
        BucketName = request.headers.get('BucketName')
    else:
        abort(500)
    client = get_client(BucketName)
    i = len(BucketName) + 8
    for root,dirs,files in os.walk("./sites/" + BucketName + "/theme"):
        for name in files:
            path = (root.replace("\\","/") + "/" + name)
            key = path[i:]
            with open(path, 'rb') as fp:
                headers = {"Content-Type": content_type_of(key)}
                client.put_object(
                    Bucket=BucketName,
                    Body=fp,
                    Key=key,
                    headers = headers
                )
    return '{"code":0}' , {'Content-Type': 'application/json'}

@app.route('/api/templates', methods=['PUT'])
def put_template():
    if 'BucketName' in request.headers:
        BucketName = request.headers.get('BucketName')
    else:
        abort(500)
    client = get_client(BucketName)
    _key = "/theme/" + request.args.get("name")
    _body = request.form['']
    headers = {"Content-Type": content_type_of(_key)}
    client.put_object(Bucket = BucketName,Body=_body.encode('utf-8'),Key=_key, headers = headers)
    with open("./sites/" + BucketName + _key ,'w',encoding='utf-8') as f:
        f.write(_body)
    return '{"code":0}' , {'Content-Type': 'application/json'}

@app.route('/api/templates', methods=['DELETE'])
def del_template():
    if 'BucketName' in request.headers:
        BucketName = request.headers.get('BucketName')
    else:
        abort(500)
    client = get_client(BucketName)
    key = "/theme/" + request.args.get("name")
    client.delete_object(Bucket=BucketName,Key=key)
    os.remove("./sites/" + BucketName + key)
    return '{"code":0}' , {'Content-Type': 'application/json'}