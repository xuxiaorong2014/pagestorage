#encoding: utf-8
import requests
import hmac
import hashlib

from base64 import b64encode
from email.utils import formatdate
from urllib import parse
import xml.etree.ElementTree

from app.clients.xml2dict import Xml2Dict
from app.clients.streambody import StreamBody

def xml_to_dict(data, origin_str="", replace_str=""):
    root = xml.etree.ElementTree.fromstring(data)
    xmldict = Xml2Dict(root)
    xmlstr = str(xmldict)
    xmlstr = xmlstr.replace("{http://doc.s3.amazonaws.com/2006-03-01}", "")
    xmlstr = xmlstr.replace("{http://s3.amazonaws.com/doc/2006-03-01/}", "")
    xmlstr = xmlstr.replace("{http://www.w3.org/2001/XMLSchema-instance}", "")
    if origin_str:
        xmlstr = xmlstr.replace(origin_str, replace_str)
    xmldict = eval(xmlstr)
    return xmldict


class OssClient(object):
    def __init__(self,  AccessKeyId=None, AccessKeySecret=None,Region=None):
        self._access_key_id = AccessKeyId
        self._access_key_secret = AccessKeySecret
        self._region = Region

    def send_request(self, method, url, bucket, **kwargs):  
        if(not kwargs.get('headers')):
            kwargs['headers']={}
        string_to_sign = method.upper() + "\n" #VERB
        string_to_sign = string_to_sign + "\n"  #Content-MD5
        string_to_sign = string_to_sign + kwargs['headers'].get('Content-Type','') + "\n"   #Content-Type
        string_to_sign = string_to_sign + formatdate(None, usegmt=True) + "\n" #Date

        for k in sorted(kwargs['headers'].keys()):
            if k[:6] == "x-oss-":
                string_to_sign = string_to_sign + k.lower() + ":" + kwargs['headers'][k] + "\n"  

        string_to_sign = string_to_sign + "/" + bucket +  parse.urlparse(url).path
        signatured_string = self.hmac_sha1_base64_sign(self._access_key_secret,string_to_sign)
        kwargs['headers']['Authorization'] = "AWS {0}:{1}".format(self._access_key_id, signatured_string)
        kwargs['headers']['Date'] = formatdate(None, usegmt=True)
        kwargs['headers']['Host'] = "{0}.oss-{1}.aliyuncs.com".format(bucket,self._region)
        try:
            if method == 'POST':
                res = requests.post(url, **kwargs)
            elif method == 'GET':
                res = requests.get(url, **kwargs)
            elif method == 'PUT':
                res = requests.put(url, **kwargs)
            elif method == 'DELETE':
                res = requests.delete(url, **kwargs)
            if res.status_code < 400:  # 2xx和3xx都认为是成功的
                return res
        except Exception as e:
            raise Exception(str(e))

        if res.status_code >= 400:  # 所有的4XX,5XX都认为是 
            if method == 'HEAD' and res.status_code == 404:   # Head 需要处理
                info = dict()
                info['code'] = 'NoSuchResource'
                info['message'] = 'The Resource You Head Not Exist'
                info['resource'] = url
                raise Exception( 'The Resource You Head Not Exist' )
            else:
                msg = res.text
                if msg == u'':  # 服务器没有返回Error Body时 给出头部的信息
                    msg = res.headers
                raise Exception( msg)
        return None
    
    def list_objects(self, Bucket, Prefix="", Delimiter="", Marker="", MaxKeys=1000, EncodingType="", **kwargs):
        _url = "https://{0}.oss-{1}.aliyuncs.com/".format(Bucket,self._region)
        params = {
            'prefix': Prefix,
            'delimiter': Delimiter,
            'marker': Marker,
            'max-keys': MaxKeys
            }
        rt = self.send_request(method="GET", url=_url, bucket=Bucket, params=params)
        data = xml_to_dict(rt.content)
        return data
    
    def get_object(self, Bucket, Key, **kwargs):
        if Key[0] != '/':
            Key = '/' + Key
        _url = "https://{0}.oss-{1}.aliyuncs.com{2}".format(Bucket,self._region,Key)
        rt = self.send_request(method="GET" ,url=_url, bucket=Bucket,stream=True)
        response = rt.headers
        response['Body'] = StreamBody(rt)
        return response
    def put_object(self, Bucket, Body, Key, **kwargs):
        if Key[0] != '/':
            Key = '/' + Key
        _url = "https://{0}.oss-{1}.aliyuncs.com{2}".format(Bucket,self._region,Key)
        rt = self.send_request(method="PUT" ,url=_url,bucket=Bucket, data=Body,**kwargs)
        return rt.headers

    def delete_object(self, Bucket, Key, **kwargs):
        if Key[0] != '/':
            Key = '/' + Key
        _url = "https://{0}.oss-{1}.aliyuncs.com{2}".format(Bucket,self._region,Key)
        rt = self.send_request(method="DELETE" ,url=_url,bucket=Bucket)
        return rt.headers

    def hmac_sha1_base64_sign(self,encrypt_key,encrypt_text):
        h = hmac.new(encrypt_key.encode("utf-8"), encrypt_text.encode("utf-8"), hashlib.sha1)
        d = h.digest()
        b = b64encode(d)
        return b.decode('utf-8')

if __name__ == "__main__":
    pass