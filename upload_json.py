import boto3
import os
import datetime
import my_logger

def get_last_modified_date(bucket):
    # last_update_date = bucket['Contents'][-1]['LastModified'] + AWS_TIMEGAP
    last_update_date = bucket['Contents'][-1]['LastModified']
    # last_update_date = last_update_date.replace(tzinfo=datetime.timezone.utc)
    return last_update_date


def get_last_file_date(file_name):
    file_date =  datetime.datetime.strptime(file_name.split('.')[0], "%Y-%m-%d %H:%M")
    file_date = file_date.replace(tzinfo=datetime.timezone.utc)
    return file_date


#convert file date to utc
if __name__ == '__main__':
    JSON_PATH = "json/"
    logger = my_logger.create_logger()
    #AWS is utc, local file is in seoul time zone
    # AWS_TIMEGAP = datetime.timedelta(hours=9)
    try:
        s3 = boto3.client('s3', region_name='ap-northeast-2')
        bucket_name = "issue-keyword-storage"
        bucket = s3.list_objects_v2(Bucket=bucket_name, Prefix= JSON_PATH, Delimiter='/')
    
    except Exception as e:
        logger.error(e)

    json_files = os.listdir(JSON_PATH)
    file_name = json_files[-1]
    
    last_update_date = get_last_modified_date(bucket)
    file_date = get_last_file_date(file_name)

    if last_update_date < file_date:
        file_path = f"{JSON_PATH}/{file_name}"
        key = "json/" + file_name
        s3.upload_file(file_path, bucket_name, key)
    
    else:
        print("No need to update")