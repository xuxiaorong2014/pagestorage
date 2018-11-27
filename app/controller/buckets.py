#encoding: utf-8
import os
import json
from flask import request,jsonify
from app import APP_ROOT, app , get_client 

@app.route("/api/buckets", methods=['GET'])
def get_buckets():
    if not os.path.exists(os.path.join(APP_ROOT, 'sites')):
        os.makedirs(os.path.join(APP_ROOT, 'sites'))
        with open(os.path.join(APP_ROOT, 'sites','buckets.json'),'w',encoding='utf-8') as fp:
            fp.write("[]")
        return "[]", {'Content-Type': 'application/json'}
    with open(os.path.join(APP_ROOT, 'sites','buckets.json'),'r',encoding='utf-8') as f:
        s=f.read()
        return str(s) , {'Content-Type': 'application/json'}
@app.route("/api/buckets/<string:id>", methods=['GET'])
def get_bucket(id):
    with open(os.path.join(APP_ROOT,'sites','buckets.json'),'r',encoding='utf-8') as f:
        buckets = json.load(f)
    for bucket in buckets:
        if id == bucket["id"]:
            return jsonify(bucket)
    return "Bucket not found", 404
@app.route("/api/buckets", methods=['POST'])
def post_bucket():
    model = {}
    model['id'] = request.form['[0].value']
    model['type'] = request.form['[1].value']
    model['sitename'] = request.form['[2].value']
    model['url'] = request.form['[3].value']
    model['bucket'] = request.form['[4].value']
    model['APPID'] = request.form['[5].value']
    model['SecretId'] = request.form['[6].value']
    model['SecretKey'] = request.form['[7].value']
    model['Region'] = request.form['[8].value']
    with open(os.path.join(APP_ROOT,'sites', 'buckets.json'),'r+',encoding='utf-8') as f:
        buckets = json.load(f)
        for item in buckets:
            if model['id'] == item["id"]:
                return "bucketid已存在", 404
        buckets.append(model)
        f.seek(0)
        f.truncate()
        json.dump(buckets,f,ensure_ascii=False)
    if(not os.path.exists("./sites/" + model['id'])):
        os.makedirs("./sites/" + model['id'] + "/data/posts")
        os.mkdir("./sites/" + model['id'] + "/theme/include")
    return jsonify(model)  
@app.route("/api/buckets/<string:id>", methods=['PUT'])
def put_bucket(id):
    with open(os.path.join(APP_ROOT,'sites', 'buckets.json'),'r+',encoding='utf-8') as f:
        buckets = json.load(f)
    for bucket in buckets:
        if id == bucket["id"]:
            i = buckets.index(bucket)
            buckets[i]['type']=request.form['[1].value']
            buckets[i]['sitename']=request.form['[2].value']
            buckets[i]['url']=request.form['[3].value']
            buckets[i]['bucket']=request.form['[4].value']
            buckets[i]['APPID']=request.form['[5].value']
            buckets[i]['SecretId']=request.form['[6].value']
            buckets[i]['SecretKey']=request.form['[7].value']
            buckets[i]['Region']=request.form['[8].value']
            f.seek(0)
            f.truncate()
            json.dump(buckets,f,ensure_ascii=False)
            return jsonify(bucket)
    return "Bucket not found", 404
@app.route("/api/buckets/<string:id>", methods=['DELETE'])
def delete_bucket(id):
    with open(os.path.join(APP_ROOT,'sites', 'buckets.json'),'r',encoding='utf-8') as f:
        buckets = json.load(f)
    for bucket in buckets:
        if id == bucket["id"]:
            i = buckets.index(bucket)
            del buckets[i]
            return '{"code":0}',{'Content-Type': 'application/json'},200
    return "Bucket not found", 404