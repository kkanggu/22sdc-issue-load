import datetime
import boto3

#convert file date to utc
def upload_json(file_name):
    s3 = boto3.client('s3', region_name='ap-northeast-2')
    bucket_name = "issue-keyword-storage"
    now = datetime.datetime.now()
    key = "json/" + datetime.datetime.strftime(now, "%Y-%m-%d %H:%M") + ".json"
    s3.upload_file(file_name, bucket_name, key)
