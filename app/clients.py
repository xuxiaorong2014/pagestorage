#encoding: utf-8
import json
import os

from app import APP_ROOT
from .cos_client import CosClient
from .oss_client import OssClient
from .gcs_client import GcsClient

def get_client(bucketname):
    with open(os.path.join(APP_ROOT, 'sites','buckets.json'),'r',encoding='utf-8') as f:
        buckets = json.load(f)
    for bucket in buckets:
            if bucketname == bucket["id"]:
                if bucket['type']=='cos':
                    return CosClient(Region=bucket['Region'], SecretId=bucket['SecretId'], SecretKey=bucket['SecretKey'])
                elif bucket['type']=='oss':
                    return OssClient(Region=bucket['Region'], AccessKeyId=bucket['SecretId'], AccessKeySecret=bucket['SecretKey'])
                elif bucket['type']=='gcs':
                    return GcsClient(AccessKeyId=bucket['SecretId'], AccessKeySecret=bucket['SecretKey'])
    raise Exception('bad')

if __name__ == "__main__":
    pass