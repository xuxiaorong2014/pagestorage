#encoding: utf-8
import os
import json
import time
import uuid
import jinja2
from flask import request,jsonify,abort,render_template
from app import app
from app.clients.get_client import get_client

@app.route('/api/posts', methods=['GET'])
def get_posts():
    if 'BucketName' in request.headers:
        BucketName = request.headers.get('BucketName')
    client = get_client(BucketName)
    response=client.get_object(Bucket=BucketName,Key='/data/posts.json')
    json_str = response['Body'].get_raw_stream().read().decode('utf-8')
    if json_str.startswith(u'\ufeff'):
        json_str = json_str.encode('utf8')[3:].decode('utf8')
    if not os.path.exists("./sites/" + BucketName + "/data/posts"):
        os.makedirs("./sites/" + BucketName + "/data/posts")
    with open("./sites/" + BucketName + "/data/posts.json",'w',encoding='utf-8') as f:
        f.write(json_str)
    return json_str,{'Content-Type': 'application/json'}

@app.route('/api/posts/<string:id>', methods=['GET'])
def get_post(id):
    if 'BucketName' in request.headers:
        BucketName = request.headers.get('BucketName')
    client = get_client(BucketName)
    key = "/data/posts/" + id + ".json"
    response=client.get_object(Bucket=BucketName,Key=key)
    article = response['Body'].get_raw_stream().read().decode('utf-8')
    return article ,{'Content-Type': 'application/json'}

@app.route('/api/posts', methods=['POST'])
def post_post():
    if 'BucketName' in request.headers:
        BucketName = request.headers.get('BucketName')
    client = get_client(BucketName)
    id = str(uuid.uuid1()).replace("-","")
    key = "/data/posts/" + id + ".json"
    headers = {"Content-Type":"application/json"}
    with open("./sites/" + BucketName + "/data/posts.json",'r+',encoding='utf-8') as f:
        posts = json.load(f)
        model = {}
        model["Id"] = id
        model["Name"] = request.form.get('Name',type=str, default=None)
        model["Title"] = request.form.get('Title',type=str, default=None)
        model["Order"] = len(posts) + 1
        model["Catalog"] = request.form.get('Catalog',type=str, default="/")
        model["Template"] = request.form.get('Template',type=str, default=None)
        model["CreationTime"] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        model["LastWriteTime"] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
        for p in posts:
            if p["Name"] == model["Name"] and p["Catalog"] == model["Catalog"]:
                abort(400)
        posts.append(model)
        posts.sort(key=lambda item: item["Order"])
        articles = json.dumps(posts, ensure_ascii=False)
        f.seek(0)
        f.truncate()
        f.write(articles)
    #上传列表 
    client.put_object(Bucket = BucketName,Body=articles.encode('utf-8'),Key="/data/posts.json",headers=headers) 
    #保存文章
    model["Content"] = request.form.get('Content',type=str, default=None)
    model["Metas"] = {}
    i = 0
    while "Metas[{}].key".format(i) in request.form :
        meta_key = request.form.get("Metas[{}].key".format(i))
        model["Metas"][meta_key] = request.form.get("Metas[{}].value".format(i))            
        i=i + 1
    article = json.dumps(model,ensure_ascii=False)
    with open("./sites/" + BucketName + key,'w',encoding='utf-8') as pf:
        pf.write(article)
    client.put_object(Bucket = BucketName,Body=article.encode('utf-8'),Key=key,headers=headers) 
    return article ,{'Content-Type': 'application/json'}

@app.route('/api/posts/<string:id>', methods=['PUT'])
def put_post(id):
    if 'BucketName' in request.headers:
        BucketName = request.headers.get('BucketName')
    client = get_client(BucketName)
    key = "/data/posts/" + id + ".json"
    with open("./sites/" + BucketName + "/data/posts.json",'r+',encoding='utf-8') as f:
        posts = json.load(f)
        for model in posts:
            if model["Id"] == id:
                model["Name"] = request.form.get('Name',type=str, default=None)
                model["Title"] = request.form.get('Title',type=str, default=None)
                model["Order"] = request.form.get('Order',type=int, default=0)
                model["Catalog"] = request.form.get('Catalog',type=str, default="/")
                model["Template"] = request.form.get('Template',type=str, default=None)
                model["CreationTime"] = request.form.get('CreationTime',type=str, default=None)
                model["LastWriteTime"] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
                posts.sort(key=lambda item: item["Order"])
                articles = json.dumps(posts,ensure_ascii=False)
                #保存列表
                f.seek(0)
                f.truncate()
                f.write(articles)
                f.seek(0)
                headers = {"Content-Type":"application/json"}
                client.put_object(Bucket = BucketName,Body=articles.encode('utf-8'),Key="/data/posts.json",headers=headers) 
                #保存文章
                model["Content"] = request.form.get('Content',type=str, default=None)
                model["Metas"] = {}
                i = 0
                while "Metas[{}].key".format(i) in request.form :
                    meta_key = request.form.get("Metas[{}].key".format(i))
                    model["Metas"][meta_key] = request.form.get("Metas[{}].value".format(i))            
                    i=i + 1
                article = json.dumps(model,ensure_ascii=False)
                with open("./sites/" + BucketName + key,'w',encoding='utf-8') as pf:
                    pf.write(article)
                client.put_object(Bucket = BucketName,Body=article.encode('utf-8'),Key=key,headers=headers) 
                return article ,{'Content-Type': 'application/json'}
        return "bad request",404

@app.route('/api/posts/<string:id>', methods=['DELETE'])
def delete_post(id):
    if 'BucketName' in request.headers:
        BucketName = request.headers.get('BucketName')
    client = get_client(BucketName)
    key = "/data/posts/" + id + ".json"
    with open("./sites/" + BucketName + "/data/posts.json",'r+',encoding='utf-8') as f:
        posts = json.load(f)
        for model in posts:
            if model["Id"] == id:
                i = posts.index(model)
                del posts[i]
                f.seek(0)
                f.truncate()
                posts.sort(key=lambda item: item["Order"])
                json_str = json.dumps(posts)
                f.write(json_str)
                #json.dump(posts,f, ensure_ascii=False)
                #上传列表
                headers = {"Content-Type":"application/json"}
                
                client.put_object(Bucket = BucketName,Body=json_str.encode("utf-8"),Key="/data/posts.json",headers=headers) 
                #删除远程文章
                client.delete_object(Bucket = BucketName,Key=key) 
                #删除本地文章
                os.remove("./sites/" + BucketName + key)
                return '{"code":0}' , {'Content-Type': 'application/json'}
        return "not found",404

@app.route('/api/publish/<string:id>',methods=['POST'])
def post_publish(id):
    if 'BucketName' in request.headers:
        BucketName = request.headers.get('BucketName')
    client = get_client(BucketName)        
    key = "/data/posts/" + id + ".json"
    template_folder = os.path.dirname(os.path.abspath("./sites/" + BucketName + "/theme/" ))
    with open("./sites/" + BucketName + "/data/posts.json",'r',encoding='utf-8') as f:
        posts = json.load(f)
    response = client.get_object(Bucket=BucketName,Key=key)
    article = response['Body'].get_raw_stream().read().decode('utf-8')
    model = json.loads(article, encoding="utf-8")
    t = model.get("Template")
    if(not t):
        abort('文章未指定模板')
    if(not os.path.exists(os.path.join(template_folder,t))):
        abort('模板不存在')
    model["Posts"] = posts
    #渲染模板
    env = jinja2.Environment(loader=jinja2.PackageLoader('app',template_folder))
    template = env.get_template(t)
    html_string = template.render(**model)
    key = model.get("Catalog", "/") + model.get("Name") + ".html"
    headers = {"Content-Type":"text/html"}
    client.put_object(Bucket=BucketName, Body=html_string.encode('utf-8'),Key=key,headers = headers)
    return '{"code":0}' , {'Content-Type': 'application/json'}