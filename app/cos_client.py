#encoding: utf-8
import requests
import hmac
import hashlib
import time
from base64 import b64encode
from email.utils import formatdate
from urllib import parse
import xml.etree.ElementTree
from six.moves.urllib.parse import quote, unquote, urlparse, urlencode
from six import text_type, binary_type, string_types
from .xml2dict import Xml2Dict
from .streambody import StreamBody

def xml_to_dict(data, origin_str="", replace_str=""):
    root = xml.etree.ElementTree.fromstring(data)
    xmldict = Xml2Dict(root)
    xmlstr = str(xmldict)
    xmlstr = xmlstr.replace("{http://www.qcloud.com/document/product/436/7751}", "")
    xmlstr = xmlstr.replace("{https://cloud.tencent.com/document/product/436}", "")
    xmlstr = xmlstr.replace("{http://doc.s3.amazonaws.com/2006-03-01}", "")
    xmlstr = xmlstr.replace("{http://s3.amazonaws.com/doc/2006-03-01/}", "")
    xmlstr = xmlstr.replace("{http://www.w3.org/2001/XMLSchema-instance}", "")
    if origin_str:
        xmlstr = xmlstr.replace(origin_str, replace_str)
    xmldict = eval(xmlstr)
    return xmldict

class CosClient(object):
    def __init__(self,  SecretId=None, SecretKey=None,Region=None):
        self._secret_id = SecretId
        self._secret_key = SecretKey
        self._region = Region

    def send_request(self, method, url, bucket, **kwargs):  
        if(not kwargs.get('headers')):
            kwargs['headers']={}
        kwargs['headers']['Date'] = formatdate(None, usegmt=True)
        kwargs['headers']['Host'] = "{0}.cos.{1}.myqcloud.com".format(bucket,self._region)
        headers={}
        for k in sorted(kwargs['headers'].keys()):
            if k == 'Content-Type' or k == 'Host' or k[0] == 'x' or k[0] == 'X':
                headers[k] = kwargs['headers'][k]
        headers = dict([(k.lower(), quote(self.to_bytes(v), '-_.~')) for k, v in headers.items()])  # headers中的key转换为小写，value进行encode
        uri_params = dict(parse.parse_qsl(parse.urlparse(url).query))
        uri_params = dict([(k.lower(), v) for k, v in uri_params.items()])

        start_sign_time = int(time.time())
        sign_time = "{bg_time};{ed_time}".format(bg_time=start_sign_time-60, ed_time=start_sign_time+10000)
        format_str = u"{method}\n{host}\n{params}\n{headers}\n".format(
            method=method.lower(),
            host=parse.urlparse(url).path,
            params=urlencode(sorted(uri_params.items())).replace('+', '%20').replace('%7E', '~'),
            headers='&'.join(map(lambda tupl: "%s=%s" % (tupl[0], tupl[1]), sorted(headers.items())))
        )
        sha1 = hashlib.sha1()
        sha1.update(self.to_bytes(format_str))
        string_to_sign = "sha1\n{time}\n{sha1}\n".format(time=sign_time, sha1=sha1.hexdigest())
        sign_key = hmac.new(self.to_bytes(self._secret_key), self.to_bytes(sign_time), hashlib.sha1).hexdigest()
        sign = hmac.new(self.to_bytes(sign_key), self.to_bytes(string_to_sign), hashlib.sha1).hexdigest()
        sign_tpl = "q-sign-algorithm=sha1&q-ak={ak}&q-sign-time={sign_time}&q-key-time={key_time}&q-header-list={headers}&q-url-param-list={params}&q-signature={sign}"
        kwargs['headers']['Authorization'] = sign_tpl.format(
            ak=self._secret_id,
            sign_time=sign_time,
            key_time=sign_time,
            params=';'.join(sorted(map(lambda k: k.lower(), uri_params.keys()))),
            headers=';'.join(sorted(headers.keys())),
            sign=sign
        )

        try:
            if method == 'POST':
                res = requests.post(url, **kwargs)
            elif method == 'GET':
                res = requests.get(url, **kwargs)
            elif method == 'PUT':
                res = requests.put(url, **kwargs)
            elif method == 'DELETE':
                #kwargs["headers"]["Content-Length"]=0
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
        _url = "https://{0}.cos.{1}.myqcloud.com/".format(Bucket,self._region)
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
        _url = "https://{0}.cos.{1}.myqcloud.com{2}".format(Bucket,self._region,Key)
        rt = self.send_request(method="GET" ,url=_url, bucket=Bucket,stream=True)
        response = rt.headers
        response['Body'] = StreamBody(rt)
        return response
    def put_object(self, Bucket, Body, Key, **kwargs):
        if Key[0] != '/':
            Key = '/' + Key
        _url = "https://{0}.cos.{1}.myqcloud.com{2}".format(Bucket,self._region,Key)
        rt = self.send_request(method="PUT" ,url=_url,bucket=Bucket, data=Body)
        return rt.headers

    def delete_object(self, Bucket, Key, **kwargs):
        if Key[0] != '/':
            Key = '/' + Key
        _url = "https://{0}.cos.{1}.myqcloud.com{2}".format(Bucket,self._region,Key)
        rt = self.send_request(method="DELETE" ,url=_url,bucket=Bucket)
        return rt.headers

    def to_bytes(self,s):
        """将字符串转为bytes"""
        if isinstance(s, text_type):
            return s.encode('utf-8')
        return s

if __name__ == "__main__":
    pass