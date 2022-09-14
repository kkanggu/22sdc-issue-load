
import json
import boto3
import requests
s3 = boto3.client('s3', region_name='ap-northeast-2')
bucket_name = "issue-keyword-storage"
#latest file 10
file_list = (s3.list_objects(Bucket=bucket_name, Prefix='json/')['Contents'])[-10:-1]
s3_objects = [s3.get_object(Bucket=bucket_name, Key=content['Key']) for content in file_list]
json_objects = [json.loads(obj_dict['Body'].read().decode()) for obj_dict in s3_objects]
title_contents = [article['title'] + " " + article['content'] for j_obj in json_objects for article in j_obj]
model_json = {'articles': title_contents}
with open("test2.json", "w") as json_file:
    json.dump(model_json, json_file, indent=4)