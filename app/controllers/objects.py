#encoding: utf-8
import os
import json
from flask import request,jsonify,abort
from werkzeug.utils import secure_filename
 
from app import app
from app.clients.get_client import get_client
from app.clients.ctypeof import content_type_of

@app.route('/api/objects', methods=['GET'])
def get_objects():
    if 'BucketName' in request.headers:
        BucketName = request.headers.get('BucketName')
        client = get_client(BucketName)
    else:
        abort(500)
    Key=request.args.get("key")
    if(Key):
        if(Key[0] != '/'):
            Key = '/' + Key
        response=client.get_object(Bucket=BucketName,Key=Key)
        return response['Body'].get_raw_stream().read().decode('utf-8'),{'Content-Type': 'text/html'}
    delimiter=request.args.get("delimiter")
    prefix=request.args.get("prefix")
    response=client.list_objects(Bucket=BucketName, Prefix=prefix, Delimiter=delimiter)
    return jsonify(response)

@app.route('/api/objects', methods=['POST'])
def post_objects():
    if 'BucketName' in request.headers:
        BucketName = request.headers.get('BucketName')
        client = get_client(BucketName)
    else:
        abort(500)
    prefix=request.args.get("prefix")
    if(prefix):
        if(prefix[0] != '/'):
            prefix = '/' + prefix
        if(prefix[0] != '/'):
            prefix = prefix + '/'
    uploaded_files = request.files.getlist('file')
    result = []
    for file in uploaded_files:
        if file:
            filename = secure_filename(file.filename)
            client.put_object(
                Bucket=BucketName, 
                Body=file.stream,  
                Key=prefix + filename, 
                headers = {"Content-Type" : file.content_type})
            result.append(prefix + filename)
    return jsonify(result) 

@app.route('/api/objects', methods=['PUT'])
def put_object():
    if 'BucketName' in request.headers:
        BucketName = request.headers.get('BucketName')
        client = get_client(BucketName)
    else:
        abort(500)
    Key=request.args.get("key")
    content=request.form['']
    if(not content):
        abort(500)
    headers = {"Content-Type": content_type_of(Key)}
    client.put_object(Bucket=BucketName ,Body=content.encode('utf-8'),Key=Key,headers=headers)
    return '{"code":0}',{'Content-Type': 'application/json'}
    
@app.route('/api/objects', methods=['DELETE'])
def delete_object():
    if 'BucketName' in request.headers:
        BucketName = request.headers.get('BucketName')
        client = get_client(BucketName)
    else:
        abort(500)
    Key=request.args.get("key")
    client.delete_object(Bucket=BucketName,Key=Key)
    return '{"code":0}' ,{'Content-Type': 'application/json'}